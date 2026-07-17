"""
LABSYS DIALIZAR
Módulo: Procesar y Validar
Archivo: app/schemas/parametro_examen.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ParametroExamenCrear(BaseModel):
    examen_id: int
    nombre: str
    unidad: Optional[str] = None
    valor_referencia: Optional[str] = None
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    tipo: str = "NUMERICO"
    opciones: Optional[str] = None
    orden: int = 0


class ParametroExamenActualizar(BaseModel):
    nombre: Optional[str] = None
    unidad: Optional[str] = None
    valor_referencia: Optional[str] = None
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    tipo: Optional[str] = None
    opciones: Optional[str] = None
    orden: Optional[int] = None


class ParametroExamenRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    examen_id: int
    nombre: str
    unidad: Optional[str] = None
    valor_referencia: Optional[str] = None
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    tipo: str
    opciones: Optional[str] = None
    orden: int
    fecha_creacion: datetime
