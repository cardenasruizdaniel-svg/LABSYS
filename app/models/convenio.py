"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-010
Archivo: app/models/convenio.py

Modelo de convenios entre el laboratorio y las EPS.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Convenio(BaseModel):
    __tablename__ = "convenios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    eps_id: Mapped[int] = mapped_column(
        ForeignKey("eps.id"),
        nullable=False,
        index=True,
    )

    codigo: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    observaciones: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Configuración de copago aplicable a las facturas de este convenio.
    # NINGUNO: el convenio cubre el 100% (ej. régimen subsidiado sin copago).
    # FIJO: el paciente paga un valor fijo (cuota moderadora) por factura.
    # PORCENTAJE: el paciente paga un porcentaje del total de la factura.
    tipo_copago: Mapped[str] = mapped_column(
        String(20),
        default="NINGUNO",
        nullable=False,
    )

    valor_copago: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
