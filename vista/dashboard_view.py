from PyQt5.QtWidgets import QMainWindow, QTabWidget, QAction, QApplication, QMessageBox
from PyQt5.QtGui import QIcon

# Importamos los QWidget que actuarán como pestañas
from .reports_widget import ReportsWidget
from .catalogo_widget import CatalogoWidget
from .censo_widget import CensoWidget
from .asistente_widget import AsistenteWidget

class DashboardView(QMainWindow):
    """
    Ventana principal de la aplicación (Dashboard).
    Contiene QTabWidget para la navegación (Requisito 3) y el menú de cierre.
    """
    def __init__(self, catalogo_controller, censo_controller, asistente_controller):
        super().__init__()
        
        self.catalogo_controller = catalogo_controller
        self.censo_controller = censo_controller
        self.asistente_controller = asistente_controller
        
        self.setWindowTitle("Dashboard - Censo de Población INEGI")
        self.setGeometry(100, 100, 950, 700) # Ventana principal más grande
        
        self.setup_ui()
        self.crear_menu() # Requisito 3: Menú para navegar/cerrar

    def setup_ui(self):
        """Configura la interfaz principal con pestañas (Navegación)."""
        
        # 1. Crear el contenedor de pestañas (Navegación)
        self.tab_widget = QTabWidget()
        
        # 2. Crear las pestañas individuales (cada una es un QWidget)
        
        # Pestaña 1: Reportes (Req 9, 10, 12)
        self.reports_tab = ReportsWidget(self.censo_controller)
        
        # Pestaña 2: Operaciones del Censo (Req 6, 7, 8, 11)
        self.censo_tab = CensoWidget(self.censo_controller, self.catalogo_controller)
        
        # Pestaña 3: CRUD de Catálogos (Req 2)
        self.catalogo_tab = CatalogoWidget(self.catalogo_controller)

        # Pestaña 4: Asistente IA
        self.assitente_tab = AsistenteWidget(self.asistente_controller)

        # 3. Añadir las pestañas al contenedor
        self.tab_widget.addTab(self.reports_tab, "Dashboard y Reportes")
        self.tab_widget.addTab(self.censo_tab, "Operaciones del Censo")
        self.tab_widget.addTab(self.catalogo_tab, "Administración de Catálogos")
        self.tab_widget.addTab(self.assitente_tab, "Asistente IA")
        
        # 4. Establecer el QTabWidget como el widget central
        self.setCentralWidget(self.tab_widget)

    def crear_menu(self):
        """Crea la barra de menú principal (Requisito 3)."""
        menubar = self.menuBar()
        
        # Menú "Archivo"
        archivo_menu = menubar.addMenu("&Archivo")
        
        # Acción "Cerrar Sistema"
        exit_action = QAction(QIcon(), "&Cerrar Sistema", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Cierra la aplicación")
        # Conecta la acción a 'self.close' que cierra la QMainWindow
        exit_action.triggered.connect(self.close) 
        
        archivo_menu.addAction(exit_action)

    def closeEvent(self, event):
        """Sobreescribe el evento de cierre para confirmación."""
        reply = QMessageBox.question(self, 'Confirmar Salida',
                                     "¿Está seguro de que desea cerrar el sistema?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # (Aquí iría la lógica de destruir variables de sesión si existieran)
            event.accept() # Cierra la aplicación
        else:
            event.ignore() # Cancela el cierre