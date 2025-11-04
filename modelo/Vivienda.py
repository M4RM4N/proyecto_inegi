from typing import List
from .Base import Base, vivienda_actividad
from sqlalchemy import ForeignKey, String, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column

class Vivienda(Base):
    """
    Captura los atributos comunes de la vivienda y maneja las relaciones con la ubicacion, 
    el tipo de casa y los habitantes

    Atributos:
        id: (PK)
        direccion: (Calle, numero) [str]
        localidad_id: (FK -> Localidad)
        tipo_vivienda_id: (FK -> TipoVivienda)
        fecha_censo: [str]
        
        coordenadas_gps, total_habitantes (pueden no venir)

    Relaciones:
        Habitantes:
            Cumple:
                Poder saber quienes y cuantos viven por vivienda
        Actividades:
            Cumple:
                Conocer la o las actividades economicas que son el sosten
    """

    __tablename__='vivienda'
    __table_args__={'extend_existing':True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_censo: Mapped[Date] = mapped_column(Date, nullable=True)
    coordenadas_gps: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_habitantes: Mapped[int] = mapped_column(String(50), nullable=True)

    # Claves foraneas
    localidad_id: Mapped[int] = mapped_column(ForeignKey('localidad.id', ondelete="CASCADE"))
    tipo_vivienda_id: Mapped[int] = mapped_column(ForeignKey('tipo_vivienda.id', ondelete="CASCADE"))

    # Relaciones
    localidad: Mapped["Localidad"] = relationship(back_populates="viviendas")
    tipo_vivienda: Mapped["TipoVivienda"] = relationship(back_populates="viviendas")

    # (1:M): Una vivienda tiene muchos habitantes
    habitantes: Mapped[List["Habitante"]] = relationship(back_populates="vivienda", cascade="all, delete-orphan")

    # (M:M): Actividades Economicas
    actividades: Mapped[List["ActividadEconomica"]] = relationship(
        secondary=vivienda_actividad,
        back_populates="viviendas"
    )
