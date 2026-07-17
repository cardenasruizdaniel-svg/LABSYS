"""
LABSYS DIALIZAR
Modulo: Seguridad
Historia: HU-002
Archivo: app/security/jwt.py
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config.settings import settings

ACCESS_TOKEN_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def crear_token_acceso(data: dict[str, Any], expires_minutes: int = ACCESS_TOKEN_MINUTES) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def validar_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
