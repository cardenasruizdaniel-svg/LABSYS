"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-012
Archivo: app/schemas/muestra.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MuestraCrear(BaseModel):
    orden_id: int
    orden_examen_id: Optional[int] = None
    codigo_barras: str
    tipo_muestra: str
    recipiente: Optional[str] = None
    responsable_toma: Optional[str] = None


class MuestraActualizar(BaseModel):
    estado: str
    recipiente: Optional[str] = None
    responsable_toma: Optional[str] = None


class MuestraRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    orden_id: int
    orden_examen_id: Optional[int] = None
    codigo_barras: str
    tipo_muestra: str
    recipiente: Optional[str] = None
    estado: str
    responsable_toma: Optional[str] = None
    fecha_toma: datetime
    fecha_actualizacion: datetime
