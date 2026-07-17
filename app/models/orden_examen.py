"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Archivo: app/models/orden_examen.py

Detalle de una orden: qué exámenes del catálogo se solicitaron.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class OrdenExamen(BaseModel):
    __tablename__ = "orden_examenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    orden_id: Mapped[int] = mapped_column(
        ForeignKey("ordenes.id"), nullable=False, index=True
    )
    examen_id: Mapped[int] = mapped_column(
        ForeignKey("examenes.id"), nullable=False, index=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
