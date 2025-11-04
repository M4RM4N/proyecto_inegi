import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QMessageBox, QDesktopWidget
)
# Importamos la ventana principal (Dashboard)
from .dashboard_view import DashboardView 

class LoginView(QWidget):
    """
    Vista de Login (Requisito 1). 
    Interactúa con AdminController para la autenticación.
    """
    def __init__(self, admin_controller, catalogo_controller, censo_controller, asistente_controller):
        super().__init__()
        
        # Guardamos referencias a todos los controladores
        self.admin_controller = admin_controller
        self.catalogo_controller = catalogo_controller
        self.censo_controller = censo_controller
        self.asistente_controller = asistente_controller
        
        # Referencia a la ventana principal
        self.dashboard_view = None
        
        self.setWindowTitle("Censo INEGI Coahuila - Acceso de Administrador")
        self.setFixedSize(350, 200) # Tamaño fijo para el login
        self.setup_ui()
        self.center()

    def setup_ui(self):
        """Crea los widgets de la interfaz."""
        layout = QVBoxLayout()
        
        self.lbl_usuario = QLabel("Usuario:")
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Ingrese su usuario")
        
        self.lbl_contrasena = QLabel("Contraseña:")
        self.txt_contrasena = QLineEdit()
        self.txt_contrasena.setPlaceholderText("Ingrese su contraseña")
        self.txt_contrasena.setEchoMode(QLineEdit.Password) # Ocultar contraseña
        
        self.btn_ingresar = QPushButton("Ingresar")
        
        layout.addWidget(self.lbl_usuario)
        layout.addWidget(self.txt_usuario)
        layout.addWidget(self.lbl_contrasena)
        layout.addWidget(self.txt_contrasena)
        layout.addSpacing(10)
        layout.addWidget(self.btn_ingresar)
        
        self.setLayout(layout)
        
        # --- Conexión (Señal -> Slot) ---
        self.btn_ingresar.clicked.connect(self.intentar_login)
        # Permite presionar Enter para ingresar
        self.txt_contrasena.returnPressed.connect(self.intentar_login)

    def center(self):
        """Centra la ventana en la pantalla."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def intentar_login(self):
        """
        Slot que se ejecuta al hacer clic en 'Ingresar'.
        Llama al AdminController para verificar las credenciales.
        """
        usuario = self.txt_usuario.text()
        contrasena = self.txt_contrasena.text()
        
        if not usuario or not contrasena:
            QMessageBox.warning(self, "Datos Incompletos", "Debe ingresar un usuario y una contraseña.")
            return

        # 1. La VISTA llama al CONTROLADOR
        login_exitoso = self.admin_controller.verificar_login(usuario, contrasena)
        
        # 2. La VISTA reacciona a la respuesta del CONTROLADOR
        if login_exitoso:
            self.abrir_dashboard()
        else:
            QMessageBox.warning(self, "Error de Acceso", "Usuario o contraseña incorrectos.")
            self.txt_contrasena.clear()

    def abrir_dashboard(self):
        """Crea y muestra la ventana principal (Dashboard)."""
        # Creamos la ventana principal y le pasamos los controladores necesarios
        self.dashboard_view = DashboardView(
            catalogo_controller=self.catalogo_controller,
            censo_controller=self.censo_controller,
            asistente_controller=self.asistente_controller
        )
        self.dashboard_view.show()
        self.close() # Cierra la ventana de login