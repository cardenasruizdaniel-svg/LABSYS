
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-004
Archivo: app/schemas/permiso.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PermisoCrear(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    modulo: str


class PermisoActualizar(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    modulo: str
    activo: bool


class PermisoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    modulo: str
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
