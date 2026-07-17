"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-012
Archivo: app/repositories/muestra_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.muestra import Muestra


class MuestraRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Muestra]:
        stmt = select(Muestra).order_by(Muestra.fecha_toma.desc())
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, muestra_id: int) -> Optional[Muestra]:
        return self.db.get(Muestra, muestra_id)

    def obtener_por_codigo_barras(self, codigo_barras: str) -> Optional[Muestra]:
        stmt = select(Muestra).where(Muestra.codigo_barras == codigo_barras)
        return self.db.scalar(stmt)

    def listar_por_orden(self, orden_id: int) -> list[Muestra]:
        stmt = select(Muestra).where(Muestra.orden_id == orden_id)
        return list(self.db.scalars(stmt).all())

    def crear(self, muestra: Muestra) -> Muestra:
        self.db.add(muestra)
        self.db.commit()
        self.db.refresh(muestra)
        return muestra

    def actualizar(self, muestra: Muestra) -> Muestra:
        self.db.commit()
        self.db.refresh(muestra)
        return muestra
