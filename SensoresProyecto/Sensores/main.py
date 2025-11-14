import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import logging

# Importamos las clases de nuestros módulos
from Interfaz.Graficasui import SensorMonitorUI
from Logica.Graficaslogica import AppLogica

# Configurar logging básico para ver los eventos en la terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    app = QApplication(sys.argv)
    # 1. Crear la Ventana de la Interfaz
    ventana_ui = SensorMonitorUI()
    # 2. inicis lógica de la aplicación
    logica = AppLogica(ventana_ui)
    
    # 3.Conectar elementos Señales y Slots
    #  Conectar Paginación 
    ventana_ui.btn_siguiente.clicked.connect(logica.siguiente_pagina)
    ventana_ui.btn_anterior.clicked.connect(logica.pagina_anterior)
    
    # Conectar Selección de Sección 
    # Conectamos el QButtonGroup. Pasará el botón presionado y (bool)checked
    ventana_ui.grupo_radios_seccion.buttonToggled.connect(logica.on_radio_button_toggled)

    # Configurar el Timer para actualizaciones en vivo 
    # QTimer en el hilo principal
    auto_update_timer = QTimer()
    # Conectamos su 'timeout' al slot 'check_for_updates' del *worker*
    # (La lógica se encarga de obtener la referencia al worker)
    # Le pasamos el timer a la lógica para que lo gestione
    logica.set_update_timer(auto_update_timer)

    # 4. Iniciar la lógica de la aplicación
    # (Esto iniciará el hilo de la BD para la carga inicial)
    logica.iniciar()

    # 5. Mostrar la ventana y ejecutar la aplicación
    ventana_ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()