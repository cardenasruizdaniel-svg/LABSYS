"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-016
Archivo: app/models/factura.py
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Factura(BaseModel):
    __tablename__ = "facturas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numero: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), index=True)
    convenio_id: Mapped[int] = mapped_column(ForeignKey("convenios.id"), index=True)

    estado: Mapped[str] = mapped_column(String(30), default="BORRADOR")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    impuestos: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)

    # Copago: parte del total que le corresponde pagar al paciente,
    # calculado a partir de la configuración del convenio (tipo_copago /
    # valor_copago). El resto lo cubre la EPS / el convenio.
    valor_copago: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    valor_cubierto_convenio: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    copago_pagado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_pago_copago: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    fecha_emision: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
