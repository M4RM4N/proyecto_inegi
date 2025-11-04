from .Base import Base
from typing import List
from sqlalchemy import String 
from sqlalchemy.orm import relationship, Mapped, mapped_column

class Municipio(Base):
    # Esta clase requerira la funcionalidad CRUD
    """
    Catalogo de municipios

    Atributos:
        id: (PK)
        nombre: [str]

    Relaciones:
        One-to-Many: Hacia Localidad (un municipio tiene muchas localidades)
    """
    
    __tablename__ = 'municipio'
    __table_args__ = {'extend_existing':True}

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relacion: Un municipio tiene muchas localidades
    localidades: Mapped[List["Localidad"]] = relationship(back_populates="municipio", cascade="all, delete-orphan")