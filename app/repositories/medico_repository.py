"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-008
Archivo: app/repositories/medico_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.medico import Medico


class MedicoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Medico]:
        stmt = select(Medico).order_by(Medico.apellidos, Medico.nombres)
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, medico_id: int) -> Optional[Medico]:
        return self.db.get(Medico, medico_id)

    def obtener_por_registro(self, registro_medico: str) -> Optional[Medico]:
        stmt = select(Medico).where(Medico.registro_medico == registro_medico)
        return self.db.scalar(stmt)

    def crear(self, medico: Medico) -> Medico:
        self.db.add(medico)
        self.db.commit()
        self.db.refresh(medico)
        return medico

    def actualizar(self, medico: Medico) -> Medico:
        self.db.commit()
        self.db.refresh(medico)
        return medico

    def desactivar(self, medico: Medico) -> Medico:
        medico.activo = False
        self.db.commit()
        self.db.refresh(medico)
        return medico
