"""
LABSYS DIALIZAR
Modulo: Seguridad
Historia: HU-002
Archivo: app/routers/login.py
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.auth_service import AuthService
from app.security.jwt import crear_token_acceso
from app.security.sesion import NOMBRE_COOKIE, UsuarioSesion, usuario_actual_opcional

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


class LoginRequest(BaseModel):
    usuario: str
    password: str


@router.post("/login")
def login(datos: LoginRequest, response: Response, db: Session = Depends(get_db)):
    servicio = AuthService(db)
    usuario = servicio.autenticar(datos.usuario, datos.password)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    token = crear_token_acceso(
        {
            "sub": usuario.usuario,
            "user_id": usuario.id,
        }
    )

    # La sesion real queda en una cookie httponly: el navegador la manda
    # sola en cada peticion siguiente, y el usuario no puede leerla ni
    # modificarla desde JavaScript.
    response.set_cookie(
        key=NOMBRE_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 8,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.usuario,
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(NOMBRE_COOKIE)
    return {"success": True}


@router.get("/me")
def quien_soy(sesion: UsuarioSesion | None = Depends(usuario_actual_opcional)):
    if sesion is None:
        raise HTTPException(status_code=401, detail="No hay sesión activa")

    return {
        "user_id": sesion.usuario.id,
        "usuario": sesion.usuario.usuario,
        "nombres": sesion.usuario.nombres,
        "apellidos": sesion.usuario.apellidos,
        "roles": sesion.roles,
        "modulos": sorted(sesion.modulos),
        "acceso_movil": getattr(sesion.usuario, "acceso_movil", False),
    }


@router.post("/mobile-login")
def mobile_login(datos: LoginRequest, response: Response, db: Session = Depends(get_db)):
    servicio = AuthService(db)
    usuario = servicio.autenticar(datos.usuario, datos.password)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    if not getattr(usuario, "acceso_movil", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a la aplicación móvil. Contacte al administrador.",
        )

    token = crear_token_acceso(
        {
            "sub": usuario.usuario,
            "user_id": usuario.id,
        }
    )

    response.set_cookie(
        key=NOMBRE_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 8,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.usuario,
    }
