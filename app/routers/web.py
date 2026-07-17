from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.security.sesion import requerir_modulo

router = APIRouter(tags=["Web"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def inicio():
    return RedirectResponse("/login")


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request
        }
    )


@router.get("/sin-acceso")
async def sin_acceso(request: Request):
    return templates.TemplateResponse(
        "auth/sin_acceso.html",
        {
            "request": request
        }
    )


@router.get("/dashboard")
async def dashboard(request: Request, sesion=Depends(requerir_modulo("Dashboard"))):
    return templates.TemplateResponse(
        "dashboard/dashboard_ejecutivo.html",
        {
            "request": request,
            "titulo": "Dashboard Ejecutivo",
            "version": "1.0.0"
        }
    )


@router.get("/pacientes")
async def pacientes(request: Request, sesion=Depends(requerir_modulo("Pacientes"))):
    return templates.TemplateResponse(
        "pacientes/lista.html",
        {
            "request": request
        }
    )


@router.get("/ordenes")
async def ordenes(request: Request, sesion=Depends(requerir_modulo("Ordenes"))):
    return templates.TemplateResponse(
        "ordenes/nueva.html",
        {
            "request": request
        }
    )


@router.get("/examenes")
async def examenes(request: Request, sesion=Depends(requerir_modulo("Examenes"))):
    return templates.TemplateResponse(
        "examenes/index.html",
        {
            "request": request
        }
    )


@router.get("/eps")
async def eps(request: Request, sesion=Depends(requerir_modulo("EPS"))):
    return templates.TemplateResponse(
        "eps/index.html",
        {
            "request": request
        }
    )


@router.get("/convenios")
async def convenios(request: Request, sesion=Depends(requerir_modulo("Convenios"))):
    return templates.TemplateResponse(
        "convenios/index.html",
        {
            "request": request
        }
    )


@router.get("/medicos")
async def medicos(request: Request, sesion=Depends(requerir_modulo("Profesionales"))):
    return templates.TemplateResponse(
        "medicos/index.html",
        {
            "request": request
        }
    )


@router.get("/muestras")
async def muestras(request: Request, sesion=Depends(requerir_modulo("Muestras"))):
    return templates.TemplateResponse(
        "muestras/index.html",
        {
            "request": request
        }
    )


@router.get("/procesamientos")
async def procesamientos(request: Request, sesion=Depends(requerir_modulo("Procesamientos"))):
    return templates.TemplateResponse(
        "procesamientos/index.html",
        {
            "request": request
        }
    )


@router.get("/validaciones")
async def validaciones(request: Request, sesion=Depends(requerir_modulo("Validaciones"))):
    return templates.TemplateResponse(
        "validaciones/index.html",
        {
            "request": request
        }
    )


@router.get("/resultados")
async def resultados(request: Request, sesion=Depends(requerir_modulo("Resultados"))):
    return templates.TemplateResponse(
        "resultados/index.html",
        {
            "request": request
        }
    )


@router.get("/facturas")
async def facturas(request: Request, sesion=Depends(requerir_modulo("Facturacion"))):
    return templates.TemplateResponse(
        "facturas/index.html",
        {
            "request": request
        }
    )


@router.get("/reportes")
async def reportes(request: Request, sesion=Depends(requerir_modulo("Reportes"))):
    return templates.TemplateResponse(
        "reportes/index.html",
        {
            "request": request
        }
    )


@router.get("/usuarios")
async def usuarios(request: Request, sesion=Depends(requerir_modulo("Usuarios"))):
    return templates.TemplateResponse(
        "usuarios/index.html",
        {
            "request": request
        }
    )


@router.get("/roles")
async def roles(request: Request, sesion=Depends(requerir_modulo("Usuarios"))):
    return templates.TemplateResponse(
        "roles/index.html",
        {
            "request": request
        }
    )


@router.get("/agenda")
async def agenda(request: Request, sesion=Depends(requerir_modulo("Agenda"))):
    return templates.TemplateResponse(
        "agenda/calendario.html",
        {
            "request": request
        }
    )


@router.get("/procesar-validar")
async def procesar_validar(request: Request, sesion=Depends(requerir_modulo("ProcesarValidar"))):
    return templates.TemplateResponse(
        "procesar_validar/index.html",
        {
            "request": request
        }
    )


@router.get("/configuracion-lab")
async def configuracion_lab(request: Request, sesion=Depends(requerir_modulo("Configuracion"))):
    return templates.TemplateResponse(
        "configuracion/index.html",
        {
            "request": request
        }
    )


@router.get("/inventario")
async def inventario(request: Request, sesion=Depends(requerir_modulo("Inventario"))):
    return templates.TemplateResponse(
        "inventario/index.html",
        {
            "request": request
        }
    )


@router.get("/gastos")
async def gastos(request: Request, sesion=Depends(requerir_modulo("Gastos"))):
    return templates.TemplateResponse("gastos/index.html", {"request": request})
