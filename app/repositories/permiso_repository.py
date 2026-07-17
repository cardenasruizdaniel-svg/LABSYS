
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-004
Archivo: app/repositories/permiso_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.permiso import Permiso


class PermisoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Permiso]:
        stmt = select(Permiso).order_by(Permiso.modulo, Permiso.nombre)
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, permiso_id: int) -> Optional[Permiso]:
        return self.db.get(Permiso, permiso_id)

    def obtener_por_codigo(self, codigo: str) -> Optional[Permiso]:
        stmt = select(Permiso).where(Permiso.codigo == codigo)
        return self.db.scalar(stmt)

    def crear(self, permiso: Permiso) -> Permiso:
        self.db.add(permiso)
        self.db.commit()
        self.db.refresh(permiso)
        return permiso

    def actualizar(self, permiso: Permiso) -> Permiso:
        self.db.commit()
        self.db.refresh(permiso)
        return permiso

    def desactivar(self, permiso: Permiso) -> Permiso:
        permiso.activo = False
        self.db.commit()
        self.db.refresh(permiso)
        return permiso
