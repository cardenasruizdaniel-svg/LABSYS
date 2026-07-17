"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-009
Archivo: app/repositories/eps_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.eps import EPS


class EPSRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[EPS]:
        stmt = select(EPS).order_by(EPS.nombre)
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, eps_id: int) -> Optional[EPS]:
        return self.db.get(EPS, eps_id)

    def obtener_por_codigo(self, codigo: str) -> Optional[EPS]:
        stmt = select(EPS).where(EPS.codigo == codigo)
        return self.db.scalar(stmt)

    def crear(self, eps: EPS) -> EPS:
        self.db.add(eps)
        self.db.commit()
        self.db.refresh(eps)
        return eps

    def actualizar(self, eps: EPS) -> EPS:
        self.db.commit()
        self.db.refresh(eps)
        return eps

    def desactivar(self, eps: EPS) -> EPS:
        eps.activo = False
        self.db.commit()
        self.db.refresh(eps)
        return eps
