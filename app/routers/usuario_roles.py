
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-005
Archivo: app/routers/usuario_roles.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.usuario_rol_repository import UsuarioRolRepository
from app.schemas.usuario_rol import UsuarioRolCrear, UsuarioRolRespuesta
from app.services.usuario_rol_service import UsuarioRolService

router = APIRouter(
    prefix="/usuario-roles",
    tags=["Usuario - Roles"],
)


def get_service(db: Session) -> UsuarioRolService:
    return UsuarioRolService(UsuarioRolRepository(db))


@router.get("/", response_model=list[UsuarioRolRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/usuario/{usuario_id}", response_model=list[UsuarioRolRespuesta])
def listar_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return get_service(db).listar_por_usuario(usuario_id)


@router.post("/", response_model=UsuarioRolRespuesta, status_code=status.HTTP_201_CREATED)
def asignar(datos: UsuarioRolCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).asignar(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.delete("/{usuario_id}/{rol_id}")
def quitar(usuario_id: int, rol_id: int, db: Session = Depends(get_db)):
    ok = get_service(db).quitar(usuario_id, rol_id)
    if ok is None:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return {"success": True, "message": "Rol retirado del usuario correctamente"}
