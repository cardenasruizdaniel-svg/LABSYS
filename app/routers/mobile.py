"""
LABSYS DIALIZAR
Módulo: App Móvil
Archivo: app/routers/mobile.py

Rutas para la aplicación móvil (PWA) de Procesar y Validar.
Solo accesible para usuarios con acceso_movil habilitado.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.security.sesion import UsuarioSesion, usuario_actual_opcional

router = APIRouter(tags=["Móvil"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/mobile", response_class=HTMLResponse)
def mobile_home(request: Request):
    return templates.TemplateResponse("mobile/login.html", {"request": request})


@router.get("/mobile/dashboard", response_class=HTMLResponse)
def mobile_dashboard(request: Request, sesion: UsuarioSesion | None = Depends(usuario_actual_opcional)):
    if sesion is None:
        return RedirectResponse(url="/mobile", status_code=302)
    if not getattr(sesion.usuario, "acceso_movil", False):
        return RedirectResponse(url="/mobile?error=acceso", status_code=302)
    return templates.TemplateResponse("mobile/dashboard.html", {"request": request, "sesion": sesion})


@router.get("/mobile/procesar", response_class=HTMLResponse)
def mobile_procesar(request: Request, sesion: UsuarioSesion | None = Depends(usuario_actual_opcional)):
    if sesion is None:
        return RedirectResponse(url="/mobile", status_code=302)
    if not getattr(sesion.usuario, "acceso_movil", False):
        return RedirectResponse(url="/mobile?error=acceso", status_code=302)
    return templates.TemplateResponse("mobile/procesar.html", {"request": request, "sesion": sesion})


@router.get("/mobile/validar", response_class=HTMLResponse)
def mobile_validar(request: Request, sesion: UsuarioSesion | None = Depends(usuario_actual_opcional)):
    if sesion is None:
        return RedirectResponse(url="/mobile", status_code=302)
    if not getattr(sesion.usuario, "acceso_movil", False):
        return RedirectResponse(url="/mobile?error=acceso", status_code=302)
    return templates.TemplateResponse("mobile/validar.html", {"request": request, "sesion": sesion})
