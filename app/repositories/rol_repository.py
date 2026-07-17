
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-003
Archivo: app/repositories/rol_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rol import Rol


class RolRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Rol]:
        stmt = select(Rol).order_by(Rol.nombre)
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, rol_id: int) -> Optional[Rol]:
        return self.db.get(Rol, rol_id)

    def obtener_por_nombre(self, nombre: str) -> Optional[Rol]:
        stmt = select(Rol).where(Rol.nombre == nombre)
        return self.db.scalar(stmt)

    def crear(self, rol: Rol) -> Rol:
        self.db.add(rol)
        self.db.commit()
        self.db.refresh(rol)
        return rol

    def actualizar(self, rol: Rol) -> Rol:
        self.db.commit()
        self.db.refresh(rol)
        return rol

    def desactivar(self, rol: Rol) -> Rol:
        rol.activo = False
        self.db.commit()
        self.db.refresh(rol)
        return rol
