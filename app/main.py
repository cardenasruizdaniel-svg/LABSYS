"""
=========================================================
LABSYS DIALIZAR
Archivo principal FastAPI
app/main.py
=========================================================
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("app/static/img", exist_ok=True)
    from app.database.init_db import initialize_database
    initialize_database()
    yield


app = FastAPI(
    title="LABSYS DIALIZAR",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Routers
from app.routers.dashboard import router as dashboard_router
from app.routers.pacientes import router as pacientes_router
from app.routers.ordenes import router as ordenes_router
from app.routers.muestras import router as muestras_router
from app.routers.procesamientos import router as procesamientos_router
from app.routers.validaciones import router as validaciones_router
from app.routers.resultados import router as resultados_router
from app.routers.facturas import router as facturas_router
from app.routers.reportes import router as reportes_router
from app.routers.usuarios import router as usuarios_router
from app.routers.roles import router as roles_router
from app.routers.permisos import router as permisos_router
from app.routers.login import router as login_router
from app.routers.web import router as web_router
from app.routers.agenda import router as agenda_router
from app.routers.convenios import router as convenios_router
from app.routers.eps import router as eps_router
from app.routers.medicos import router as medicos_router
from app.routers.rol_permisos import router as rol_permisos_router
from app.routers.usuario_roles import router as usuario_roles_router
from app.routers.configuracion import router as configuracion_router
from app.routers.inventario import router as inventario_router
from app.routers.examenes import router as examenes_router
from app.routers.geografia import router as geografia_router
from app.routers.caja import router as caja_router
from app.routers.parametros_examen import router as parametros_examen_router
from app.routers.gastos import router as gastos_router
from app.routers.mobile import router as mobile_router

from fastapi.responses import RedirectResponse
from starlette.requests import Request as StarletteRequest

from app.security.sesion import RedireccionRequerida


@app.exception_handler(RedireccionRequerida)
async def _manejar_redireccion_requerida(request: StarletteRequest, exc: RedireccionRequerida):
    return RedirectResponse(url=exc.url, status_code=302)


templates = Jinja2Templates(directory="app/templates")

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


@app.middleware("http")
async def _no_cache_static(request: StarletteRequest, call_next):
    resp = await call_next(request)
    path = request.url.path
    if path.startswith("/static/") and (path.endswith(".js") or path.endswith(".css")):
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
    return resp


app.include_router(web_router)
app.include_router(login_router)
app.include_router(dashboard_router)
app.include_router(pacientes_router)
app.include_router(ordenes_router)
app.include_router(muestras_router)
app.include_router(procesamientos_router)
app.include_router(validaciones_router)
app.include_router(resultados_router)
app.include_router(facturas_router)
app.include_router(reportes_router)
app.include_router(usuarios_router)
app.include_router(roles_router)
app.include_router(permisos_router)
app.include_router(agenda_router)
app.include_router(convenios_router)
app.include_router(eps_router)
app.include_router(medicos_router)
app.include_router(rol_permisos_router)
app.include_router(usuario_roles_router)
app.include_router(configuracion_router)
app.include_router(inventario_router)
app.include_router(examenes_router)
app.include_router(geografia_router)
app.include_router(caja_router)
app.include_router(parametros_examen_router)
app.include_router(gastos_router)
app.include_router(mobile_router)


@app.get("/")
async def home():
    return {
        "application": "LABSYS DIALIZAR",
        "version": "1.0.0",
        "status": "running",
    }
