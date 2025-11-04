# vista/reports_widget.py (Actualizado con PyQtGraph)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHeaderView, QMessageBox, QGroupBox, QHBoxLayout, QSplitter
)
from PyQt5.QtCore import Qt

# --- 1. IMPORTACIONES DE PYQTGRAPH y NUMPY ---
import pyqtgraph as pg
import numpy as np

# Configuración global de PyQtGraph (opcional, pero recomendado)
pg.setConfigOption('background', 'w') # Fondo blanco
pg.setConfigOption('foreground', 'k') # Letras negras

class ReportsWidget(QWidget):
    """
    Pestaña que muestra los reportes y el dashboard principal.
    (Requisitos 9, 10, 12 y 25)
    """
    def __init__(self, censo_controller):
        super().__init__()
        self.censo_controller = censo_controller
        
        # --- 2. INICIALIZAR PLOTWIDGET de PyQtGraph ---
        # Creamos el widget del histograma aquí
        self.histograma_widget = pg.PlotWidget()
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- Grupo 1: Dashboard de Población (Sin cambios) ---
        poblacion_group = QGroupBox("Dashboard: Población por Ubicación")
        poblacion_layout = QVBoxLayout()
        self.btn_recargar_poblacion = QPushButton("Recargar Reporte de Población")
        self.tabla_reporte_poblacion = QTableWidget()
        self.tabla_reporte_poblacion.setColumnCount(3)
        self.tabla_reporte_poblacion.setHorizontalHeaderLabels(["Municipio", "Localidad", "Total Habitantes"])
        self.tabla_reporte_poblacion.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        poblacion_layout.addWidget(self.btn_recargar_poblacion)
        poblacion_layout.addWidget(self.tabla_reporte_poblacion)
        poblacion_group.setLayout(poblacion_layout)
        
        # --- Grupo 2: Reporte por Tipo de Vivienda (Sin cambios) ---
        tipo_vivienda_group = QGroupBox("Reporte: Habitantes por Tipo de Vivienda")
        tipo_vivienda_layout = QVBoxLayout()
        self.btn_recargar_tipo = QPushButton("Recargar Reporte por Tipo de Vivienda")
        self.tabla_reporte_tipo = QTableWidget()
        self.tabla_reporte_tipo.setColumnCount(2)
        self.tabla_reporte_tipo.setHorizontalHeaderLabels(["Tipo de Vivienda", "Total Habitantes"])
        self.tabla_reporte_tipo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tipo_vivienda_layout.addWidget(self.btn_recargar_tipo)
        tipo_vivienda_layout.addWidget(self.tabla_reporte_tipo)
        tipo_vivienda_group.setLayout(tipo_vivienda_layout)

        # --- 3. GRUPO 3: Histograma de Edades (Req 25) con PyQtGraph ---
        edad_group = QGroupBox("Estimación Estadística: Distribución de Edades")
        edad_layout = QVBoxLayout()
        
        # Botón de recarga
        self.btn_recargar_histograma = QPushButton("Recargar Histograma de Edades")
        
        # Añadimos los widgets al layout
        # (Se elimina la NavigationToolbar de Matplotlib)
        edad_layout.addWidget(self.histograma_widget) # <-- Aquí se mostrará el gráfico
        edad_layout.addWidget(self.btn_recargar_histograma)
        edad_group.setLayout(edad_layout)

        # --- 4. Añadir los grupos al layout principal (Sin cambios) ---
        splitter_vertical = QSplitter(Qt.Vertical)
        splitter_horizontal = QSplitter(Qt.Horizontal)
        splitter_horizontal.addWidget(poblacion_group)
        splitter_horizontal.addWidget(tipo_vivienda_group)
        splitter_vertical.addWidget(splitter_horizontal)
        splitter_vertical.addWidget(edad_group)
        main_layout.addWidget(splitter_vertical)
        
        # --- 5. Conexiones (Sin cambios) ---
        self.btn_recargar_poblacion.clicked.connect(self.cargar_reporte_poblacion)
        self.btn_recargar_tipo.clicked.connect(self.cargar_reporte_tipo_vivienda)
        self.btn_recargar_histograma.clicked.connect(self.cargar_histograma_edad)
        
        # Carga inicial de datos
        self.cargar_reporte_poblacion()
        self.cargar_reporte_tipo_vivienda()
        self.cargar_histograma_edad()

    # ... (cargar_reporte_poblacion y cargar_reporte_tipo_vivienda sin cambios) ...
    def cargar_reporte_poblacion(self):
        self.tabla_reporte_poblacion.setRowCount(0)
        datos_reporte = self.censo_controller.generar_dashboard_poblacion()
        if not datos_reporte:
            QMessageBox.information(self, "Reporte de Población", "No hay datos de población para mostrar.")
            return
        for i, fila in enumerate(datos_reporte):
            self.tabla_reporte_poblacion.insertRow(i)
            self.tabla_reporte_poblacion.setItem(i, 0, QTableWidgetItem(fila['municipio']))
            self.tabla_reporte_poblacion.setItem(i, 1, QTableWidgetItem(fila['localidad']))
            self.tabla_reporte_poblacion.setItem(i, 2, QTableWidgetItem(str(fila['total_habitantes'])))

    def cargar_reporte_tipo_vivienda(self):
        self.tabla_reporte_tipo.setRowCount(0)
        datos_reporte = self.censo_controller.generar_reporte_tipos_vivienda()
        if not datos_reporte:
            QMessageBox.information(self, "Reporte de Vivienda", "No hay datos de tipos de vivienda para mostrar.")
            return
        for i, fila in enumerate(datos_reporte):
            self.tabla_reporte_tipo.insertRow(i)
            self.tabla_reporte_tipo.setItem(i, 0, QTableWidgetItem(fila['tipo_vivienda']))
            self.tabla_reporte_tipo.setItem(i, 1, QTableWidgetItem(str(fila['habitantes'])))

    # --- 6. MÉTODO ACTUALIZADO (Para PyQtGraph) ---
    def cargar_histograma_edad(self):
        """
        Llama al CensoController y dibuja el Histograma de Edades usando PyQtGraph.
        """
        # 1. VISTA llama al CONTROLADOR
        lista_edades = self.censo_controller.generar_reporte_distribucion_edad()
        
        if not lista_edades:
            QMessageBox.information(self, "Reporte de Edades", "No hay datos de edades para mostrar.")
            return

        try:
            # 2. VISTA actualiza el gráfico PyQtGraph
            
            # Limpiar el gráfico anterior
            self.histograma_widget.clear()
            
            # --- Lógica de Histograma para PyQtGraph ---
            # (a) Calcular los bins (grupos) usando NumPy
            #     'bins=20' crea 20 grupos de edad
            hist, bin_edges = np.histogram(lista_edades, bins=20)
            
            # (b) Calcular el ancho de cada barra
            width = bin_edges[1] - bin_edges[0]
            
            # (c) Crear el BarGraphItem
            bar_item = pg.BarGraphItem(
                x=bin_edges[:-1],  # Posición X de inicio de las barras
                height=hist,       # Altura (conteo de habitantes)
                width=width,       # Ancho de la barra
                brush='teal'       # Color de relleno
            )
            
            # (d) Añadir el gráfico al widget
            self.histograma_widget.addItem(bar_item)
            
            # (e) Configurar etiquetas y títulos
            self.histograma_widget.setTitle('Distribución de Edades de la Población')
            self.histograma_widget.setLabel('bottom', 'Rango de Edad')
            self.histograma_widget.setLabel('left', 'Cantidad de Habitantes')
            self.histograma_widget.showGrid(x=True, y=True, alpha=0.3)
            
        except Exception as e:
            print(f"Error al dibujar el histograma de PyQtGraph: {e}")
            QMessageBox.critical(self, "Error de Gráfico", f"No se pudo dibujar el histograma: {e}")