"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-011
Archivo: app/models/orden.py

Modelo principal de órdenes de laboratorio.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Orden(BaseModel):
    __tablename__ = "ordenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    numero_orden: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("pacientes.id"),
        nullable=False,
        index=True,
    )

    medico_id: Mapped[int] = mapped_column(
        ForeignKey("medicos.id"),
        nullable=False,
        index=True,
    )

    eps_id: Mapped[int] = mapped_column(
        ForeignKey("eps.id"),
        nullable=False,
        index=True,
    )

    convenio_id: Mapped[int] = mapped_column(
        ForeignKey("convenios.id"),
        nullable=False,
        index=True,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        default="REGISTRADA",
        nullable=False,
    )

    prioridad: Mapped[str] = mapped_column(
        String(20),
        default="NORMAL",
        nullable=False,
    )

    observaciones: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
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
