"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-012
Archivo: app/routers/muestras.py

CRUD REST de muestras.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.muestra_repository import MuestraRepository
from app.schemas.muestra import MuestraActualizar, MuestraCrear, MuestraRespuesta
from app.services.muestra_service import MuestraService

router = APIRouter(prefix="/muestras", tags=["Muestras"])


def get_service(db: Session) -> MuestraService:
    return MuestraService(MuestraRepository(db))


@router.get("/", response_model=list[MuestraRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{muestra_id}", response_model=MuestraRespuesta)
def obtener(muestra_id: int, db: Session = Depends(get_db)):
    muestra = get_service(db).obtener_por_id(muestra_id)
    if muestra is None:
        raise HTTPException(status_code=404, detail="Muestra no encontrada")
    return muestra


@router.post("/", response_model=MuestraRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: MuestraCrear, db: Session = Depends(get_db)):
    return get_service(db).crear(datos.model_dump())


@router.put("/{muestra_id}", response_model=MuestraRespuesta)
def actualizar(muestra_id: int, datos: MuestraActualizar, db: Session = Depends(get_db)):
    muestra = get_service(db).actualizar(muestra_id, datos.model_dump())
    if muestra is None:
        raise HTTPException(status_code=404, detail="Muestra no encontrada")
    return muestra
