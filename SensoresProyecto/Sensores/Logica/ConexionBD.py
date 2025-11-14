from PySide6.QtCore import QObject, Signal, Slot
import logging
import pyodbc
import datetime

# Configurar logging para este módulo
logger = logging.getLogger(__name__)

class DatabaseWorker(QObject):
    """
    Se ejecuta en un QThread separado.
    Maneja las interacciones con la base de datos
    para evitar que la GUI se congele.
    """
    
    # Señales (signals) que este worker emite:
    new_data_row = Signal(list)       # Emite una fila de datos nueva+
    initial_load_finished = Signal(int) # Emite cuando la carga termina (con el # de sensores)
    status_update = Signal(str)       # Emite mensajes de estado/error

    def __init__(self, connection_string):
        super().__init__()
        self.connection_string = connection_string
        self.running = True
        
        # Rastrea la última fecha/hora consultada para obtener solo datos nuevos
        self.last_timestamp_queried = datetime.datetime.min 

    @Slot()
    def load_initial_data(self):
        """
        Carga TODOS los datos
        Se ejecuta una vez cuando el hilo arranca.
        """
        logger.info("Worker: Iniciando carga inicial de datos...")
        sensor_count = set() # Usamos un set para contar MACs únicas
        try:
            # Usamos 'with' para asegurar que la conexión se cierre
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # Seleccionar todas las columnas necesarias, ordenadas por fecha
                query = """
                    SELECT
                        [MAC_Sensor], [Capa], [No_paquete], 
                        [Distancia_1], [Distancia_2], [Distancia_3], 
                        [Temperatura], [Humedad], 
                        [Q1], [Q2], [Q3], [Q4], 
                        [Identificador], [Fecha]
                    FROM [Sensores].[dbo].[Data_sensor]
                    ORDER BY [Fecha] ASC
                """
                cursor.execute(query)
                
                for row in cursor:
                    if not self.running:
                        logger.info("Worker: Carga inicial detenida.")
                        break
                    
                    # Convertimos la fila a lista y la emitimos
                    row_data = list(row)
                    self.new_data_row.emit(row_data)
                    
                    sensor_count.add(row[0]) # Añadir MAC al set
                    
                    # Guardar la última marca de tiempo (índice 13)
                    self.last_timestamp_queried = row[13] 

                if self.running:
                    logger.info(f"Worker: Carga inicial completada. {len(sensor_count)} sensores únicos.")
                    # Emitir la señal de finalización con el conteo
                    self.initial_load_finished.emit(len(sensor_count))
                    self.status_update.emit("Carga inicial completada. Listo.")
                    
        except pyodbc.Error as e:
            logger.error(f"Worker: Error de PyODBC en carga inicial: {e}")
            self.status_update.emit(f"Error de BD (Carga): {e}")
        except Exception as e:
            logger.error(f"Worker: Error inesperado en carga inicial: {e}")
            self.status_update.emit(f"Error (Carga): {e}")

    @Slot()
    def check_for_updates(self):
        """
        Busca NUEVOS datos (por el timestamp).
        Llamado por el QTimer de la lógica principal.
        """
        if not self.running:
            return
            
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # filas recientes que la última que vimos
                query = """
                    SELECT
                        [MAC_Sensor], [Capa], [No_paquete], 
                        [Distancia_1], [Distancia_2], [Distancia_3], 
                        [Temperatura], [Humedad], 
                        [Q1], [Q2], [Q3], [Q4], 
                        [Identificador], [Fecha]
                    FROM [Sensores].[dbo].[Data_sensor]
                    WHERE [Fecha] > ?
                    ORDER BY [Fecha] ASC
                """
                
                #ultima marca de tiempo como parámetro
                cursor.execute(query, (self.last_timestamp_queried,))
                
                nuevos_registros = 0
                for row in cursor:
                    if not self.running:
                        logger.info("Worker: Búsqueda de actualizaciones detenida.")
                        break
                        
                    row_data = list(row)
                    self.new_data_row.emit(row_data)
                    self.last_timestamp_queried = row[13] # Actualizar marca de tiempo
                    nuevos_registros += 1
                
                if nuevos_registros > 0:
                     logger.info(f"Worker: {nuevos_registros} nuevos registros encontrados.")
                     self.status_update.emit(f"{nuevos_registros} nuevos registros procesados.")

        except pyodbc.Error as e:
            logger.error(f"Worker: Error de PyODBC en actualización: {e}")
            self.status_update.emit(f"Error de BD (Actualización): {e}")
        except Exception as e:
            logger.error(f"Worker: Error inesperado en actualización: {e}")
            self.status_update.emit(f"Error (Actualización): {e}")

    def stop(self):
        """Permite detener el worker de forma segura desde el hilo principal."""
        self.running = False
        logger.info("Worker: Señal de detención recibida.")