"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Archivo: app/models/examen.py

Catálogo de exámenes que el laboratorio ofrece. Se usa para
seleccionar qué exámenes se solicitan en cada Orden.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Examen(BaseModel):
    __tablename__ = "examenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    # Área o categoría del examen (Hematología, Química, Microbiología, etc.)
    categoria: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    tipo_muestra: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    recipiente: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
