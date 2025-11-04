from .Base import Base, vivienda_actividad
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column

class ActividadEconomica(Base):
    # Esta clase requerira la funcionalidad CRUD
    """
    Sosten economico de la vivienda

    Atributos:
        id: (PK)
        nombre: [str]

    Relaciones:
        Many-to-Many: Hacia vivienda (via tabla de asosiación)
    """

    __tablename__='actividad_economica'
    __table_args__={'extend_existing':True}

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relacion Many-to-Many (M:M)
    viviendas: Mapped[List["Vivienda"]] = relationship(
        secondary=vivienda_actividad,
        back_populates="actividades"
    )