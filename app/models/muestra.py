"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-012
Archivo: app/models/muestra.py

Modelo de toma y trazabilidad de muestras.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Muestra(BaseModel):
    __tablename__ = "muestras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    orden_id: Mapped[int] = mapped_column(
        ForeignKey("ordenes.id"),
        nullable=False,
        index=True,
    )

    orden_examen_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orden_examenes.id"),
        nullable=True,
        index=True,
    )

    codigo_barras: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    tipo_muestra: Mapped[str] = mapped_column(String(50), nullable=False)
    recipiente: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    estado: Mapped[str] = mapped_column(
        String(30),
        default="PENDIENTE",
        nullable=False,
    )

    responsable_toma: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
    )

    fecha_toma: Mapped[datetime] = mapped_column(
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
