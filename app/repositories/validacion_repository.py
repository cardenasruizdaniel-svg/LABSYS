"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-014
Archivo: app/repositories/validacion_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.validacion import Validacion


class ValidacionRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Validacion]:
        stmt = select(Validacion).order_by(Validacion.fecha_creacion.desc())
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, validacion_id: int) -> Optional[Validacion]:
        return self.db.get(Validacion, validacion_id)

    def obtener_por_procesamiento(self, procesamiento_id: int) -> Optional[Validacion]:
        stmt = select(Validacion).where(
            Validacion.procesamiento_id == procesamiento_id
        )
        return self.db.scalar(stmt)

    def crear(self, validacion: Validacion) -> Validacion:
        self.db.add(validacion)
        self.db.commit()
        self.db.refresh(validacion)
        return validacion

    def actualizar(self, validacion: Validacion) -> Validacion:
        self.db.commit()
        self.db.refresh(validacion)
        return validacion
