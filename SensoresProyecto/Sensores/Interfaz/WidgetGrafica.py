import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox
from PySide6.QtCore import Slot

# --- Importaciones de Matplotlib ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from collections import deque

# Configurar logging
logger = logging.getLogger(__name__)

class GraficaWidget(QGroupBox):
    """
    widget que contiene una figura, canvas y
    barra de herramientas de Matplotlib. Sabe cómo dibujarse a sí mismo.
    """
    def __init__(self, mac, parent=None):
        
        # Usar los últimos 6 dígitos de la MAC para el título
        mac_suffix = f'{mac.split(":")[-2]}:{mac.split(":")[-1]}' if ':' in mac else mac
        super().__init__(f"Sensor: {mac_suffix}", parent)
        
        self.mac = mac
        self.setMinimumHeight(350) # Darle tamaño
        
        #  Configuracion 
        self.figura = Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figura)
        self.ax = self.figura.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self) # Barra de herramientas
        
        #  layout 
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    @Slot(dict, str)
    def actualizar_grafica(self, datos_sensor: dict, seccion: str):
        """
        Función principal. Borra y redibuja el lienzo (canvas)
        basado en la sección y los datos (deques) proporcionados.
        """
        if not datos_sensor:
            logger.warning(f"No hay datos para {self.mac}")
            return
            
        self.ax.clear() # Limpiar el eje
        
        try:
            # Seleccionar la función de dibujo apropiada
            if seccion == 'distancias':
                self.dibujar_distancias(datos_sensor)
            elif seccion == 'temperatura':
                self.dibujar_temperatura(datos_sensor)
            elif seccion == 'humedad':
                self.dibujar_humedad(datos_sensor)
            elif seccion == 'quaterniones':
                self.dibujar_quaterniones(datos_sensor)
            
            # Configuración común
            self.ax.legend(loc='upper right', fontsize=8)
            self.ax.grid(True, linestyle='--', alpha=0.5)
            self.ax.set_xlabel('Identificador de Muestra', fontsize=10)
            
            # Ajustar límites X (eje horizontal)
            muestras = list(datos_sensor.get('muestras', []))
            if muestras:
                # Mostrar solo las últimas N muestras si hay muchas
                # O simplemente dejar que Matplotlib lo ajuste
                self.ax.set_xlim(min(muestras), max(muestras))

        except Exception as e:
            logger.error(f"Error al dibujar gráfica para {self.mac}: {e}")
            self.ax.set_title(f"Error al dibujar: {e}")

        # Redibujar el lienzo
        self.figura.tight_layout()
        self.canvas.draw()

    #  Funciones de Dibujo 
    
    def dibujar_distancias(self, datos):
        muestras = list(datos['muestras'])
        d1 = list(datos['D1'])
        d2 = list(datos['D2'])
        d3 = list(datos['D3'])
        
        if muestras:
            self.ax.plot(muestras, d1, label='D1', color='blue', linewidth=1.5)
            self.ax.plot(muestras, d2, label='D2', color='red', linewidth=1.5)
            self.ax.plot(muestras, d3, label='D3', color='green', linewidth=1.5)
        
        self.ax.set_ylabel('Distancia (metros)', fontsize=10)
        self.ax.set_title('Mediciones de Distancia', fontsize=12)
        
        # Ajustar límites Y automáticamente
        todos_datos = d1 + d2 + d3
        datos_validos = [d for d in todos_datos if d > 0]
        if datos_validos:
            y_min = max(0, min(datos_validos) - 0.5)
            y_max = max(datos_validos) + 0.5
            self.ax.set_ylim(y_min, y_max)
        else:
            self.ax.set_ylim(0, 10) # Default

    def dibujar_temperatura(self, datos):
        muestras = list(datos['muestras'])
        temp = list(datos['temperatura'])
        if muestras:
            self.ax.plot(muestras, temp, label='Temperatura', color='red', linewidth=2)
        
        self.ax.set_ylabel('Temperatura (°C)', fontsize=10)
        self.ax.set_title('Temperatura', fontsize=12)
        if temp:
            temp_min = min(temp); temp_max = max(temp)
            margen = max((temp_max - temp_min) * 0.1, 1.0)
            
            self.ax.set_ylim(temp_min - margen, temp_max + margen)

    def dibujar_humedad(self, datos):
        muestras = list(datos['muestras'])
        humedad = list(datos['humedad'])
        if muestras:
            self.ax.plot(muestras, humedad, label='Humedad', color='blue', linewidth=2)
        
        self.ax.set_ylabel('Humedad (%)', fontsize=10)
        self.ax.set_title('Humedad Relativa', fontsize=12)
        self.ax.set_ylim(0, 100) # Fijo

    def dibujar_quaterniones(self, datos):
        muestras = list(datos['muestras'])
        quats = list(datos['quaterniones'])
        if muestras and quats:
            q1 = [q[0] for q in quats]
            
            q2 = [q[1] for q in quats]
            q3 = [q[2] for q in quats]
            q4 = [q[3] for q in quats]
            
            self.ax.plot(muestras, q1, label='Q1 (W)', linewidth=1, alpha=0.8)
            
            self.ax.plot(muestras, q2, label='Q2 (X)', linewidth=1, alpha=0.8)
            self.ax.plot(muestras, q3, label='Q3 (Y)', linewidth=1, alpha=0.8)
            self.ax.plot(muestras, q4, label='Q4 (Z)', linewidth=1, alpha=0.8)
        
        self.ax.set_ylabel('Valor Quaternion', fontsize=10)
        self.ax.set_title('Orientacion (Quaterniones)', fontsize=12)
        self.ax.set_ylim(-1.2, 1.2) # Fijo