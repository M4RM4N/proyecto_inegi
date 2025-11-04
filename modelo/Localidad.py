from .Base import Base
from typing import List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

class Localidad(Base):
    # Esta clase requerira la funcionalidad CRUD
    """
    Catalogo de localidades

    Atributos:
        id: (PK)
        nombre: [str]
        municipio_id: (FK -> Municipio)

    Relaciones:
        Many-to-One: Hacia municipio
        One-to-Many: hacia Vivienda
    """

    __tablename__='localidad'
    __table_args__={'extend_existing':True}

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    municipio_id: Mapped[int] = mapped_column(ForeignKey('municipio.id', ondelete="CASCADE"))

    # Relaciones
    municipio: Mapped["Municipio"] = relationship(back_populates="localidades")
    viviendas: Mapped[List["Vivienda"]] = relationship(back_populates="localidad", cascade="all, delete-orphan")