"""
LABSYS DIALIZAR
Módulo: Procesar y Validar
Archivo: app/models/parametro_examen.py

Define los campos pre-diseñados para cada examen del catálogo.
Permite generar formularios de resultado automáticos según el tipo
de examen, de modo que el bacteriólogo solo ingrese los valores.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ParametroExamen(BaseModel):
    __tablename__ = "parametros_examen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    examen_id: Mapped[int] = mapped_column(
        ForeignKey("examenes.id"),
        nullable=False,
        index=True,
    )

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    unidad: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    valor_referencia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    valor_minimo: Mapped[Optional[float]] = mapped_column(nullable=True)

    valor_maximo: Mapped[Optional[float]] = mapped_column(nullable=True)

    tipo: Mapped[str] = mapped_column(
        String(20),
        default="NUMERICO",
        nullable=False,
    )

    opciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

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
