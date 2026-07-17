"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Archivo: app/schemas/examen.py
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ExamenCrear(BaseModel):
    codigo: str
    nombre: str
    categoria: Optional[str] = None
    precio: Decimal = Decimal("0.00")
    tipo_muestra: Optional[str] = None
    recipiente: Optional[str] = None


class ExamenActualizar(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    precio: Optional[Decimal] = None
    tipo_muestra: Optional[str] = None
    recipiente: Optional[str] = None
    activo: Optional[bool] = None


class ExamenRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    categoria: Optional[str] = None
    precio: Decimal
    tipo_muestra: Optional[str] = None
    recipiente: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class ExamenOrdenExamenRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    orden_examen_id: int
    id: int
    codigo: str
    nombre: str
    categoria: Optional[str] = None
    precio: Decimal
    tipo_muestra: Optional[str] = None
    recipiente: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
