"""
LABSYS DIALIZAR
Módulo: Seguridad
Archivo: app/security/sesion.py

Define la sesión real del usuario (antes el login generaba un token
que nunca se guardaba en ningún lado, así que cualquiera podía entrar
a cualquier pantalla escribiendo la URL). Ahora:

  - El login deja la sesión en una cookie httponly.
  - Cada página valida esa cookie y sabe qué MÓDULOS puede ver el
    usuario, según los roles que tenga asignados.

El "módulo" es el mismo campo `modulo` que ya existía en Permiso,
pero aquí se usa a nivel de página completa (ej. "Facturacion"),
no de acción específica. Es una malla más simple y más fácil de
mantener que permisos CRUD finísimos, y coincide con cómo el
laboratorio realmente piensa los accesos (por pantalla).
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.permiso import Permiso
from app.models.rol_permiso import RolPermiso
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.security.jwt import validar_token

NOMBRE_COOKIE = "labsys_sesion"

# Modulos que el rol "Administrador" recibe automaticamente (todos).
TODOS_LOS_MODULOS = [
    "Dashboard", "Pacientes", "Profesionales", "Ordenes", "Examenes",
    "EPS", "Convenios", "Agenda", "ProcesarValidar",
    "Facturacion", "Inventario",
    "Reportes", "Configuracion", "Usuarios", "Geografia",
]


class UsuarioSesion:
    def __init__(self, usuario: Usuario, roles: list[str], modulos: set[str]):
        self.usuario = usuario
        self.roles = roles
        self.modulos = modulos

    def puede(self, modulo: str) -> bool:
        return modulo in self.modulos


def _cargar_sesion(request: Request, db: Session) -> Optional[UsuarioSesion]:
    token = request.cookies.get(NOMBRE_COOKIE)
    if not token:
        return None

    payload = validar_token(token)
    if payload is None:
        return None

    usuario_id = payload.get("user_id")
    if usuario_id is None:
        return None

    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        return None

    rol_ids = [
        ur.rol_id
        for ur in db.query(UsuarioRol).filter(UsuarioRol.usuario_id == usuario.id).all()
    ]

    if not rol_ids:
        return UsuarioSesion(usuario, [], set())

    from app.models.rol import Rol
    roles = db.query(Rol).filter(Rol.id.in_(rol_ids), Rol.activo == True).all()  # noqa: E712
    nombres_roles = [r.nombre for r in roles]

    modulos: set[str] = set()
    if any(r.nombre == "Administrador" for r in roles):
        modulos.update(TODOS_LOS_MODULOS)
    else:
        permiso_ids = [
            rp.permiso_id
            for rp in db.query(RolPermiso).filter(RolPermiso.rol_id.in_(rol_ids)).all()
        ]
        if permiso_ids:
            permisos = db.query(Permiso).filter(Permiso.id.in_(permiso_ids)).all()
            modulos.update(p.modulo for p in permisos)

    return UsuarioSesion(usuario, nombres_roles, modulos)


class RedireccionRequerida(Exception):
    def __init__(self, url: str):
        self.url = url


def usuario_actual_opcional(request: Request, db: Session = Depends(get_db)) -> Optional[UsuarioSesion]:
    """Para endpoints que quieren saber quién es el usuario, sin exigirlo."""
    return _cargar_sesion(request, db)


def usuario_actual(request: Request, db: Session = Depends(get_db)) -> UsuarioSesion:
    """Exige sesión activa. Lanza 401 si no hay usuario logueado."""
    sesion = _cargar_sesion(request, db)
    if sesion is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Debe iniciar sesión.")
    return sesion


def requerir_modulo(modulo: str):
    """
    Fabrica una dependencia de FastAPI para una pagina web: exige
    sesion iniciada y acceso al modulo indicado. Si falta cualquiera
    de las dos cosas, lanza RedireccionRequerida (ver el manejador
    global registrado en app/main.py) en vez de tumbar la app.
    """

    def dependencia(request: Request, db: Session = Depends(get_db)):
        sesion = _cargar_sesion(request, db)

        if sesion is None:
            raise RedireccionRequerida(f"/login?siguiente={request.url.path}")

        if not sesion.puede(modulo):
            raise RedireccionRequerida("/sin-acceso")

        return sesion

    return dependencia
