
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-003
Archivo: app/routers/roles.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.rol_repository import RolRepository
from app.schemas.rol import RolActualizar, RolCrear, RolRespuesta
from app.services.rol_service import RolService

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


def get_service(db: Session) -> RolService:
    return RolService(RolRepository(db))


@router.get("/", response_model=list[RolRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{rol_id}", response_model=RolRespuesta)
def obtener(rol_id: int, db: Session = Depends(get_db)):
    rol = get_service(db).obtener_por_id(rol_id)
    if rol is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol


@router.post("/", response_model=RolRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: RolCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{rol_id}", response_model=RolRespuesta)
def actualizar(rol_id: int, datos: RolActualizar, db: Session = Depends(get_db)):
    rol = get_service(db).actualizar(rol_id, datos.model_dump())
    if rol is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol


@router.delete("/{rol_id}")
def eliminar(rol_id: int, db: Session = Depends(get_db)):
    rol = get_service(db).eliminar(rol_id)
    if rol is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"success": True, "message": "Rol desactivado correctamente"}
