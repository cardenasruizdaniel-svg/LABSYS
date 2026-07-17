"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-013
Archivo: app/schemas/procesamiento.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProcesamientoCrear(BaseModel):
    muestra_id: int
    analizador: str
    profesional_id: Optional[int] = None
    profesional: Optional[str] = None
    observaciones: Optional[str] = None


class ProcesamientoActualizar(BaseModel):
    estado: str
    profesional: Optional[str] = None
    fecha_fin: Optional[datetime] = None
    observaciones: Optional[str] = None


class ProcesamientoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    muestra_id: int
    analizador: str
    profesional: Optional[str] = None
    profesional_id: Optional[int] = None
    estado: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    observaciones: Optional[str] = None
