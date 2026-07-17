"""
LABSYS DIALIZAR
Módulo: Gastos
Archivo: app/routers/gastos.py
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.gasto_repository import GastoRepository
from app.schemas.gasto import GastoCrear, GastoActualizar, GastoRespuesta
from app.security.sesion import UsuarioSesion, usuario_actual_opcional
from app.services.gasto_service import GastoService

router = APIRouter(prefix="/gastos", tags=["Gastos"])


def get_service(db: Session) -> GastoService:
    return GastoService(GastoRepository(db))


@router.get("/", response_model=list[GastoRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/categorias")
def categorias():
    from app.services.gasto_service import CATEGORIAS_GASTOS
    return {"categorias": CATEGORIAS_GASTOS}


@router.get("/resumen-hoy")
def resumen_hoy(db: Session = Depends(get_db)):
    svc = get_service(db)
    return {
        "total_gastos_hoy": svc.total_gastos_hoy(),
        "por_categoria": svc.gastos_por_categoria(),
    }


@router.get("/{gasto_id}", response_model=GastoRespuesta)
def obtener(gasto_id: int, db: Session = Depends(get_db)):
    g = get_service(db).obtener_por_id(gasto_id)
    if not g:
        raise HTTPException(404, "Gasto no encontrado")
    return g


@router.post("/", response_model=GastoRespuesta, status_code=status.HTTP_201_CREATED)
def crear(
    datos: GastoCrear,
    db: Session = Depends(get_db),
    sesion: Optional[UsuarioSesion] = Depends(usuario_actual_opcional),
):
    try:
        usuario_id = sesion.usuario.id if sesion else None
        return get_service(db).crear(datos.model_dump(), usuario_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{gasto_id}", response_model=GastoRespuesta)
def actualizar(gasto_id: int, datos: GastoActualizar, db: Session = Depends(get_db)):
    g = get_service(db).actualizar(gasto_id, datos.model_dump(exclude_unset=True))
    if not g:
        raise HTTPException(404, "Gasto no encontrado")
    return g


@router.delete("/{gasto_id}")
def eliminar(gasto_id: int, db: Session = Depends(get_db)):
    if not get_service(db).eliminar(gasto_id):
        raise HTTPException(404, "Gasto no encontrado")
    return {"success": True, "message": "Gasto eliminado correctamente"}
