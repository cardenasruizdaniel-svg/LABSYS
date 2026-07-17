
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-006
Archivo: app/schemas/rol_permiso.py
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RolPermisoCrear(BaseModel):
    rol_id: int
    permiso_id: int


class RolPermisoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rol_id: int
    permiso_id: int
    fecha_creacion: datetime
