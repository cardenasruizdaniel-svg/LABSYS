
"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-007
Archivo: app/models/paciente.py

Modelo principal de pacientes.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Paciente(BaseModel):
    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    tipo_documento: Mapped[str] = mapped_column(String(10), nullable=False)
    documento: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)

    primer_nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    segundo_nombre: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    primer_apellido: Mapped[str] = mapped_column(String(80), nullable=False)
    segundo_apellido: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    sexo: Mapped[str] = mapped_column(String(20), nullable=False)

    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    celular: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    correo: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    direccion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    municipio: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    departamento: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Afiliación: si es_particular=True, paga directo (sin EPS) y
    # normalmente tiene_copago tambien sera True (paga el 100%).
    # Si tiene EPS, tiene_copago indica si esa EPS le exige copago o no.
    es_particular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    eps_id: Mapped[Optional[int]] = mapped_column(ForeignKey("eps.id"), nullable=True)
    tiene_copago: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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
