"""
LABSYS DIALIZAR
Módulo: Catálogos geográficos
Archivo: app/models/ciudad.py
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Ciudad(BaseModel):
    __tablename__ = "ciudades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    departamento_id: Mapped[int] = mapped_column(
        ForeignKey("departamentos.id"), nullable=False, index=True
    )
