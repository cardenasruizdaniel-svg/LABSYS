"""
LABSYS DIALIZAR
Módulo: Agenda
Archivo: app/models/cita.py

Modelo de citas para programación de exámenes.
Una cita puede venir de una orden médica ya existente (orden_id)
o puede ser solicitada directamente por el paciente sin orden
previa, en cuyo caso es un examen particular que el paciente
paga directamente (es_particular = True). En ese segundo caso,
la orden puede crearse y asociarse más adelante (por ejemplo
cuando el paciente llega a tomarse la muestra).
"""

from __future__ import annotations

from datetime import date as date_, datetime
from datetime import time as time_
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Cita(BaseModel):
    __tablename__ = "citas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("pacientes.id"),
        nullable=False,
        index=True,
    )

    orden_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ordenes.id"),
        nullable=True,
        index=True,
    )

    medico_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("medicos.id"),
        nullable=True,
        index=True,
    )

    fecha_cita: Mapped[date_] = mapped_column(Date, nullable=False, index=True)

    # Hora deseada de la cita (opcional). El cupo sigue siendo por
    # dia, no por hora: varios pacientes pueden compartir la misma
    # hora sin que el sistema lo bloquee.
    hora_cita: Mapped[Optional[time_]] = mapped_column(Time, nullable=True)

    # CON_ORDEN: el examen viene de una orden médica ya registrada.
    # PARTICULAR: el paciente solicita el examen directamente y lo paga él mismo.
    tipo_atencion: Mapped[str] = mapped_column(
        String(20),
        default="CON_ORDEN",
        nullable=False,
    )

    es_particular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # PROGRAMADA, CONFIRMADA, ATENDIDA, CANCELADA, NO_ASISTIO
    estado: Mapped[str] = mapped_column(
        String(20),
        default="PROGRAMADA",
        nullable=False,
    )

    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

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
