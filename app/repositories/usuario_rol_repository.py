
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-005
Archivo: app/repositories/usuario_rol_repository.py
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario_rol import UsuarioRol


class UsuarioRolRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[UsuarioRol]:
        stmt = select(UsuarioRol).order_by(UsuarioRol.usuario_id, UsuarioRol.rol_id)
        return list(self.db.scalars(stmt).all())

    def listar_por_usuario(self, usuario_id: int) -> list[UsuarioRol]:
        stmt = select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        return list(self.db.scalars(stmt).all())

    def obtener(self, usuario_id: int, rol_id: int):
        stmt = select(UsuarioRol).where(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.rol_id == rol_id,
        )
        return self.db.scalar(stmt)

    def crear(self, relacion: UsuarioRol) -> UsuarioRol:
        self.db.add(relacion)
        self.db.commit()
        self.db.refresh(relacion)
        return relacion

    def eliminar(self, relacion: UsuarioRol) -> None:
        self.db.delete(relacion)
        self.db.commit()
