"""
LABSYS DIALIZAR
Modulo: Catalogos geograficos
Archivo: app/routers/geografia.py

Catalogo de Departamentos y Ciudades/Municipios de Colombia. Viene
precargado (ver seed_data.py) pero se puede crear o eliminar mas
entradas desde aqui.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.geografia_repository import CiudadRepository, DepartamentoRepository
from app.schemas.geografia import (
    CiudadCrear,
    CiudadRespuesta,
    DepartamentoCrear,
    DepartamentoRespuesta,
)

router = APIRouter(prefix="/geografia", tags=["Geografía (Ciudades/Departamentos)"])


@router.get("/departamentos", response_model=list[DepartamentoRespuesta])
def listar_departamentos(db: Session = Depends(get_db)):
    return DepartamentoRepository(db).listar()


@router.post("/departamentos", response_model=DepartamentoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_departamento(datos: DepartamentoCrear, db: Session = Depends(get_db)):
    repo = DepartamentoRepository(db)
    if repo.obtener_por_nombre(datos.nombre):
        raise HTTPException(status_code=400, detail="Ya existe un departamento con ese nombre.")
    from app.models.departamento import Departamento
    return repo.crear(Departamento(nombre=datos.nombre))


@router.delete("/departamentos/{dep_id}")
def eliminar_departamento(dep_id: int, db: Session = Depends(get_db)):
    repo = DepartamentoRepository(db)
    dep = repo.obtener_por_id(dep_id)
    if dep is None:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    repo.eliminar(dep)
    return {"success": True, "message": "Departamento eliminado"}


@router.get("/ciudades", response_model=list[CiudadRespuesta])
def listar_ciudades(departamento_id: int | None = None, db: Session = Depends(get_db)):
    repo = CiudadRepository(db)
    if departamento_id:
        return repo.listar_por_departamento(departamento_id)
    return repo.listar()


@router.post("/ciudades", response_model=CiudadRespuesta, status_code=status.HTTP_201_CREATED)
def crear_ciudad(datos: CiudadCrear, db: Session = Depends(get_db)):
    repo = CiudadRepository(db)
    if repo.obtener_por_nombre_y_departamento(datos.nombre, datos.departamento_id):
        raise HTTPException(status_code=400, detail="Esa ciudad ya existe en ese departamento.")
    from app.models.ciudad import Ciudad
    return repo.crear(Ciudad(nombre=datos.nombre, departamento_id=datos.departamento_id))


@router.delete("/ciudades/{ciudad_id}")
def eliminar_ciudad(ciudad_id: int, db: Session = Depends(get_db)):
    repo = CiudadRepository(db)
    ciudad = repo.obtener_por_id(ciudad_id)
    if ciudad is None:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    repo.eliminar(ciudad)
    return {"success": True, "message": "Ciudad eliminada"}
