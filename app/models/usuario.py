"""
LABSYS DIALIZAR
Módulo: Usuarios
Archivo: app/models/usuario.py
SQLAlchemy 2.0
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Usuario(BaseModel):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    tipo_documento: Mapped[str] = mapped_column(String(10), nullable=False)
    documento: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)

    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(120), nullable=False)

    correo: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    celular: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    cargo: Mapped[str] = mapped_column(String(100), nullable=False)

    usuario: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    cambiar_password: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    acceso_movil: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    creado_por: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actualizado_por: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

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
