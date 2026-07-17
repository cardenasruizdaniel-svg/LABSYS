"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-013
Archivo: app/routers/procesamientos.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.medico_repository import MedicoRepository
from app.repositories.procesamiento_repository import ProcesamientoRepository
from app.schemas.procesamiento import ProcesamientoActualizar, ProcesamientoCrear, ProcesamientoRespuesta
from app.services.procesamiento_service import ProcesamientoService

router = APIRouter(prefix="/procesamientos", tags=["Procesamientos"])


def get_service(db: Session) -> ProcesamientoService:
    return ProcesamientoService(ProcesamientoRepository(db))


@router.get("/", response_model=list[ProcesamientoRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{procesamiento_id}", response_model=ProcesamientoRespuesta)
def obtener(procesamiento_id: int, db: Session = Depends(get_db)):
    proc = get_service(db).obtener_por_id(procesamiento_id)
    if proc is None:
        raise HTTPException(status_code=404, detail="Procesamiento no encontrado")
    return proc


@router.post("/", response_model=ProcesamientoRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: ProcesamientoCrear, db: Session = Depends(get_db)):
    payload = datos.model_dump()

    if payload.get("profesional_id") and not payload.get("profesional"):
        profesional = MedicoRepository(db).obtener_por_id(payload["profesional_id"])
        if profesional:
            payload["profesional"] = f"{profesional.nombres} {profesional.apellidos}"

    try:
        return get_service(db).crear(payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{procesamiento_id}", response_model=ProcesamientoRespuesta)
def actualizar(procesamiento_id: int, datos: ProcesamientoActualizar, db: Session = Depends(get_db)):
    proc = get_service(db).actualizar(procesamiento_id, datos.model_dump())
    if proc is None:
        raise HTTPException(status_code=404, detail="Procesamiento no encontrado")
    return proc
