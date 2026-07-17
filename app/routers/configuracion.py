"""
LABSYS DIALIZAR
Módulo: Configuración
Archivo: app/routers/configuracion.py

Datos del laboratorio (nombre, NIT, dirección, logo) usados como
membrete en los documentos imprimibles (resultados, facturas, etc.).
"""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.convenio import Convenio
from app.models.eps import EPS
from app.models.medico import Medico
from app.repositories.configuracion_laboratorio_repository import (
    ConfiguracionLaboratorioRepository,
)
from app.schemas.configuracion_laboratorio import (
    ConfiguracionLaboratorioActualizar,
    ConfiguracionLaboratorioRespuesta,
)
from app.security.sesion import UsuarioSesion, usuario_actual
from app.services.configuracion_laboratorio_service import (
    ConfiguracionLaboratorioService,
)

router = APIRouter(prefix="/configuracion", tags=["Configuración"])

EXTENSIONES_PERMITIDAS = {".png", ".jpg", ".jpeg"}
LOGO_DIR = os.path.join("app", "static", "img")


def get_service(db: Session) -> ConfiguracionLaboratorioService:
    return ConfiguracionLaboratorioService(ConfiguracionLaboratorioRepository(db))


@router.get("/particular")
def obtener_datos_particular(db: Session = Depends(get_db)):
    """
    Devuelve los IDs de la EPS, Convenio y Médico "PARTICULAR" que se
    usan para registrar Órdenes y Facturas de pacientes que no tienen
    EPS ni médico remitente (exámenes que el paciente paga directo,
    típicamente agendados desde el módulo de Agenda como "particular").
    """
    eps = db.query(EPS).filter(EPS.codigo == "PARTICULAR").first()
    convenio = db.query(Convenio).filter(Convenio.codigo == "PARTICULAR").first()
    medico = db.query(Medico).filter(Medico.registro_medico == "PARTICULAR").first()

    if not (eps and convenio and medico):
        raise HTTPException(
            status_code=404,
            detail=(
                "Los datos de 'Particular' todavía no existen en la base de datos. "
                "Ejecute nuevamente: python -m app.database.create_tables"
            ),
        )

    return {
        "eps_id": eps.id,
        "convenio_id": convenio.id,
        "medico_id": medico.id,
    }


@router.get("/", response_model=ConfiguracionLaboratorioRespuesta)
def obtener(db: Session = Depends(get_db)):
    return get_service(db).obtener()


@router.put("/", response_model=ConfiguracionLaboratorioRespuesta)
def actualizar(datos: ConfiguracionLaboratorioActualizar, db: Session = Depends(get_db)):
    return get_service(db).actualizar(datos.model_dump(exclude_unset=True))


@router.post("/logo", response_model=ConfiguracionLaboratorioRespuesta)
def subir_logo(archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    extension = os.path.splitext(archivo.filename or "")[1].lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail="El logo debe ser una imagen .png, .jpg o .jpeg.",
        )

    os.makedirs(LOGO_DIR, exist_ok=True)

    nombre_archivo = f"logo_{uuid.uuid4().hex[:8]}{extension}"
    ruta_absoluta = os.path.join(LOGO_DIR, nombre_archivo)

    with open(ruta_absoluta, "wb") as destino:
        destino.write(archivo.file.read())

    # Ruta relativa a app/static, tal como se sirve por /static/...
    ruta_relativa = f"img/{nombre_archivo}"

    return get_service(db).actualizar_logo(ruta_relativa)


class BorrarDatosPayload(BaseModel):
    tablas: list[str]


TABLAS_PROTEGIDAS = {"usuarios", "roles", "permisos", "usuario_rol", "rol_permiso", "configuracion_laboratorio"}

TABLAS_DISPONIBLES = [
    "pacientes", "medicos", "eps", "convenios", "examenes", "parametros",
    "orden_examen", "ordenes", "resultados", "muestras", "procesamientos",
    "validaciones", "facturas", "gastos",
    "caja_aperturas", "caja_cierres",
    "movimientos_inventario", "items_inventario",
    "agenda_eventos", "agenda_configuracion",
]


@router.get("/tablas")
def listar_tablas(db: Session = Depends(get_db)):
    inspector = inspect(db.get_bind())
    tablas = inspector.get_table_names()
    return {"tablas": tablas, "protegidas": list(TABLAS_PROTEGIDAS)}


@router.post("/borrar-datos")
def borrar_datos(
    datos: BorrarDatosPayload,
    db: Session = Depends(get_db),
    sesion: UsuarioSesion = Depends(usuario_actual),
):
    if "Administrador" not in sesion.roles:
        raise HTTPException(status_code=403, detail="Solo el rol Administrador puede borrar datos.")

    tablas_borradas = []
    errores = []

    for tabla in datos.tablas:
        if tabla in TABLAS_PROTEGIDAS:
            errores.append(f"'{tabla}' está protegida y no se puede borrar.")
            continue
        try:
            db.execute(text(f'TRUNCATE TABLE "{tabla}" CASCADE'))
            db.commit()
            tablas_borradas.append(tabla)
        except Exception as e:
            db.rollback()
            errores.append(f"Error al borrar '{tabla}': {str(e)}")

    return {
        "borradas": tablas_borradas,
        "errores": errores,
        "mensaje": f"Se borraron {len(tablas_borradas)} tabla(s). {len(errores)} error(es).",
    }
