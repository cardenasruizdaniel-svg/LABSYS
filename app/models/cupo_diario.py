"""
LABSYS DIALIZAR
Módulo: Agenda
Archivo: app/models/cupo_diario.py

Permite configurar (opcionalmente) un cupo máximo de citas distinto
para una fecha específica (ej. un día festivo con menos personal,
o un día con jornada extendida). Si una fecha no tiene registro
aquí, se usa el cupo por defecto definido en la configuración
de la aplicación (settings.CUPO_DIARIO_DEFAULT).
"""

from __future__ import annotations

from datetime import date as date_, datetime

from sqlalchemy import Date, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class CupoDiario(BaseModel):
    __tablename__ = "cupos_diarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    fecha: Mapped[date_] = mapped_column(Date, unique=True, nullable=False, index=True)

    cupo_maximo: Mapped[int] = mapped_column(Integer, nullable=False)

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
