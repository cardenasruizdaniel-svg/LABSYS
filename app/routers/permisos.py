
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-004
Archivo: app/routers/permisos.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.permiso_repository import PermisoRepository
from app.schemas.permiso import (
    PermisoActualizar,
    PermisoCrear,
    PermisoRespuesta,
)
from app.services.permiso_service import PermisoService

router = APIRouter(prefix="/permisos", tags=["Permisos"])


def get_service(db: Session) -> PermisoService:
    return PermisoService(PermisoRepository(db))


@router.get("/", response_model=list[PermisoRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{permiso_id}", response_model=PermisoRespuesta)
def obtener(permiso_id: int, db: Session = Depends(get_db)):
    permiso = get_service(db).obtener_por_id(permiso_id)
    if permiso is None:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return permiso


@router.post("/", response_model=PermisoRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: PermisoCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{permiso_id}", response_model=PermisoRespuesta)
def actualizar(permiso_id: int, datos: PermisoActualizar, db: Session = Depends(get_db)):
    permiso = get_service(db).actualizar(permiso_id, datos.model_dump())
    if permiso is None:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return permiso


@router.delete("/{permiso_id}")
def eliminar(permiso_id: int, db: Session = Depends(get_db)):
    permiso = get_service(db).eliminar(permiso_id)
    if permiso is None:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return {"success": True, "message": "Permiso desactivado correctamente"}
