"""
LABSYS DIALIZAR
Módulo: Gastos
Archivo: app/models/gasto.py
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Gasto(BaseModel):
    __tablename__ = "gastos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    categoria: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    descripcion: Mapped[str] = mapped_column(String(300), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    proveedor: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    fecha_gasto: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
