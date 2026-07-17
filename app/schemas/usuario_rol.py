
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-005
Archivo: app/schemas/usuario_rol.py
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UsuarioRolCrear(BaseModel):
    usuario_id: int
    rol_id: int


class UsuarioRolRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    rol_id: int
    fecha_creacion: datetime
