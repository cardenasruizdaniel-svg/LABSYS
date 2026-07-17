"""
LABSYS DIALIZAR
Modulo: Usuarios
Archivo: app/routers/usuarios.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import (
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioRespuesta,
)
from app.services.usuario_service import UsuarioService

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)


class ResetearPasswordPayload(BaseModel):
    password: str


def get_service(db: Session) -> UsuarioService:
    return UsuarioService(UsuarioRepository(db))


@router.get("/", response_model=list[UsuarioRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{usuario_id}", response_model=UsuarioRespuesta)
def obtener(usuario_id: int, db: Session = Depends(get_db)):
    usuario = get_service(db).obtener_por_id(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: UsuarioCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{usuario_id}", response_model=UsuarioRespuesta)
def actualizar(usuario_id: int, datos: UsuarioActualizar, db: Session = Depends(get_db)):
    usuario = get_service(db).actualizar(usuario_id, datos.model_dump())
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.patch("/{usuario_id}/resetear-password", response_model=UsuarioRespuesta)
def resetear_password(usuario_id: int, datos: ResetearPasswordPayload, db: Session = Depends(get_db)):
    usuario = get_service(db).resetear_password(usuario_id, datos.password)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.delete("/{usuario_id}")
def eliminar(usuario_id: int, db: Session = Depends(get_db)):
    usuario = get_service(db).eliminar(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"success": True, "message": "Usuario desactivado correctamente"}
