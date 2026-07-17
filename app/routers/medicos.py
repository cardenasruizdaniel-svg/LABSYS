"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-008
Archivo: app/routers/medicos.py

CRUD REST de profesionales (medicos y enfermeros/as).
"""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.medico_repository import MedicoRepository
from app.schemas.medico import MedicoActualizar, MedicoCrear, MedicoRespuesta
from app.services.importacion_excel_service import (
    generar_plantilla_excel,
    leer_filas_excel,
    procesar_importacion,
)
from app.services.medico_service import MedicoService

router = APIRouter(prefix="/medicos", tags=["Profesionales"])

COLUMNAS_PROFESIONAL = [
    "tipo_profesional", "registro_medico", "nombres", "apellidos",
    "especialidad", "telefono", "correo",
]

CARPETA_FIRMAS = os.path.join("app", "static", "firmas")
EXTENSIONES_FIRMA_PERMITIDAS = {".png", ".jpg", ".jpeg"}


def get_service(db: Session) -> MedicoService:
    return MedicoService(MedicoRepository(db))


@router.get("/", response_model=list[MedicoRespuesta])
def listar(tipo: str | None = None, db: Session = Depends(get_db)):
    medicos = get_service(db).listar()
    if tipo:
        medicos = [m for m in medicos if m.tipo_profesional == tipo.upper()]
    return medicos


@router.get("/{medico_id}", response_model=MedicoRespuesta)
def obtener(medico_id: int, db: Session = Depends(get_db)):
    medico = get_service(db).obtener_por_id(medico_id)
    if medico is None:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    return medico


@router.post("/", response_model=MedicoRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: MedicoCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{medico_id}", response_model=MedicoRespuesta)
def actualizar(medico_id: int, datos: MedicoActualizar, db: Session = Depends(get_db)):
    medico = get_service(db).actualizar(medico_id, datos.model_dump())
    if medico is None:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    return medico


@router.delete("/{medico_id}")
def eliminar(medico_id: int, db: Session = Depends(get_db)):
    medico = get_service(db).eliminar(medico_id)
    if medico is None:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    return {"success": True, "message": "Médico desactivado correctamente"}


@router.get("/plantilla/excel")
def descargar_plantilla():
    contenido = generar_plantilla_excel(
        "Profesionales",
        COLUMNAS_PROFESIONAL,
        ["MEDICO", "RM-12345", "CARLOS", "PEREZ", "Medicina interna", "3160000000", "correo@ejemplo.com"],
    )
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="plantilla_profesionales.xlsx"'},
    )


@router.post("/{medico_id}/firma", response_model=MedicoRespuesta)
def subir_firma(medico_id: int, archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    servicio = get_service(db)
    medico = servicio.obtener_por_id(medico_id)
    if medico is None:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    extension = os.path.splitext(archivo.filename or "")[1].lower()
    if extension not in EXTENSIONES_FIRMA_PERMITIDAS:
        raise HTTPException(status_code=400, detail="La firma debe ser una imagen .png, .jpg o .jpeg.")

    os.makedirs(CARPETA_FIRMAS, exist_ok=True)
    nombre_archivo = f"firma_{medico_id}_{uuid.uuid4().hex[:8]}{extension}"
    ruta_absoluta = os.path.join(CARPETA_FIRMAS, nombre_archivo)

    with open(ruta_absoluta, "wb") as destino:
        destino.write(archivo.file.read())

    ruta_relativa = f"firmas/{nombre_archivo}"
    return servicio.actualizar_firma(medico_id, ruta_relativa)


@router.post("/importar/excel")
async def importar_excel(archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    if not (archivo.filename or "").lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel .xlsx (no .csv ni .xls).")

    contenido = await archivo.read()

    try:
        registros = leer_filas_excel(contenido, COLUMNAS_PROFESIONAL)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    servicio = get_service(db)

    def crear_uno(registro: dict):
        datos = {
            "tipo_profesional": str(registro.get("tipo_profesional") or "MEDICO").strip().upper(),
            "registro_medico": str(registro.get("registro_medico") or "").strip(),
            "nombres": str(registro.get("nombres") or "").strip(),
            "apellidos": str(registro.get("apellidos") or "").strip(),
            "especialidad": (str(registro["especialidad"]).strip() if registro.get("especialidad") else None),
            "telefono": (str(registro["telefono"]).strip() if registro.get("telefono") else None),
            "correo": (str(registro["correo"]).strip() if registro.get("correo") else None),
        }

        if not datos["registro_medico"] or not datos["nombres"] or not datos["apellidos"]:
            raise ValueError("registro_medico, nombres y apellidos son obligatorios.")

        if datos["tipo_profesional"] not in ("MEDICO", "ENFERMERO"):
            raise ValueError("tipo_profesional debe ser MEDICO o ENFERMERO.")

        servicio.crear(datos)

    resultado = procesar_importacion(registros, crear_uno)
    return resultado
