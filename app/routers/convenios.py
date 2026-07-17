"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-010
Archivo: app/routers/convenios.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.convenio_repository import ConvenioRepository
from app.schemas.convenio import ConvenioActualizar, ConvenioCrear, ConvenioRespuesta
from app.services.convenio_service import ConvenioService

router = APIRouter(prefix="/convenios", tags=["Convenios"])


def get_service(db: Session) -> ConvenioService:
    return ConvenioService(ConvenioRepository(db))


@router.get("/", response_model=list[ConvenioRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{convenio_id}", response_model=ConvenioRespuesta)
def obtener(convenio_id: int, db: Session = Depends(get_db)):
    convenio = get_service(db).obtener_por_id(convenio_id)
    if convenio is None:
        raise HTTPException(status_code=404, detail="Convenio no encontrado")
    return convenio


@router.post("/", response_model=ConvenioRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: ConvenioCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{convenio_id}", response_model=ConvenioRespuesta)
def actualizar(convenio_id: int, datos: ConvenioActualizar, db: Session = Depends(get_db)):
    convenio = get_service(db).actualizar(convenio_id, datos.model_dump())
    if convenio is None:
        raise HTTPException(status_code=404, detail="Convenio no encontrado")
    return convenio


@router.delete("/{convenio_id}")
def eliminar(convenio_id: int, db: Session = Depends(get_db)):
    convenio = get_service(db).eliminar(convenio_id)
    if convenio is None:
        raise HTTPException(status_code=404, detail="Convenio no encontrado")
    return {"success": True, "message": "Convenio desactivado correctamente"}
