"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-016
Archivo: app/schemas/factura.py
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FacturaCrear(BaseModel):
    numero: str
    orden_id: int
    convenio_id: int
    subtotal: Decimal = Decimal("0.00")
    impuestos: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")


class FacturaActualizar(BaseModel):
    estado: str
    subtotal: Decimal
    impuestos: Decimal
    total: Decimal


class FacturaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    orden_id: int
    convenio_id: int
    estado: str
    subtotal: Decimal
    impuestos: Decimal
    total: Decimal
    valor_copago: Decimal
    valor_cubierto_convenio: Decimal
    copago_pagado: bool
    fecha_pago_copago: Optional[datetime] = None
    fecha_emision: datetime
    es_particular: bool = False
