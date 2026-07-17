"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-008
Archivo: app/models/medico.py

Modelo de médicos solicitantes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Medico(BaseModel):
    __tablename__ = "medicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    registro_medico: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    # MEDICO o ENFERMERO: permite reutilizar este mismo catálogo tanto
    # para el médico remitente de una orden como para el profesional
    # que toma la muestra (enfermera/o).
    tipo_profesional: Mapped[str] = mapped_column(
        String(20), default="MEDICO", nullable=False
    )

    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)

    especialidad: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    correo: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Ruta relativa dentro de /static (ej: "firmas/firma_xxxx.png"),
    # usada para estampar la firma en los resultados que valide.
    firma_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

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
