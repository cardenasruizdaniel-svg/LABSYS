
"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-007
Archivo: app/routers/pacientes.py

CRUD REST de pacientes.
"""

from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.paciente_repository import PacienteRepository
from app.schemas.paciente import (
    PacienteActualizar,
    PacienteCrear,
    PacienteRespuesta,
)
from app.services.importacion_excel_service import (
    generar_plantilla_excel,
    leer_filas_excel,
    procesar_importacion,
)
from app.services.paciente_service import PacienteService

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"],
)

COLUMNAS_PACIENTE = [
    "tipo_documento", "documento", "primer_nombre", "segundo_nombre",
    "primer_apellido", "segundo_apellido", "fecha_nacimiento", "sexo",
    "telefono", "celular", "correo", "direccion", "municipio", "departamento",
]


def get_service(db: Session) -> PacienteService:
    return PacienteService(PacienteRepository(db))


@router.get("/", response_model=list[PacienteRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{paciente_id}", response_model=PacienteRespuesta)
def obtener(paciente_id: int, db: Session = Depends(get_db)):
    paciente = get_service(db).obtener_por_id(paciente_id)
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente


@router.post("/", response_model=PacienteRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: PacienteCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{paciente_id}", response_model=PacienteRespuesta)
def actualizar(paciente_id: int, datos: PacienteActualizar, db: Session = Depends(get_db)):
    paciente = get_service(db).actualizar(paciente_id, datos.model_dump())
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente


@router.delete("/{paciente_id}")
def eliminar(paciente_id: int, db: Session = Depends(get_db)):
    paciente = get_service(db).eliminar(paciente_id)
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {"success": True, "message": "Paciente desactivado correctamente"}


@router.get("/plantilla/excel")
def descargar_plantilla():
    contenido = generar_plantilla_excel(
        "Pacientes",
        COLUMNAS_PACIENTE,
        ["CC", "123456789", "MARIA", "ELENA", "RUIZ", "PIEDRAHITA", "1990-05-20", "Femenino",
         "3160000000", "3160000000", "correo@ejemplo.com", "Calle 10 # 5-20", "Armenia", "Quindío"],
    )
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="plantilla_pacientes.xlsx"'},
    )


@router.post("/importar/excel")
async def importar_excel(archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    if not (archivo.filename or "").lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel .xlsx (no .csv ni .xls).")

    contenido = await archivo.read()

    try:
        registros = leer_filas_excel(contenido, COLUMNAS_PACIENTE)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    servicio = get_service(db)

    def crear_uno(registro: dict):
        datos = {
            "tipo_documento": str(registro.get("tipo_documento") or "CC").strip(),
            "documento": str(registro.get("documento") or "").strip(),
            "primer_nombre": str(registro.get("primer_nombre") or "").strip(),
            "segundo_nombre": (str(registro["segundo_nombre"]).strip() if registro.get("segundo_nombre") else None),
            "primer_apellido": str(registro.get("primer_apellido") or "").strip(),
            "segundo_apellido": (str(registro["segundo_apellido"]).strip() if registro.get("segundo_apellido") else None),
            "fecha_nacimiento": str(registro.get("fecha_nacimiento"))[:10] if registro.get("fecha_nacimiento") else None,
            "sexo": str(registro.get("sexo") or "").strip(),
            "telefono": (str(registro["telefono"]).strip() if registro.get("telefono") else None),
            "celular": (str(registro["celular"]).strip() if registro.get("celular") else None),
            "correo": (str(registro["correo"]).strip() if registro.get("correo") else None),
            "direccion": (str(registro["direccion"]).strip() if registro.get("direccion") else None),
            "municipio": (str(registro["municipio"]).strip() if registro.get("municipio") else None),
            "departamento": (str(registro["departamento"]).strip() if registro.get("departamento") else None),
        }

        if not datos["documento"] or not datos["primer_nombre"] or not datos["primer_apellido"] or not datos["fecha_nacimiento"]:
            raise ValueError("documento, primer_nombre, primer_apellido y fecha_nacimiento son obligatorios.")

        try:
            datos["fecha_nacimiento"] = date.fromisoformat(datos["fecha_nacimiento"])
        except ValueError:
            raise ValueError(f"fecha_nacimiento '{datos['fecha_nacimiento']}' no tiene formato AAAA-MM-DD.")

        servicio.crear(datos)

    resultado = procesar_importacion(registros, crear_uno)
    return resultado
