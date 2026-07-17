
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-006
Archivo: app/repositories/rol_permiso_repository.py
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rol_permiso import RolPermiso


class RolPermisoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[RolPermiso]:
        stmt = select(RolPermiso).order_by(RolPermiso.rol_id, RolPermiso.permiso_id)
        return list(self.db.scalars(stmt).all())

    def listar_por_rol(self, rol_id: int) -> list[RolPermiso]:
        stmt = select(RolPermiso).where(RolPermiso.rol_id == rol_id)
        return list(self.db.scalars(stmt).all())

    def obtener(self, rol_id: int, permiso_id: int):
        stmt = select(RolPermiso).where(
            RolPermiso.rol_id == rol_id,
            RolPermiso.permiso_id == permiso_id,
        )
        return self.db.scalar(stmt)

    def crear(self, relacion: RolPermiso) -> RolPermiso:
        self.db.add(relacion)
        self.db.commit()
        self.db.refresh(relacion)
        return relacion

    def eliminar(self, relacion: RolPermiso):
        self.db.delete(relacion)
        self.db.commit()
