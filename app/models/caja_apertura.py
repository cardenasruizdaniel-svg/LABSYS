"""
LABSYS DIALIZAR
Módulo: Facturación / Caja
Archivo: app/models/caja_apertura.py
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class CajaApertura(BaseModel):
    __tablename__ = "caja_aperturas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    monto_inicial: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    # ABIERTA o CERRADA
    estado: Mapped[str] = mapped_column(String(20), default="ABIERTA", nullable=False)

    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    fecha_apertura: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
