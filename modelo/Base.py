from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Table, ForeignKey, Column


class Base(DeclarativeBase):
    pass


# Tabla de Asociación Many-to-Many
# Definida aquí usando Base.metadata y nombres de tablas/columnas como strings
# para evitar importaciones circulares.)
vivienda_actividad = Table(
    'vivienda_actividad',
    Base.metadata,
    Column('vivienda_id', ForeignKey('vivienda.id', ondelete="CASCADE"), primary_key=True),
    Column('actividad_id', ForeignKey('actividad_economica.id', ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)