from PySide6.QtCore import QObject, Slot, QThread, QTimer
import logging
import math
from collections import deque

# Importaciones relativas correctas
from .ConexionBD import DatabaseWorker
from Interfaz.WidgetGrafica import GraficaWidget 

# --- Configuración ---
MAX_MUESTRAS = 1000 
SENSORES_POR_PAGINA = 3

class AppLogica(QObject):
    """
    manejar el estado de la aplicación.
    """
    
    def __init__(self, ui: 'SensorMonitorUI'):
        super().__init__()
        self.ui = ui
        self.seccion_actual = "distancias" # Default
        self.pagina_actual = 0
        
        #  Modelo de Datos 
        self.datos_sensores = {} 
        self.ultimos_valores_validos = {}
        
        #  Widgets 
        self.widgets_graficas = {} # {mac: GraficaWidget}
        self.lista_macs_ordenada = []
        
        self.db_thread = None
        self.db_worker = None
        self.update_timer = None 
        
        self.connection_string = (
            r"Driver={SQL Server Native Client 11.0};"
            r"Server=DESKTOP-J4U2VS9\sqlexpress;"
            r"Database=Sensores;"
            r"Trusted_Connection=yes;"
        )

    def set_update_timer(self, timer: QTimer):
        """Recibe el QTimer desde main.py"""
        self.update_timer = timer
        # primero el worker debe existir

    def iniciar(self):
        """configurando el hilo de la BD"""
        logging.info("AppLogica iniciada.")
        self.setup_threading()

    def setup_threading(self):
        """Configura e inicia el QThread y el DatabaseWorker."""
        logging.info("Configurando hilo de base de datos...")
        self.db_thread = QThread()
        self.db_worker = DatabaseWorker(self.connection_string)
        self.db_worker.moveToThread(self.db_thread)
        # Conectar señales del worker a nuestros slots
        self.db_thread.started.connect(self.db_worker.load_initial_data)
        self.db_worker.new_data_row.connect(self.procesar_fila_datos)
        self.db_worker.initial_load_finished.connect(self.on_initial_load_finished)
        self.db_worker.status_update.connect(self.ui.statusbar.showMessage)
        # Conectar el timer al worker 
        if self.update_timer:
            self.update_timer.timeout.connect(self.db_worker.check_for_updates)

        logging.info("Iniciando hilo de base de datos...")
        self.db_thread.start()

    # --- Procesamiento de Datos (Recibido del Worker) ---
    @Slot(list)
    def procesar_fila_datos(self, row):
        """
        Slot que recibe cada fila de datos del DatabaseWorker.
        """
        try:
            mac = row[0]
            
            #  Lógica de Creación Dinámica 
            if mac not in self.datos_sensores:
                self.inicializar_estructura_datos(mac)
                
                # ¡Nuevo sensor! Lo añadimos a la lista
                if mac not in self.widgets_graficas:
                    self.lista_macs_ordenada.append(mac)
                    self.lista_macs_ordenada.sort() # Mantener ordenado
                    
                    # Le pedimos a la UI que cree el widget real
                    widget = self.ui.crear_grafica_real(mac)
                    self.widgets_graficas[mac] = widget
                    widget.hide() # Ocultarlo hasta que esté en la página correcta
            
            # Extraer y validar datos (índices de tu tabla)
            d1_raw = float(row[3]) if row[3] is not None else 0.0
            d2_raw = float(row[4]) if row[4] is not None else 0.0
            d3_raw = float(row[5]) if row[5] is not None else 0.0
            temp = float(row[6]) if row[6] is not None else 0.0
            hum = float(row[7]) if row[7] is not None else 0.0
            q1,q2,q3,q4 = [float(row[i]) if row[i] is not None else 0.0 for i in range(8, 12)]
            identificador = int(row[12]) # Eje X
            
            # Corregir valores 0
            d1 = self.validate_values(mac, d1_raw, 'D1')
            d2 = self.validate_values(mac, d2_raw, 'D2')
            d3 = self.validate_values(mac, d3_raw, 'D3')

            # --- Lógica de Deque (Cola) ---
            self.datos_sensores[mac]['D1'].append(d1)
            self.datos_sensores[mac]['D2'].append(d2)
            self.datos_sensores[mac]['D3'].append(d3)
            self.datos_sensores[mac]['temperatura'].append(temp)
            self.datos_sensores[mac]['humedad'].append(hum)
            self.datos_sensores[mac]['quaterniones'].append((q1, q2, q3, q4))
            self.datos_sensores[mac]['muestras'].append(identificador)
            
            # --- Actualización en Vivo ---
            # Si el timer está activo, actualizamos la gráfica visible
            if self.update_timer and self.update_timer.isActive():
                if mac in self.widgets_graficas and self.widgets_graficas[mac].isVisible():
                    datos_sensor = self.datos_sensores[mac]
                    self.widgets_graficas[mac].actualizar_grafica(datos_sensor, self.seccion_actual)

        except Exception as e:
            logging.error(f"Error procesando fila {row}: {e}")

    @Slot(int)
    def on_initial_load_finished(self, sensor_count):
        """Llamado cuando el worker termina la carga inicial."""
        logging.info(f"Carga inicial de BD completada. {sensor_count} sensores encontrados.")
        
        # Ordenar la lista de MACs
        self.lista_macs_ordenada = sorted(list(self.datos_sensores.keys()))
                
        # Mostrar la primera página
        self.actualizar_display_graficas()
        self.ui.statusbar.showMessage(f"Mostrando {len(self.widgets_graficas)} sensores. Carga completa.")
        
        # Iniciar el timer de actualizaciones en vivo (ej: cada 2 segundos)
        if self.update_timer:
            self.update_timer.start(2000) 
            logging.info("Timer de actualizacion en vivo iniciado.")

    # ---(Slots llamados por main.py) ---

    def actualizar_display_graficas(self):
        """
        Muestra/Oculta los widgets de gráfica correctos según la paginación
        y les pide que se redibujen con la sección actual.
        """
        logging.info(f"Actualizando display: Seccion='{self.seccion_actual}', Pagina={self.pagina_actual}")
        
        total_sensores = len(self.lista_macs_ordenada)
        if total_sensores == 0:
            total_paginas = 1
        else:
            total_paginas = math.ceil(total_sensores / SENSORES_POR_PAGINA)
            
        # Asegurarse que la página actual sea válida
        if self.pagina_actual >= total_paginas: self.pagina_actual = total_paginas - 1
        if self.pagina_actual < 0: self.pagina_actual = 0
            
        start_index = self.pagina_actual * SENSORES_POR_PAGINA
        end_index = start_index + SENSORES_POR_PAGINA
        
        sensores_a_mostrar = self.lista_macs_ordenada[start_index:end_index]
        logging.info(f"Mostrando sensores (indices {start_index}-{end_index}): {sensores_a_mostrar}")

        # Ocultar todos los widgets, luego mostrar solo los de esta página
        for mac, widget in self.widgets_graficas.items():
            if mac in sensores_a_mostrar:
                datos_del_sensor = self.datos_sensores.get(mac)
                if datos_del_sensor:
                    widget.actualizar_grafica(datos_del_sensor, self.seccion_actual)
                widget.show()
            else:
                widget.hide()
            
        # Actualizar estado de paginación en la UI
        hay_anterior = self.pagina_actual > 0
        hay_siguiente = end_index < total_sensores
        
        self.ui.actualizar_estado_paginacion(
            self.pagina_actual, total_paginas, hay_anterior, hay_siguiente
        )

    @Slot(QObject, bool)
    def on_radio_button_toggled(self, radio_button, checked):
        """Slot llamado cuando CUALQUIER radio button cambia."""
        # Solo reaccionamos al que se activó (checked=True)
        if not checked:
            return

        seccion_nombre_ui = radio_button.text()
        nueva_seccion = self.ui.radio_map.get(seccion_nombre_ui, "distancias")
        
        if nueva_seccion == self.seccion_actual:
            return
            
        logging.info(f"Cambiando a seccion: {nueva_seccion}")
        self.seccion_actual = nueva_seccion
        # Redibujar las gráficas visibles con la nueva sección
        self.actualizar_display_graficas()

    @Slot()
    def siguiente_pagina(self):
        """Slot llamado por el botón 'Siguiente'."""
        logging.info("Boton 'Siguiente' presionado.")
        self.pagina_actual += 1
        self.actualizar_display_graficas()

    @Slot()
    def pagina_anterior(self):
        """Slot llamado por el botón 'Anterior'."""
        logging.info("Boton 'Anterior' presionado.")
        self.pagina_actual -= 1
        self.actualizar_display_graficas()

    # --- Funciones de Ayuda (Lógica de Datos) ---

    def inicializar_estructura_datos(self, mac):
        """Crea la estructura de deques (colas) para un nuevo sensor."""
        logging.info(f"Inicializando estructura de datos para nueva MAC: {mac}")
        self.datos_sensores[mac] = {
            'muestras': deque(maxlen=MAX_MUESTRAS),  
            'D1': deque(maxlen=MAX_MUESTRAS),
            'D2': deque(maxlen=MAX_MUESTRAS),
            'D3': deque(maxlen=MAX_MUESTRAS),
            'temperatura': deque(maxlen=MAX_MUESTRAS),
            'humedad': deque(maxlen=MAX_MUESTRAS),
            'quaterniones': deque(maxlen=MAX_MUESTRAS) 
        }
        self.ultimos_valores_validos[mac] = {'D1': None, 'D2': None, 'D3': None}

    def validate_values(self, mac, distancia_actual, tipo_distancia):
        """Corrige valores cero (o inválidos)."""
        if distancia_actual <= 0:
            if self.ultimos_valores_validos[mac].get(tipo_distancia) is not None:
                return self.ultimos_valores_validos[mac][tipo_distancia]
            else:
                return 0.0 # No hay valor previo, devolver 0
        
        self.ultimos_valores_validos[mac][tipo_distancia] = distancia_actual
        return distancia_actual