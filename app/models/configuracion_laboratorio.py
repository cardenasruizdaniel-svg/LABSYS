"""
LABSYS DIALIZAR
Módulo: Configuración
Archivo: app/models/configuracion_laboratorio.py

Tabla de un solo registro (id=1) con los datos del laboratorio que
se usan como membrete/pie de página en los PDF de resultados,
facturas y demás documentos imprimibles.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ConfiguracionLaboratorio(BaseModel):
    __tablename__ = "configuracion_laboratorio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    nombre_laboratorio: Mapped[str] = mapped_column(String(200), nullable=False)
    nit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    resolucion_habilitacion: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    direccion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    correo: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    ciudad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Ruta relativa dentro de /static (ej: "uploads/logo.png")
    logo_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    pie_pagina: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    smtp_host: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    smtp_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    smtp_user: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    smtp_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    smtp_from: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
