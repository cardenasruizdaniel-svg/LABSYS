"""
LABSYS DIALIZAR
Módulo: Inventario
Archivo: app/models/movimiento_inventario.py

Kárdex de movimientos de cada ítem: cada entrada/salida/ajuste queda
registrado aquí, y es lo único que modifica el stock_actual del
ítem (a través del servicio, nunca directamente).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class MovimientoInventario(BaseModel):
    __tablename__ = "movimientos_inventario"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    item_id: Mapped[int] = mapped_column(
        ForeignKey("items_inventario.id"), nullable=False, index=True
    )

    # ENTRADA, SALIDA, AJUSTE
    tipo_movimiento: Mapped[str] = mapped_column(String(20), nullable=False)

    cantidad: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    stock_resultante: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    motivo: Mapped[str] = mapped_column(String(150), nullable=False)
    responsable: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Costo real de una entrada por compra (opcional). Se usa para que
    # las compras de insumos/papelería/aseo salgan reflejadas como
    # salida de dinero en el reporte de caja.
    costo_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    fecha_movimiento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
