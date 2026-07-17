"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-010
Archivo: app/repositories/convenio_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.convenio import Convenio


class ConvenioRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Convenio]:
        stmt = select(Convenio).order_by(Convenio.nombre)
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, convenio_id: int) -> Optional[Convenio]:
        return self.db.get(Convenio, convenio_id)

    def obtener_por_codigo(self, codigo: str) -> Optional[Convenio]:
        stmt = select(Convenio).where(Convenio.codigo == codigo)
        return self.db.scalar(stmt)

    def crear(self, convenio: Convenio) -> Convenio:
        self.db.add(convenio)
        self.db.commit()
        self.db.refresh(convenio)
        return convenio

    def actualizar(self, convenio: Convenio) -> Convenio:
        self.db.commit()
        self.db.refresh(convenio)
        return convenio

    def desactivar(self, convenio: Convenio) -> Convenio:
        convenio.activo = False
        self.db.commit()
        self.db.refresh(convenio)
        return convenio
