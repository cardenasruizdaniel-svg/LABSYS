"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-015
Archivo: app/schemas/resultado.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ResultadoCrear(BaseModel):
    validacion_id: int
    examen: str
    examen_codigo: Optional[str] = None
    resultado: Optional[str] = None
    valor_numerico: Optional[float] = None
    unidad: Optional[str] = None
    valor_referencia: Optional[str] = None
    critico: bool = False


class ResultadoActualizar(BaseModel):
    resultado: Optional[str] = None
    valor_numerico: Optional[float] = None
    unidad: Optional[str] = None
    valor_referencia: Optional[str] = None
    critico: bool = False


class ResultadoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    validacion_id: int
    examen: str
    examen_codigo: Optional[str] = None
    resultado: Optional[str]
    valor_numerico: Optional[float]
    unidad: Optional[str]
    valor_referencia: Optional[str]
    critico: bool
    fecha_creacion: datetime
