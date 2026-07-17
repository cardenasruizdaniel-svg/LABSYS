"""
LABSYS DIALIZAR
Módulo: Agenda
Archivo: app/schemas/cita.py
"""

from datetime import date, datetime
from datetime import time as time_
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CitaCrear(BaseModel):
    paciente_id: int
    fecha_cita: date
    hora_cita: Optional[time_] = None
    orden_id: Optional[int] = None
    medico_id: Optional[int] = None
    observaciones: Optional[str] = None


class CitaAsociarOrden(BaseModel):
    orden_id: int


class CitaCambiarEstado(BaseModel):
    estado: str


class CitaActualizar(BaseModel):
    fecha_cita: Optional[date] = None
    hora_cita: Optional[time_] = None
    medico_id: Optional[int] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None


class CitaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
    orden_id: Optional[int] = None
    medico_id: Optional[int] = None
    fecha_cita: date
    hora_cita: Optional[time_] = None
    tipo_atencion: str
    es_particular: bool
    estado: str
    observaciones: Optional[str] = None
    fecha_creacion: datetime


class DisponibilidadRespuesta(BaseModel):
    fecha: date
    cupo_maximo: int
    cupo_usado: int
    cupo_disponible: int
