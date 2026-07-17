"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-013
Archivo: app/models/procesamiento.py

Modelo de procesamiento analítico de muestras.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Procesamiento(BaseModel):
    __tablename__ = "procesamientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    muestra_id: Mapped[int] = mapped_column(
        ForeignKey("muestras.id"),
        nullable=False,
        index=True,
    )

    analizador: Mapped[str] = mapped_column(String(120), nullable=False)
    profesional: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    profesional_id: Mapped[Optional[int]] = mapped_column(ForeignKey("medicos.id"), nullable=True)

    estado: Mapped[str] = mapped_column(
        String(30),
        default="EN_PROCESO",
        nullable=False,
    )

    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    fecha_fin: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    observaciones: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
