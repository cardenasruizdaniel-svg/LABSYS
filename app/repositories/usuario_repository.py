"""
LABSYS DIALIZAR
Módulo: Usuarios
Archivo: app/repositories/usuario_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Usuario]:
        stmt = select(Usuario).order_by(Usuario.apellidos, Usuario.nombres)
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.get(Usuario, usuario_id)

    def obtener_por_usuario(self, usuario: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.usuario == usuario)
        return self.db.scalar(stmt)

    def obtener_por_documento(self, documento: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.documento == documento)
        return self.db.scalar(stmt)

    def crear(self, entidad: Usuario) -> Usuario:
        self.db.add(entidad)
        self.db.commit()
        self.db.refresh(entidad)
        return entidad

    def actualizar(self, entidad: Usuario) -> Usuario:
        self.db.commit()
        self.db.refresh(entidad)
        return entidad

    def desactivar(self, entidad: Usuario) -> Usuario:
        entidad.activo = False
        self.db.commit()
        self.db.refresh(entidad)
        return entidad
