"""
LABSYS DIALIZAR
Módulo: Procesar y Validar
Archivo: app/routers/parametros_examen.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.parametro_examen_repository import ParametroExamenRepository
from app.schemas.parametro_examen import (
    ParametroExamenActualizar,
    ParametroExamenCrear,
    ParametroExamenRespuesta,
)
from app.services.parametro_examen_service import ParametroExamenService

router = APIRouter(prefix="/parametros-examen", tags=["ParametrosExamen"])


def get_service(db: Session) -> ParametroExamenService:
    return ParametroExamenService(ParametroExamenRepository(db))


@router.get("/", response_model=list[ParametroExamenRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{parametro_id}", response_model=ParametroExamenRespuesta)
def obtener(parametro_id: int, db: Session = Depends(get_db)):
    parametro = get_service(db).obtener_por_id(parametro_id)
    if parametro is None:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro


@router.get("/examen/{examen_id}", response_model=list[ParametroExamenRespuesta])
def listar_por_examen(examen_id: int, db: Session = Depends(get_db)):
    return get_service(db).listar_por_examen(examen_id)


@router.post("/por-examenes", response_model=list[ParametroExamenRespuesta])
def listar_por_examenes(examenes_ids: list[int], db: Session = Depends(get_db)):
    return get_service(db).listar_por_examenes(examenes_ids)


@router.post(
    "/",
    response_model=ParametroExamenRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(datos: ParametroExamenCrear, db: Session = Depends(get_db)):
    return get_service(db).crear(datos.model_dump())


@router.put("/{parametro_id}", response_model=ParametroExamenRespuesta)
def actualizar(
    parametro_id: int,
    datos: ParametroExamenActualizar,
    db: Session = Depends(get_db),
):
    parametro = get_service(db).actualizar(
        parametro_id, datos.model_dump(exclude_unset=True)
    )
    if parametro is None:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro


@router.delete("/{parametro_id}")
def eliminar(parametro_id: int, db: Session = Depends(get_db)):
    parametro = get_service(db).eliminar(parametro_id)
    if parametro is None:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return {"success": True, "message": "Parámetro eliminado correctamente"}
