"""
LABSYS DIALIZAR
Módulo: Agenda
Archivo: app/repositories/cita_repository.py
"""

from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cita import Cita


class CitaRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Cita]:
        stmt = select(Cita).order_by(Cita.fecha_cita.desc(), Cita.id.desc())
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, cita_id: int) -> Optional[Cita]:
        return self.db.get(Cita, cita_id)

    def listar_por_fecha(self, fecha: date) -> list[Cita]:
        stmt = select(Cita).where(Cita.fecha_cita == fecha).order_by(Cita.id)
        return list(self.db.scalars(stmt).all())

    def listar_por_paciente(self, paciente_id: int) -> list[Cita]:
        stmt = (
            select(Cita)
            .where(Cita.paciente_id == paciente_id)
            .order_by(Cita.fecha_cita.desc())
        )
        return list(self.db.scalars(stmt).all())

    def contar_activas_por_fecha(self, fecha: date) -> int:
        stmt = select(func.count(Cita.id)).where(
            Cita.fecha_cita == fecha,
            Cita.estado != "CANCELADA",
        )
        return self.db.scalar(stmt) or 0

    def crear(self, cita: Cita) -> Cita:
        self.db.add(cita)
        self.db.commit()
        self.db.refresh(cita)
        return cita

    def actualizar(self, cita: Cita) -> Cita:
        self.db.commit()
        self.db.refresh(cita)
        return cita
