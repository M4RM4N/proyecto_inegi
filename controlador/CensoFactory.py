from modelo import Vivienda, Habitante, Localidad, TipoVivienda
from datetime import date
from typing import Dict, Any, Optional

class CensoFactory:
    """
    Implementa el Patrón Factory Method para la creación controlada 
    de entidades de censo (Vivienda y Habitante), aplicando validaciones de inicialización.
    """

    def crear_vivienda(self, 
                       datos: Dict[str, Any], 
                       localidad: Localidad, 
                       tipo_vivienda: TipoVivienda) -> Vivienda:
        """
        Crea y retorna una instancia de Vivienda. 
        Lanza ValueError si faltan datos esenciales para el censo.
        """
        # --- VALIDACIONES DE INTEGRIDAD DE DATOS (Lógica de Factory) ---
        
        direccion = datos.get('direccion')
        if not direccion:
            raise ValueError("La dirección de la vivienda es un dato obligatorio para el censo.")
        
        if not localidad or not tipo_vivienda:
            raise ValueError("Localidad y TipoVivienda deben ser objetos válidos para crear la Vivienda.")
            
        # --- CREACIÓN DEL OBJETO ---
        
        # El Factory asigna valores por defecto y garantiza el estado inicial
        nueva_vivienda = Vivienda(
            direccion=direccion,
            localidad=localidad,          # Asignación de objeto de relación M:1
            tipo_vivienda=tipo_vivienda,  # Asignación de objeto de relación M:1
            fecha_censo=datos.get('fecha_censo', date.today()), # Valor por defecto
            coordenadas_gps=datos.get('coordenadas_gps', None),
            total_habitantes=0 # Siempre inicia en 0 hasta que se registren habitantes
        )
        return nueva_vivienda

    def crear_habitante(self, datos: Dict[str, Any]) -> Habitante:
        """
        Crea y retorna una instancia de Habitante.
        Lanza ValueError si faltan datos esenciales.
        """
        # --- VALIDACIONES DE INTEGRIDAD DE DATOS ---
        
        nombre_completo = datos.get('nombre_completo')
        edad = datos.get('edad')
        sexo = datos.get('sexo')

        if not all([nombre_completo, edad is not None, sexo]):
            raise ValueError("Nombre, edad y sexo son datos esenciales para registrar a un habitante.")
        
        if not isinstance(edad, int) or edad < 0:
            raise ValueError("La edad debe ser un número entero no negativo.")

        # --- CREACIÓN DEL OBJETO ---
        
        nuevo_habitante = Habitante(
            nombre_completo=nombre_completo,
            edad=edad,
            sexo=sexo,
            parentesco_con_jefe_familia=datos.get('parentesco_con_jefe_familia', 'No especificado'),
            # NOTA: La relación 'vivienda' se establece en el CensoController después de la creación.
        )
        return nuevo_habitante