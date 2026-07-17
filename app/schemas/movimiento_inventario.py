"""
LABSYS DIALIZAR
Módulo: Inventario
Archivo: app/schemas/movimiento_inventario.py
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

TIPOS_VALIDOS = {"ENTRADA", "SALIDA", "AJUSTE"}


class MovimientoInventarioCrear(BaseModel):
    item_id: int
    tipo_movimiento: str
    cantidad: Decimal
    motivo: str
    responsable: Optional[str] = None
    observaciones: Optional[str] = None
    costo_total: Optional[Decimal] = None

    @field_validator("tipo_movimiento")
    @classmethod
    def _validar_tipo(cls, v: str) -> str:
        v = v.upper()
        if v not in TIPOS_VALIDOS:
            raise ValueError(f"tipo_movimiento debe ser uno de: {', '.join(sorted(TIPOS_VALIDOS))}")
        return v

    @field_validator("cantidad")
    @classmethod
    def _validar_cantidad(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("La cantidad no puede ser negativa. Use tipo_movimiento para indicar el sentido.")
        return v


class MovimientoInventarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    tipo_movimiento: str
    cantidad: Decimal
    stock_resultante: Decimal
    motivo: str
    responsable: Optional[str] = None
    observaciones: Optional[str] = None
    costo_total: Optional[Decimal] = None
    fecha_movimiento: datetime
