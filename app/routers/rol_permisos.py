
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-006
Archivo: app/routers/rol_permisos.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.rol_permiso_repository import RolPermisoRepository
from app.schemas.rol_permiso import RolPermisoCrear, RolPermisoRespuesta
from app.services.rol_permiso_service import RolPermisoService

router = APIRouter(
    prefix="/rol-permisos",
    tags=["Rol - Permisos"],
)


def get_service(db: Session) -> RolPermisoService:
    return RolPermisoService(RolPermisoRepository(db))


@router.get("/", response_model=list[RolPermisoRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/rol/{rol_id}", response_model=list[RolPermisoRespuesta])
def listar_por_rol(rol_id: int, db: Session = Depends(get_db)):
    return get_service(db).listar_por_rol(rol_id)


@router.post("/", response_model=RolPermisoRespuesta, status_code=status.HTTP_201_CREATED)
def asignar(datos: RolPermisoCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).asignar(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.delete("/{rol_id}/{permiso_id}")
def quitar(rol_id: int, permiso_id: int, db: Session = Depends(get_db)):
    ok = get_service(db).quitar(rol_id, permiso_id)
    if ok is None:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return {"success": True, "message": "Permiso retirado del rol correctamente"}
