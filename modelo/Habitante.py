from .Base import Base
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

class Habitante(Base):
    """
    Registra a cada individuo y es dependiente de la vivienda en la que reside

    Atributos:
        id: (PK)
        vivienda_id: (FK -> Vivienda)
        nombre_completo: [str]
        edad: [int]
        sexo: [str]
        fecha_nacimiento: [date]
        parentesco_con_jefe_familia: (Define el vinculo con el jefe de familia) [str]

        nivel_educativo (puede no venir)

    Relaciones:
        Vivienda:
            Cumple:
                Vincula a la persona con su domicilio

    """

    __tablename__='habitante'
    __table_args__={'extend_existing':True}

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    edad: Mapped[int] = mapped_column(Integer, nullable=False)
    sexo: Mapped[str] = mapped_column(String(10))
    parentesco_con_jefe_familia: Mapped[str] = mapped_column(String(50))

    # Clave foranea
    vivienda_id: Mapped[int] = mapped_column(ForeignKey('vivienda.id', ondelete="CASCADE"))

    # Relacion: Un Habitante pertenece a una Vivienda
    vivienda: Mapped["Vivienda"] = relationship(back_populates="habitantes")