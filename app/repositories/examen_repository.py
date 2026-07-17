"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Archivo: app/repositories/examen_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.examen import Examen


class ExamenRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Examen]:
        stmt = select(Examen).order_by(Examen.nombre)
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, examen_id: int) -> Optional[Examen]:
        return self.db.get(Examen, examen_id)

    def obtener_por_codigo(self, codigo: str) -> Optional[Examen]:
        stmt = select(Examen).where(Examen.codigo == codigo)
        return self.db.scalar(stmt)

    def crear(self, examen: Examen) -> Examen:
        self.db.add(examen)
        self.db.commit()
        self.db.refresh(examen)
        return examen

    def actualizar(self, examen: Examen) -> Examen:
        self.db.commit()
        self.db.refresh(examen)
        return examen
