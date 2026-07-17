
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-003
Archivo: app/schemas/rol.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RolCrear(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RolActualizar(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: bool


class RolRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
