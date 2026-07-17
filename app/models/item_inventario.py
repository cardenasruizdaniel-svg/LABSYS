"""
LABSYS DIALIZAR
Módulo: Inventario
Archivo: app/models/item_inventario.py

Catálogo de reactivos, insumos y demás elementos que el laboratorio
controla en existencias. El stock_actual se mantiene siempre
actualizado a través de los movimientos de inventario (entradas,
salidas, ajustes); no se edita directamente.
"""

from __future__ import annotations

from datetime import date as date_, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ItemInventario(BaseModel):
    __tablename__ = "items_inventario"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    # REACTIVO, INSUMO, EQUIPO, OTRO
    categoria: Mapped[str] = mapped_column(String(30), default="INSUMO", nullable=False)

    unidad_medida: Mapped[str] = mapped_column(String(20), nullable=False)

    stock_actual: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    stock_minimo: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    precio_unitario: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    proveedor: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    fecha_vencimiento: Mapped[Optional[date_]] = mapped_column(Date, nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
