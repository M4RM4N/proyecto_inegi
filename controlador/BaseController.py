from dao import BaseDAO, AdministradorDAO, MunicipioDAO, LocalidadDAO, TipoViviendaDAO, ActividadEconomicaDAO, CensoDAO
from .CensoFactory import CensoFactory

class BaseController:
    """
    Clase base para todos los controladores. Inicializa DAOs y el Factory
    """

    def __init__(self, engine):
        self.admin_dao = AdministradorDAO(engine)
        self.municipio_dao = MunicipioDAO(engine)
        self.localidad_dao = LocalidadDAO(engine)
        self.tipo_vivienda_dao = TipoViviendaDAO(engine)
        self.actividad_dao = ActividadEconomicaDAO(engine)
        self.censo_dao = CensoDAO(engine)

        self.factory = CensoFactory()