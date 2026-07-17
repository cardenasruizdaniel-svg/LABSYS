"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Archivo: app/routers/examenes.py

CRUD del catalogo de examenes que ofrece el laboratorio.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.examen_repository import ExamenRepository
from app.schemas.examen import ExamenActualizar, ExamenCrear, ExamenRespuesta
from app.services.examen_service import ExamenService

router = APIRouter(prefix="/examenes", tags=["Exámenes"])


def get_service(db: Session) -> ExamenService:
    return ExamenService(ExamenRepository(db))


@router.get("/", response_model=list[ExamenRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{examen_id}", response_model=ExamenRespuesta)
def obtener(examen_id: int, db: Session = Depends(get_db)):
    examen = get_service(db).obtener_por_id(examen_id)
    if examen is None:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    return examen


@router.post("/", response_model=ExamenRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: ExamenCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{examen_id}", response_model=ExamenRespuesta)
def actualizar(examen_id: int, datos: ExamenActualizar, db: Session = Depends(get_db)):
    examen = get_service(db).actualizar(examen_id, datos.model_dump(exclude_unset=True))
    if examen is None:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    return examen
