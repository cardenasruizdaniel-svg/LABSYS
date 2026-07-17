"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-014
Archivo: app/schemas/validacion.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ValidacionCrear(BaseModel):
    procesamiento_id: int
    observaciones: Optional[str] = None


class ValidacionActualizar(BaseModel):
    estado: str
    validador: Optional[str] = None
    validador_id: Optional[int] = None
    observaciones: Optional[str] = None
    fecha_validacion: Optional[datetime] = None


class ValidacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    procesamiento_id: int
    estado: str
    validador: Optional[str] = None
    validador_id: Optional[int] = None
    observaciones: Optional[str] = None
    fecha_validacion: Optional[datetime] = None
    fecha_creacion: datetime
