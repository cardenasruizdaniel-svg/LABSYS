# ============================================================
# LABSYS DIALIZAR ERP
# Archivo: base.py
# Módulo: Modelos Base
# Descripción:
# Clase base para todos los modelos del sistema.
# ============================================================

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer

from sqlalchemy.sql import func

from app.database.base import Base


class BaseModel(Base):

    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    activo = Column(
        Boolean,
        default=True,
        nullable=False
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )