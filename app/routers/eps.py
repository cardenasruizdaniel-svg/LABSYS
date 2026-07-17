"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-009
Archivo: app/routers/eps.py

CRUD REST de EPS (entidades aseguradoras).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.eps_repository import EPSRepository
from app.schemas.eps import EPSActualizar, EPSCrear, EPSRespuesta
from app.services.eps_service import EPSService

router = APIRouter(prefix="/eps", tags=["EPS"])


def get_service(db: Session) -> EPSService:
    return EPSService(EPSRepository(db))


@router.get("/", response_model=list[EPSRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{eps_id}", response_model=EPSRespuesta)
def obtener(eps_id: int, db: Session = Depends(get_db)):
    eps = get_service(db).obtener_por_id(eps_id)
    if eps is None:
        raise HTTPException(status_code=404, detail="EPS no encontrada")
    return eps


@router.post("/", response_model=EPSRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: EPSCrear, db: Session = Depends(get_db)):
    return get_service(db).crear(datos.model_dump())


@router.put("/{eps_id}", response_model=EPSRespuesta)
def actualizar(eps_id: int, datos: EPSActualizar, db: Session = Depends(get_db)):
    eps = get_service(db).actualizar(eps_id, datos.model_dump())
    if eps is None:
        raise HTTPException(status_code=404, detail="EPS no encontrada")
    return eps


@router.delete("/{eps_id}")
def eliminar(eps_id: int, db: Session = Depends(get_db)):
    eps = get_service(db).eliminar(eps_id)
    if eps is None:
        raise HTTPException(status_code=404, detail="EPS no encontrada")
    return {"success": True, "message": "EPS desactivada correctamente"}
