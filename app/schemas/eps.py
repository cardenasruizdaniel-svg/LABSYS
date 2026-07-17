"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-009
Archivo: app/schemas/eps.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class EPSCrear(BaseModel):
    codigo: str
    nombre: str
    nit: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[str] = None


class EPSActualizar(EPSCrear):
    activo: bool


class EPSRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    nit: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
