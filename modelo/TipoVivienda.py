from .Base import Base
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column

class TipoVivienda(Base):
    # Esta clase requerira la funcionalidad CRUD
    """
    Tipos de casas (ej. Concreto, Adobe, etc.)

    Atributos:
        id: (PK)
        nombre: [str]

    Relaciones:
        NA
    """

    __tablename__ = 'tipo_vivienda'
    __table_args__ = {'extend_existing':True}

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    # Relacion
    viviendas: Mapped[List["Vivienda"]] = relationship(back_populates="tipo_vivienda", cascade="all, delete-orphan")