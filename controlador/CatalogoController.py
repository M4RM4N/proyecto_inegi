from .BaseController import BaseController
from modelo import Municipio, Localidad, TipoVivienda, ActividadEconomica
from typing import List, Optional
from sqlalchemy.orm import joinedload

class CatalogoController(BaseController):
    """
    Controlador para el CRUD de entidades de catalogo (Municipio, Localidad, etc.)
    """

    # --- METODOS GENERICOS DE CATALOGO --- 
    # --- De municipios ---

    def obtener_todos_municipios(self) -> List[Municipio]:
        """
        Obtiene la lista de todos los municipios
        """
        return self.municipio_dao.listar_todos(Municipio)
    
    def guardar_municipio(self, nombre_municipio: str) -> Municipio | None:
        """
        Crea y guarda un nuevo municipio.
        (Ejemplo de integración con lógica de Factory si fuera necesario)
        """
        if not nombre_municipio:
            print("El nombre del municipio no puede estar vacío.")
            return None
            
        # 1. Crear el objeto: Puede usar el Factory, pero para catálogos simples es directo.
        nuevo_municipio = Municipio(nombre=nombre_municipio)
        
        # 2. Persistir: Llama al DAO
        return self.municipio_dao.guardar(nuevo_municipio)
    
    def actualizar_municipio(self, id_municipio: int, nombre_nuevo: str) -> Optional[Municipio]:
        """(U)pdate: Actualiza un municipio existente."""
        # 1. Obtener el objeto
        municipio = self.municipio_dao.obtener_por_id(Municipio, id_municipio)
        
        if municipio:
            # 2. Modificar el objeto
            municipio.nombre = nombre_nuevo
            # 3. Guardar (el DAO.guardar detecta que es una actualización)
            return self.municipio_dao.guardar(municipio)
        return None
    
    def eliminar_municipio(self, id_municipio: int) -> bool:
        """(D)elete: Elimina un municipio por su ID."""
        return self.municipio_dao.eliminar(Municipio, id_municipio)

    # --- De localidad ---
    
    def obtener_localidades_por_municipio(self, id_municipio: int) -> List[Localidad]:
        """
        Obtiene las localidades dependientes de un municipio específico.
        """
        return self.localidad_dao.obtener_por_municipio(id_municipio)
        
    def obtener_todas_localidades(self) -> List[Localidad]:
        """
        Obtiene todas las localidades, incluyendo su municipio (Eager Loading).
        Usado para el ComboBox de CensoWidget.
        """
        # Usamos Eager Loading (joinedload) para que 'loc.municipio.nombre'
        # no cause consultas N+1 en la vista.
        opciones = [joinedload(Localidad.municipio)]
        return self.localidad_dao.listar_todos(Localidad, options=opciones)
    
    def guardar_localidad(self, nombre: str, id_municipio: int) -> Optional[Localidad]:
        """(C)rea una nueva localidad."""
        municipio = self.municipio_dao.obtener_por_id(Municipio, id_municipio)
        if not nombre or not municipio:
            print("Datos incompletos (nombre o municipio) para guardar la localidad.")
            return None
            
        nueva_localidad = Localidad(nombre=nombre, municipio=municipio)
        return self.localidad_dao.guardar(nueva_localidad)
    
    def actualizar_localidad(self, id_localidad: int, nombre_nuevo: str, id_municipio: int) -> Optional[Localidad]:
        """(U)pdate: Actualiza una localidad existente."""
        localidad = self.localidad_dao.obtener_por_id(Localidad, id_localidad)
        municipio = self.municipio_dao.obtener_por_id(Municipio, id_municipio)
        
        if not localidad or not municipio:
            print("No se encontró la localidad o el municipio para actualizar.")
            return None
            
        localidad.nombre = nombre_nuevo
        localidad.municipio = municipio
        return self.localidad_dao.guardar(localidad)
    
    def eliminar_localidad(self, id_localidad: int) -> bool:
        """(D)elete: Elimina una localidad por su ID."""
        return self.localidad_dao.eliminar(Localidad, id_localidad)
    


    def obtener_todos_tipos_vivienda(self) -> List[TipoVivienda]:
        """
        Obtiene todos los tipos de vivienda.
        Usado para el ComboBox de CensoWidget.
        """
        return self.tipo_vivienda_dao.listar_todos(TipoVivienda)
    
    def obtener_todas_actividades_economicas(self) -> List[ActividadEconomica]:
        """Obtiene todas las actividades económicas del catálogo."""
        return self.actividad_dao.listar_todos(ActividadEconomica)