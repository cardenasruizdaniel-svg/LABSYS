"""
LABSYS DIALIZAR
Módulo: Gastos
Archivo: app/schemas/gasto.py
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GastoCrear(BaseModel):
    categoria: str
    descripcion: str
    valor: Decimal
    proveedor: Optional[str] = None
    observaciones: Optional[str] = None


class GastoActualizar(BaseModel):
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    valor: Optional[Decimal] = None
    proveedor: Optional[str] = None
    observaciones: Optional[str] = None


class GastoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    categoria: str
    descripcion: str
    valor: Decimal
    proveedor: Optional[str] = None
    usuario_id: Optional[int] = None
    observaciones: Optional[str] = None
    fecha_gasto: datetime
