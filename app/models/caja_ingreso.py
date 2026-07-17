"""
LABSYS DIALIZAR
Módulo: Facturación / Caja
Archivo: app/models/caja_ingreso.py

Ingresos manuales a la caja (aportes de dinero cuando no hay
suficiente efectivo para cubrir compras o gastos).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class CajaIngreso(BaseModel):
    __tablename__ = "caja_ingresos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    apertura_id: Mapped[int] = mapped_column(
        ForeignKey("caja_aperturas.id"), nullable=False, index=True
    )

    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    origen: Mapped[str] = mapped_column(String(120), nullable=False)

    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    usuario_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True
    )

    fecha_ingreso: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
