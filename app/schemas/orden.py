"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-011
Archivo: app/schemas/orden.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrdenCrear(BaseModel):
    paciente_id: int
    medico_id: int
    eps_id: int
    convenio_id: int
    prioridad: str = "NORMAL"
    observaciones: Optional[str] = None
    examenes_ids: list[int] = []


class OrdenActualizar(BaseModel):
    estado: str
    prioridad: str
    observaciones: Optional[str] = None


class OrdenRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_orden: str
    paciente_id: int
    medico_id: int
    eps_id: int
    convenio_id: int
    estado: str
    prioridad: str
    observaciones: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
