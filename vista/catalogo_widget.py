# vista/catalogo_widget.py (Actualizado con CRUD de Localidades)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QLineEdit, QLabel, QFormLayout, QGroupBox, QMessageBox,
    QAbstractItemView, QComboBox, QSplitter, QHeaderView
)
from PyQt5.QtCore import Qt
from modelo import Municipio, Localidad # Para Type Hinting

class CatalogoWidget(QWidget):
    """
    Pestaña para el CRUD de todos los catálogos (Requisito 2).
    Implementado para Municipios y Localidades.
    """
    def __init__(self, catalogo_controller):
        super().__init__()
        self.catalogo_controller = catalogo_controller
        self.current_municipio_id = None
        self.current_localidad_id = None # <-- Añadido
        
        self.setup_ui()
        
        # Carga inicial de datos
        self.poblar_combo_municipios() # <-- Añadido
        self.cargar_municipios()
        self.cargar_localidades() # <-- Añadido

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- Grupo de Municipios (CRUD Completo) ---
        municipio_group = QGroupBox("Municipios")
        municipio_layout = QHBoxLayout()

        # Formulario
        form_widget_muni = QWidget()
        form_layout_muni = QFormLayout(form_widget_muni)
        self.txt_municipio_nombre = QLineEdit()
        self.btn_guardar_municipio = QPushButton("Guardar (Nuevo/Actualizar)")
        self.btn_limpiar_form_muni = QPushButton("Limpiar Formulario")
        self.btn_eliminar_municipio = QPushButton("Eliminar Seleccionado")
        
        form_layout_muni.addRow(QLabel("Nombre:"), self.txt_municipio_nombre)
        form_layout_muni.addRow(self.btn_guardar_municipio)
        form_layout_muni.addRow(self.btn_limpiar_form_muni)
        form_layout_muni.addRow(self.btn_eliminar_municipio)

        # Tabla
        self.tabla_municipios = QTableWidget()
        self.tabla_municipios.setColumnCount(2)
        self.tabla_municipios.setHorizontalHeaderLabels(["ID", "Nombre"])
        self.tabla_municipios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_municipios.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_municipios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        municipio_layout.addWidget(form_widget_muni, 1)
        municipio_layout.addWidget(self.tabla_municipios, 2)
        municipio_group.setLayout(municipio_layout)
        
        # --- Grupo de Localidades (CRUD Completo) ---
        localidad_group = QGroupBox("Localidades")
        localidad_layout = QHBoxLayout()

        # Formulario
        form_widget_loc = QWidget()
        form_layout_loc = QFormLayout(form_widget_loc)
        self.txt_localidad_nombre = QLineEdit()
        self.combo_localidad_municipio = QComboBox() # <-- Importante
        self.btn_guardar_localidad = QPushButton("Guardar (Nuevo/Actualizar)")
        self.btn_limpiar_form_loc = QPushButton("Limpiar Formulario")
        self.btn_eliminar_localidad = QPushButton("Eliminar Seleccionado")
        
        form_layout_loc.addRow(QLabel("Nombre:"), self.txt_localidad_nombre)
        form_layout_loc.addRow(QLabel("Municipio:"), self.combo_localidad_municipio)
        form_layout_loc.addRow(self.btn_guardar_localidad)
        form_layout_loc.addRow(self.btn_limpiar_form_loc)
        form_layout_loc.addRow(self.btn_eliminar_localidad)

        # Tabla
        self.tabla_localidades = QTableWidget()
        self.tabla_localidades.setColumnCount(3) # <-- 3 Columnas
        self.tabla_localidades.setHorizontalHeaderLabels(["ID", "Nombre", "Municipio"])
        self.tabla_localidades.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_localidades.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_localidades.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        localidad_layout.addWidget(form_widget_loc, 1)
        localidad_layout.addWidget(self.tabla_localidades, 2)
        localidad_group.setLayout(localidad_layout)

        # Usamos un Splitter para que sean redimensionables
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(municipio_group)
        splitter.addWidget(localidad_group)
        main_layout.addWidget(splitter)
        
        # (Aquí se añadirían QGroupBox para TipoVivienda y ActividadEconomica)

        # --- Conexiones Municipios ---
        self.btn_guardar_municipio.clicked.connect(self.guardar_municipio)
        self.btn_limpiar_form_muni.clicked.connect(self.limpiar_form_municipio)
        self.btn_eliminar_municipio.clicked.connect(self.eliminar_municipio)
        self.tabla_municipios.itemClicked.connect(self.seleccionar_municipio)

        # --- Conexiones Localidades ---
        self.btn_guardar_localidad.clicked.connect(self.guardar_localidad)
        self.btn_limpiar_form_loc.clicked.connect(self.limpiar_form_localidad)
        self.btn_eliminar_localidad.clicked.connect(self.eliminar_localidad)
        self.tabla_localidades.itemClicked.connect(self.seleccionar_localidad)

    # --- Métodos de Municipio ---
    
    def limpiar_form_municipio(self):
        self.current_municipio_id = None
        self.txt_municipio_nombre.clear()
        self.tabla_municipios.clearSelection()

    def cargar_municipios(self):
        self.tabla_municipios.setRowCount(0)
        lista_municipios: list[Municipio] = self.catalogo_controller.obtener_todos_municipios()
        for i, municipio in enumerate(lista_municipios):
            self.tabla_municipios.insertRow(i)
            self.tabla_municipios.setItem(i, 0, QTableWidgetItem(str(municipio.id)))
            self.tabla_municipios.setItem(i, 1, QTableWidgetItem(municipio.nombre))
        self.limpiar_form_municipio()
        # Actualizar el combobox de localidades por si cambiaron los municipios
        self.poblar_combo_municipios() 

    def seleccionar_municipio(self, item):
        fila = self.tabla_municipios.row(item)
        id_municipio = self.tabla_municipios.item(fila, 0).text()
        nombre_municipio = self.tabla_municipios.item(fila, 1).text()
        self.current_municipio_id = int(id_municipio)
        self.txt_municipio_nombre.setText(nombre_municipio)

    def guardar_municipio(self):
        nombre = self.txt_municipio_nombre.text()
        if not nombre:
            QMessageBox.warning(self, "Datos Incompletos", "El nombre del municipio no puede estar vacío.")
            return
            
        if self.current_municipio_id is None:
            resultado = self.catalogo_controller.guardar_municipio(nombre)
            mensaje = f"Municipio '{resultado.nombre}' creado."
        else:
            resultado = self.catalogo_controller.actualizar_municipio(self.current_municipio_id, nombre)
            mensaje = f"Municipio '{resultado.nombre}' actualizado."
        
        if resultado:
            QMessageBox.information(self, "Éxito", mensaje)
            self.cargar_municipios()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar el municipio.")

    def eliminar_municipio(self):
        if self.current_municipio_id is None:
            QMessageBox.warning(self, "Sin Selección", "Seleccione un municipio de la tabla para eliminar.")
            return

        confirmar = QMessageBox.question(self, "Confirmar Eliminación",
                                         f"¿Seguro desea eliminar el municipio ID {self.current_municipio_id}?\nADVERTENCIA: Esto podría eliminar localidades asociadas.",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if confirmar == QMessageBox.Yes:
            exito = self.catalogo_controller.eliminar_municipio(self.current_municipio_id)
            if exito:
                QMessageBox.information(self, "Eliminado", "El municipio ha sido eliminado.")
                self.cargar_municipios()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el municipio (puede tener localidades activas).")

    # --- Métodos de Localidad (NUEVOS) ---

    def poblar_combo_municipios(self):
        """Llena el ComboBox de municipios en el formulario de Localidad."""
        self.combo_localidad_municipio.clear()
        self.combo_localidad_municipio.addItem("Seleccione un Municipio...", None)
        municipios = self.catalogo_controller.obtener_todos_municipios()
        for m in municipios:
            self.combo_localidad_municipio.addItem(m.nombre, m.id)

    def limpiar_form_localidad(self):
        self.current_localidad_id = None
        self.txt_localidad_nombre.clear()
        self.combo_localidad_municipio.setCurrentIndex(0) # Volver a "Seleccione..."
        self.tabla_localidades.clearSelection()

    def cargar_localidades(self):
        """Carga la tabla de localidades."""
        self.tabla_localidades.setRowCount(0)
        # Usamos el Eager Loading (joinedload) que definimos en el controlador
        lista_localidades: list[Localidad] = self.catalogo_controller.obtener_todas_localidades()
        
        for i, loc in enumerate(lista_localidades):
            self.tabla_localidades.insertRow(i)
            self.tabla_localidades.setItem(i, 0, QTableWidgetItem(str(loc.id)))
            self.tabla_localidades.setItem(i, 1, QTableWidgetItem(loc.nombre))
            # Gracias al Eager Loading, esto no causa un error DetachedInstance
            self.tabla_localidades.setItem(i, 2, QTableWidgetItem(loc.municipio.nombre))
        
        self.limpiar_form_localidad()

    def seleccionar_localidad(self, item):
        """Carga los datos de la fila seleccionada en el formulario de localidad."""
        fila = self.tabla_localidades.row(item)
        id_localidad = self.tabla_localidades.item(fila, 0).text()
        nombre_localidad = self.tabla_localidades.item(fila, 1).text()
        nombre_municipio = self.tabla_localidades.item(fila, 2).text()
        
        self.current_localidad_id = int(id_localidad)
        self.txt_localidad_nombre.setText(nombre_localidad)
        
        # Buscar y seleccionar el municipio correcto en el ComboBox
        index = self.combo_localidad_municipio.findText(nombre_municipio, Qt.MatchFixedString)
        if index >= 0:
            self.combo_localidad_municipio.setCurrentIndex(index)

    def guardar_localidad(self):
        """Maneja 'Crear' (C) y 'Actualizar' (U) para Localidad."""
        nombre = self.txt_localidad_nombre.text()
        id_municipio = self.combo_localidad_municipio.currentData() # Obtiene el ID del municipio
        
        if not nombre or not id_municipio:
            QMessageBox.warning(self, "Datos Incompletos", "Debe ingresar un nombre y seleccionar un municipio.")
            return

        if self.current_localidad_id is None:
            # --- CREAR (C) ---
            resultado = self.catalogo_controller.guardar_localidad(nombre, id_municipio)
            mensaje = f"Localidad '{resultado.nombre}' creada."
        else:
            # --- ACTUALIZAR (U) ---
            resultado = self.catalogo_controller.actualizar_localidad(self.current_localidad_id, nombre, id_municipio)
            mensaje = f"Localidad '{resultado.nombre}' actualizada."
        
        if resultado:
            QMessageBox.information(self, "Éxito", mensaje)
            self.cargar_localidades() # Recargar la tabla
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la localidad.")

    def eliminar_localidad(self):
        """Maneja 'Eliminar' (D) para Localidad."""
        if self.current_localidad_id is None:
            QMessageBox.warning(self, "Sin Selección", "Seleccione una localidad de la tabla para eliminar.")
            return

        confirmar = QMessageBox.question(self, "Confirmar Eliminación",
                                         f"¿Seguro desea eliminar la localidad ID {self.current_localidad_id}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if confirmar == QMessageBox.Yes:
            exito = self.catalogo_controller.eliminar_localidad(self.current_localidad_id)
            if exito:
                QMessageBox.information(self, "Eliminado", "La localidad ha sido eliminada.")
                self.cargar_localidades()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar la localidad (puede tener viviendas activas).")