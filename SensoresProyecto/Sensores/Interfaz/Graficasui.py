import logging
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, 
                             QLabel, QPushButton, QRadioButton,
                             QGroupBox, QScrollArea, QHBoxLayout, QStatusBar,
                             QButtonGroup)
from PySide6.QtCore import Qt

# Importamos el widget de gráfica
from .WidgetGrafica import GraficaWidget

class SensorMonitorUI(QMainWindow):
    """
    Ventana Principal y todos los componentes.
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sistema de Monitoreo de Sensores")
        self.setGeometry(100, 100, 900, 700)
        
        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout_principal = QVBoxLayout(central_widget)
        
        self.setup_controles()
        self.setup_area_graficas()
        
        # Barra de estado
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Listo.")

    def setup_controles(self):
        """Crea la sección superior de controles (paginas y secciones)"""
        
        grupo_controles = QGroupBox("Controles")
        layout_controles = QHBoxLayout(grupo_controles)
        
        
        grupo_seccion = QGroupBox("Seleccion de Grafica")
        layout_seccion = QHBoxLayout(grupo_seccion)
        
        # Mapeo de texto de UI a ID de lógica
        self.radio_map = {
            "Distancias": "distancias",
            "Temperatura": "temperatura",
            "Humedad": "humedad",
            "Quaterniones": "quaterniones"
        }
        
        self.grupo_radios_seccion = QButtonGroup(self)
        
        for texto in self.radio_map.keys():
            radio = QRadioButton(texto)
            layout_seccion.addWidget(radio)
            self.grupo_radios_seccion.addButton(radio)
            if texto == "Distancias":
                radio.setChecked(True) # Default
        
        #Grupo de Paginación 
        grupo_paginacion = QGroupBox("Navegación de Sensores (3 por pág)")
        layout_paginacion = QHBoxLayout(grupo_paginacion)
        
        self.btn_anterior = QPushButton("<- Anterior")
        self.label_pagina = QLabel("Página 1 / 1")
        self.btn_siguiente = QPushButton("Siguiente ->")
        
        layout_paginacion.addWidget(self.btn_anterior)
        layout_paginacion.addWidget(self.label_pagina)
        layout_paginacion.addWidget(self.btn_siguiente)
        
        layout_controles.addWidget(grupo_seccion)
        layout_controles.addWidget(grupo_paginacion)
        layout_controles.addStretch() 
        
        self.layout_principal.addWidget(grupo_controles)

    def setup_area_graficas(self):
        """Crea el area donde se mostrarán las graficas"""
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.widget_contenedor_graficas = QWidget()
        # Usamos un verticaubox para apilar las graficas verticalmente
        self.layout_graficas = QVBoxLayout(self.widget_contenedor_graficas)
        self.layout_graficas.setAlignment(Qt.AlignmentFlag.AlignTop) 
        
        scroll.setWidget(self.widget_contenedor_graficas)
        self.layout_principal.addWidget(scroll)

    # Funciones de Ayuda (Llamadas por la Lógica) 

    def limpiar_layout_graficas(self):
        """
        Elimina todos los widgets de graficas del layout.
        """
        logging.debug("Limpiando layout de graficas...")
        while self.layout_graficas.count():
            child = self.layout_graficas.takeAt(0)
            if child.widget():
                child.widget().deleteLater() # Borrar el widget de memoria

    def crear_grafica_real(self, mac) -> GraficaWidget:
        """
        Crea el widget de gráfica real
        y lo añade al layout. Devuelve la instancia.
        """
        logging.info(f"UI: Creando GraficaWidget real para {mac}")
        widget = GraficaWidget(mac) # Usa la clase
        self.layout_graficas.addWidget(widget)
        return widget
        
    def actualizar_estado_paginacion(self, pagina_actual_cero_index, total_paginas, hay_anterior, hay_siguiente):
        """Actualiza la etiqueta de página y habilita/deshabilita botones"""
        self.label_pagina.setText(f"Página {pagina_actual_cero_index + 1} / {total_paginas}")
        self.btn_anterior.setEnabled(hay_anterior)
        self.btn_siguiente.setEnabled(hay_siguiente)

    def obtener_seccion_seleccionada(self) -> str:
        """Devuelve el ID de la sección seleccionada (ej: 'distancias')"""
        boton_chequeado = self.grupo_radios_seccion.checkedButton()
        if boton_chequeado:
            return self.radio_map.get(boton_chequeado.text(), 'distancias')
        return 'distancias'