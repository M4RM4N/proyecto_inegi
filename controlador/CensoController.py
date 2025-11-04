from .BaseController import BaseController
from modelo import Vivienda, Habitante, Localidad, TipoVivienda, ActividadEconomica
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import joinedload, selectinload

class CensoController(BaseController):
    """
    Controlador para el registro de datos de censo y generacion de reportes
    """

    # --- REGISTRO DE DATOS (Usa el factory method) ---

    def registrar_nueva_vivienda(self, datos_vivienda: Dict[str, Any], id_localidad: int, id_tipo_vivienda: int) -> Vivienda | None:
        """
        Usa el Factory para crear la vivienda y el DAO para guardarla
        """

        # 1. Obtener objetos de relacion (necesario para el Factory)
        localidad = self.localidad_dao.obtener_por_id(Localidad, id_localidad)
        tipo_vivienda = self.tipo_vivienda_dao.obtener_por_id(TipoVivienda, id_tipo_vivienda)

        if not localidad or not tipo_vivienda:
            print("Error: Localidad o Tipo de Vivienda invalidos")
            return None
        
        try:
            # 2. Crear objeto (Patron Factory Method)
            nueva_vivienda = self.factory.crear_vivienda(datos_vivienda, localidad, tipo_vivienda)
            
            # 3. Persistir (DAO)
            return self.censo_dao.guardar(nueva_vivienda)
        except ValueError as e:
            print(f"Error de validacion al crear vivienda: {e}")
            return None
        
    def registrar_habitante_en_vivienda(self, id_vivienda: int, datos_habitante: Dict[str, Any]) -> Habitante | None:
        """
        Registra un habitante y lo asocia a una vivienda existente.
        """

        vivienda = self.censo_dao.obtener_por_id(Vivienda, id_vivienda)

        if not vivienda:
            print("Error: Vivienda no encontrada")
            return None
        
        try:
            # 1. Crear Objeto (Patrón Factory Method)
            nuevo_habitante = self.factory.crear_habitante(datos_habitante)
            
            # 2. Asociar (Lógica de Negocio)
            nuevo_habitante.vivienda = vivienda
            
            # 3. Persistir (DAO)
            habitante_guardado = self.censo_dao.guardar(nuevo_habitante)
            
            # Lógica de Negocio Adicional: Actualizar contador de habitantes en Vivienda
            if habitante_guardado:
                vivienda.total_habitante = int(vivienda.total_habitantes) + 1
                self.censo_dao.guardar(vivienda) # Actualizar la vivienda
                return habitante_guardado
            return None
        except ValueError as e:
            print(f"Error de validación al crear habitante: {e}")
            return None
        

    # --- MÉTODOS DE REPORTE (Llamada directa al DAO) ---
    
    def generar_dashboard_poblacion(self) -> List[Dict[str, Any]]:
        """
        Llama al DAO para obtener los datos del dashboard
        """
        return self.censo_dao.obtener_conteo_poblacion_por_ubicacion()

    def generar_reporte_tipos_vivienda(self) -> List[Dict[str, Any]]:
        """
        Llama al DAO para obtener el conteo por tipo de vivienda
        """
        return self.censo_dao.obtener_conteo_por_tipo_vivienda()
    
    def obtener_todas_viviendas_con_localidad(self) -> List[Vivienda]:
        """
        Obtiene todas las viviendas con su localidad (Eager Loading).
        Usado para la tabla principal de CensoWidget.
        """
        # (M:1) joinedload es eficiente aquí
        opciones = [
            joinedload(Vivienda.localidad),
            joinedload(Vivienda.tipo_vivienda)
        ]
        return self.censo_dao.listar_todos(Vivienda, options=opciones)

    def obtener_habitantes_por_vivienda(self, id_vivienda: int) -> List[Habitante]:
        """
        (Req 8) Obtiene solo los habitantes de una vivienda específica.
        """
        # Usamos el método del DAO que carga la vivienda CON sus habitantes
        vivienda = self.censo_dao.obtener_vivienda_con_habitantes(id_vivienda)
        if vivienda:
            return vivienda.habitantes # Retorna la lista cargada (Eager)
        return []

    def obtener_actividades_por_vivienda(self, id_vivienda: int) -> List[ActividadEconomica]:
        """
        (Req 11) Obtiene los OBJETOS de las actividades económicas de una vivienda.
        """
        # 1. Obtener la Vivienda con sus actividades (Eager Loading)
        # (selectinload es mejor para M:M)
        opciones = [selectinload(Vivienda.actividades)]
        vivienda = self.censo_dao.obtener_por_id(Vivienda, id_vivienda, options=opciones)
        
        if vivienda:
            return vivienda.actividades # Retorna la lista de objetos
        return []
    

    def asociar_actividad_a_vivienda(self, id_vivienda: int, id_actividad: int) -> bool:
        """Asocia una Actividad (M:M) a una Vivienda."""
        try:
            # Obtener ambas entidades
            vivienda = self.censo_dao.obtener_por_id(Vivienda, id_vivienda, options=[selectinload(Vivienda.actividades)])
            actividad = self.actividad_dao.obtener_por_id(ActividadEconomica, id_actividad)
            
            if not vivienda or not actividad:
                print("Error: No se encontró la vivienda o la actividad.")
                return False
                
            # Verificar si ya existe la asociación
            if actividad in vivienda.actividades:
                print("La actividad ya está asociada a la vivienda.")
                return False # O True, si la idempotencia es deseada
            
            # Crear la asociación
            vivienda.actividades.append(actividad)
            self.censo_dao.guardar(vivienda) # Guardar la entidad 'padre'
            return True
        except Exception as e:
            print(f"Error al asociar actividad: {e}")
            return False
        

    def desasociar_actividad_de_vivienda(self, id_vivienda: int, id_actividad: int) -> bool:
        """Desasocia una Actividad (M:M) de una Vivienda."""
        try:
            # Obtener ambas entidades, con la relación cargada
            vivienda = self.censo_dao.obtener_por_id(Vivienda, id_vivienda, options=[selectinload(Vivienda.actividades)])
            actividad = self.actividad_dao.obtener_por_id(ActividadEconomica, id_actividad)

            if not vivienda or not actividad:
                print("Error: No se encontró la vivienda o la actividad.")
                return False

            # Verificar si la asociación existe y eliminarla
            if actividad in vivienda.actividades:
                vivienda.actividades.remove(actividad)
                self.censo_dao.guardar(vivienda)
                return True
            else:
                print("Error: La actividad no estaba asociada a esta vivienda.")
                return False
        except Exception as e:
            print(f"Error al desasociar actividad: {e}")
            return False

    
    # --- NUEVOS MÉTODOS PARA CRUD DE VIVIENDA ---

    def actualizar_vivienda(self, id_vivienda: int, datos: Dict[str, Any], id_localidad: int, id_tipo_vivienda: int) -> Optional[Vivienda]:
        """
        (U)pdate: Actualiza una vivienda existente.
        """
        # 1. Obtener la entidad a actualizar
        vivienda = self.censo_dao.obtener_por_id(Vivienda, id_vivienda)
        if not vivienda:
            print(f"Error: No se encontró la vivienda ID {id_vivienda} para actualizar.")
            return None
            
        # 2. Obtener las entidades de relación
        localidad = self.localidad_dao.obtener_por_id(Localidad, id_localidad)
        tipo_vivienda = self.tipo_vivienda_dao.obtener_por_id(TipoVivienda, id_tipo_vivienda)
        
        if not localidad or not tipo_vivienda:
            print("Error: Localidad o Tipo de Vivienda inválidos para la actualización.")
            return None

        # 3. Actualizar los campos
        vivienda.direccion = datos["direccion"]
        vivienda.localidad = localidad
        vivienda.tipo_vivienda = tipo_vivienda
        # (Otros campos como coordenadas_gps se podrían añadir aquí)

        # 4. Guardar (el DAO.guardar maneja la actualización)
        return self.censo_dao.guardar(vivienda)

    def eliminar_vivienda(self, id_vivienda: int) -> bool:
        """
        (D)elete: Elimina una vivienda por su ID.
        (La relación 'cascade="all, delete-orphan"' en el Modelo
        debería eliminar automáticamente a los habitantes).
        """
        return self.censo_dao.eliminar(Vivienda, id_vivienda)
    
    # --- NUEVOS MÉTODOS PARA CRUD DE HABITANTE ---

    def actualizar_habitante(self, id_habitante: int, datos: Dict[str, Any]) -> Optional[Habitante]:
        """
        (U)pdate: Actualiza un habitante existente.
        """
        # 1. Obtener la entidad a actualizar
        habitante = self.censo_dao.obtener_por_id(Habitante, id_habitante)
        if not habitante:
            print(f"Error: No se encontró el habitante ID {id_habitante} para actualizar.")
            return None
            
        # 2. Actualizar los campos
        habitante.nombre_completo = datos["nombre_completo"]
        habitante.edad = datos["edad"]
        habitante.sexo = datos["sexo"]
        habitante.parentesco_con_jefe_familia = datos["parentesco_con_jefe_familia"]

        # 3. Guardar
        return self.censo_dao.guardar(habitante)

    def eliminar_habitante(self, id_habitante: int) -> bool:
        """
        (D)elete: Elimina un habitante por su ID y actualiza el conteo de la vivienda.
        """
        # 1. Obtener el habitante y su vivienda (Eager Load)
        opciones = [joinedload(Habitante.vivienda)]
        habitante = self.censo_dao.obtener_por_id(Habitante, id_habitante, options=opciones)
        
        if not habitante:
            print(f"Error: No se encontró el habitante ID {id_habitante} para eliminar.")
            return False
            
        vivienda_asociada = habitante.vivienda

        # 2. Eliminar el habitante
        exito = self.censo_dao.eliminar(Habitante, id_habitante)
        
        # 3. Lógica de Negocio: Actualizar el contador de la vivienda
        if exito and vivienda_asociada:
            try:
                # Recalcular el total (la forma más segura es contar)
                # (Una forma más simple es restar 1 si total_habitantes no es Nulo)
                if vivienda_asociada.total_habitantes is not None and vivienda_asociada.total_habitantes > 0:
                    vivienda_asociada.total_habitantes -= 1
                    self.censo_dao.guardar(vivienda_asociada)
                return True
            except Exception as e:
                print(f"Error al actualizar el conteo de habitantes: {e}")
                return False # La eliminación fue exitosa pero el conteo falló
        
        return exito
    

    def generar_reporte_distribucion_edad(self) -> List[int]:
        """(Req 25) Llama al DAO para obtener la lista de edades."""
        return self.censo_dao.obtener_todas_las_edades()