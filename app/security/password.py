"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-002
Archivo: app/security/password.py

Gestión segura de contraseñas utilizando bcrypt.
"""

from passlib.context import CryptContext

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def generar_hash(password: str) -> str:
    """
    Genera el hash seguro de una contraseña.
    """
    return _pwd_context.hash(password)


def verificar_password(password_plano: str, password_hash: str) -> bool:
    """
    Verifica una contraseña en texto plano contra su hash.
    """
    return _pwd_context.verify(password_plano, password_hash)
