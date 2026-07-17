"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-013
Archivo: app/repositories/procesamiento_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.procesamiento import Procesamiento


class ProcesamientoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Procesamiento]:
        stmt = select(Procesamiento).order_by(Procesamiento.fecha_inicio.desc())
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, procesamiento_id: int) -> Optional[Procesamiento]:
        return self.db.get(Procesamiento, procesamiento_id)

    def obtener_por_muestra(self, muestra_id: int) -> Optional[Procesamiento]:
        stmt = select(Procesamiento).where(Procesamiento.muestra_id == muestra_id)
        return self.db.scalar(stmt)

    def crear(self, procesamiento: Procesamiento) -> Procesamiento:
        self.db.add(procesamiento)
        self.db.commit()
        self.db.refresh(procesamiento)
        return procesamiento

    def actualizar(self, procesamiento: Procesamiento) -> Procesamiento:
        self.db.commit()
        self.db.refresh(procesamiento)
        return procesamiento
