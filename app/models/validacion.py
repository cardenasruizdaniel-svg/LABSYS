"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-014
Archivo: app/models/validacion.py

Modelo de validación técnica y biomédica de resultados.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Validacion(BaseModel):
    __tablename__ = "validaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    procesamiento_id: Mapped[int] = mapped_column(
        ForeignKey("procesamientos.id"),
        nullable=False,
        index=True,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        default="PENDIENTE",
        nullable=False,
    )

    validador: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
    )

    validador_id: Mapped[Optional[int]] = mapped_column(ForeignKey("medicos.id"), nullable=True)

    observaciones: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    fecha_validacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
