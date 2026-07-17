
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-006
Archivo: app/models/rol_permiso.py

Relación entre roles y permisos.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RolPermiso(BaseModel):
    __tablename__ = "rol_permisos"

    __table_args__ = (
        UniqueConstraint("rol_id", "permiso_id", name="uq_rol_permiso"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    rol_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    permiso_id: Mapped[int] = mapped_column(
        ForeignKey("permisos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
