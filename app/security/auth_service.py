"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-002
Archivo: app/security/auth_service.py
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.usuario_repository import UsuarioRepository
from app.security.password import verificar_password


class AuthService:
    """Servicio de autenticación."""

    def __init__(self, db: Session):
        self.repository = UsuarioRepository(db)

    def autenticar(self, usuario: str, password: str):
        entidad = self.repository.obtener_por_usuario(usuario)

        if entidad is None:
            return None

        if not entidad.activo:
            return None

        if not verificar_password(password, entidad.password_hash):
            return None

        return entidad
