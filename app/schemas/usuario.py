"""
LABSYS DIALIZAR
Módulo: Usuarios
Archivo: app/schemas/usuario.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UsuarioCrear(BaseModel):
    tipo_documento: str
    documento: str
    nombres: str
    apellidos: str
    correo: str
    celular: Optional[str] = None
    cargo: str
    usuario: str
    password: str
    acceso_movil: bool = False


class UsuarioActualizar(BaseModel):
    tipo_documento: str
    documento: str
    nombres: str
    apellidos: str
    correo: str
    celular: Optional[str] = None
    cargo: str
    activo: bool
    acceso_movil: bool = False


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_documento: str
    documento: str
    nombres: str
    apellidos: str
    correo: str
    celular: Optional[str] = None
    cargo: str
    usuario: str
    activo: bool
    acceso_movil: bool = False
    ultimo_acceso: Optional[datetime] = None
