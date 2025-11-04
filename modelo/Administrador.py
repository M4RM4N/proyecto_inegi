from typing import List
from .Base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class Administrador(Base):
    """
    Para el requisito de seguridad y acceso

    Atributos:
        id: (PK),
        usuario: [str]
        contrasena_hash: (Se recomienda almacenar un hash, no la contraseña en texto plano)
    """

    __tablename__ = 'administrador'
    __table_args__ = {'extend_existing': True}


    id: Mapped[int] = mapped_column(primary_key=True)
    usuario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    contrasena_hash: Mapped[str] = mapped_column(String(256), nullable=False)