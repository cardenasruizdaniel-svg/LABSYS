"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-015
Archivo: app/models/resultado.py
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Resultado(BaseModel):
    __tablename__ = "resultados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    validacion_id: Mapped[int] = mapped_column(ForeignKey("validaciones.id"), index=True)

    examen: Mapped[str] = mapped_column(String(150), nullable=False)
    examen_codigo: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    resultado: Mapped[Optional[str]] = mapped_column(String(255))
    valor_numerico: Mapped[Optional[float]] = mapped_column(Numeric(10,2))
    unidad: Mapped[Optional[str]] = mapped_column(String(30))
    valor_referencia: Mapped[Optional[str]] = mapped_column(String(120))
    critico: Mapped[bool] = mapped_column(Boolean, default=False)

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
