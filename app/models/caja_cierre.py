"""
LABSYS DIALIZAR
Módulo: Facturación / Caja
Archivo: app/models/caja_cierre.py
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class CajaCierre(BaseModel):
    __tablename__ = "caja_cierres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    apertura_id: Mapped[int] = mapped_column(ForeignKey("caja_aperturas.id"), nullable=False, unique=True)

    monto_esperado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    monto_contado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    diferencia: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    total_copagos_cobrados: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_facturado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_compras_inventario: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_gastos: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    denominaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    fecha_cierre: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
