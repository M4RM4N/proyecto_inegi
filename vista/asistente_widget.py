from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QHBoxLayout, QLabel
)
from PyQt5.QtCore import QThread, pyqtSignal, QObject

# --- Worker Thread ---
# Clase para ejecutar el controlador en segundo plano
class AsistenteWorker(QObject):
    # Señal que emitirá la respuesta cuando esté lista
    respuesta_lista = pyqtSignal(str)
    
    def __init__(self, controller, pregunta):
        super().__init__()
        self.controller = controller
        self.pregunta = pregunta

    def run(self):
        """Ejecuta la tarea en segundo plano."""
        try:
            respuesta = self.controller.chatear(self.pregunta)
            self.respuesta_lista.emit(respuesta)
        except Exception as e:
            self.respuesta_lista.emit(f"Error en el hilo: {e}")

# --- Pestaña de Chat ---
class AsistenteWidget(QWidget):
    """
    Pestaña de Chat que interactúa con el AsistenteController.
    """
    def __init__(self, asistente_controller):
        super().__init__()
        self.controller = asistente_controller
        self.thread = None # Para manejar la referencia al hilo
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. Visor del Chat (solo lectura)
        self.visor_chat = QTextEdit()
        self.visor_chat.setReadOnly(True)
        self.visor_chat.setPlaceholderText("Haz una pregunta sobre los datos del censo...")
        layout.addWidget(self.visor_chat)
        
        # 2. Línea de entrada
        input_layout = QHBoxLayout()
        self.txt_pregunta = QLineEdit()
        self.txt_pregunta.setPlaceholderText("Escribe tu pregunta aquí (ej: ¿Cuántos habitantes hay en Saltillo?)")
        
        self.btn_enviar = QPushButton("Enviar")
        
        input_layout.addWidget(self.txt_pregunta)
        input_layout.addWidget(self.btn_enviar)
        layout.addLayout(input_layout)
        
        # --- Conexiones ---
        self.btn_enviar.clicked.connect(self.enviar_pregunta)
        self.txt_pregunta.returnPressed.connect(self.enviar_pregunta)

    def enviar_pregunta(self):
        pregunta = self.txt_pregunta.text().strip()
        if not pregunta:
            return
            
        # Deshabilitar UI mientras se procesa
        self.btn_enviar.setEnabled(False)
        self.txt_pregunta.setEnabled(False)
        
        # Mostrar la pregunta en el chat
        self.visor_chat.append(f"<b>Tú:</b> {pregunta}\n")
        self.visor_chat.append("<b>Asistente:</b> Pensando...")
        
        # Limpiar la entrada
        self.txt_pregunta.clear()

        # 1. Crear el Worker y el Hilo
        self.worker = AsistenteWorker(self.controller, pregunta)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        
        # 2. Conectar señales
        self.thread.started.connect(self.worker.run)
        self.worker.respuesta_lista.connect(self.mostrar_respuesta)
        
        # 3. Limpieza del hilo
        self.worker.respuesta_lista.connect(self.thread.quit)
        self.worker.respuesta_lista.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # 4. Iniciar el hilo
        self.thread.start()

    def mostrar_respuesta(self, respuesta: str):
        """Slot que recibe la respuesta del hilo y actualiza la UI."""
        # Reemplazar el "Pensando..." con la respuesta real
        cursor = self.visor_chat.textCursor()
        cursor.movePosition(cursor.End)
        cursor.select(cursor.BlockUnderCursor)
        cursor.removeSelectedText()
        self.visor_chat.append(f"<b>Asistente:</b> {respuesta}\n")
        
        # Rehabilitar UI
        self.btn_enviar.setEnabled(True)
        self.txt_pregunta.setEnabled(True)
        self.txt_pregunta.setFocus()