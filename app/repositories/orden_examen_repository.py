"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Archivo: app/repositories/orden_examen_repository.py
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.orden_examen import OrdenExamen


class OrdenExamenRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar_por_orden(self, orden_id: int) -> list[OrdenExamen]:
        stmt = select(OrdenExamen).where(OrdenExamen.orden_id == orden_id)
        return list(self.db.scalars(stmt).all())

    def crear(self, orden_examen: OrdenExamen) -> OrdenExamen:
        self.db.add(orden_examen)
        return orden_examen

    def guardar_cambios(self) -> None:
        self.db.commit()
