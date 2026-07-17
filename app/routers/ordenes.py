"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-011
Archivo: app/routers/ordenes.py
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.examen_repository import ExamenRepository
from app.repositories.orden_examen_repository import OrdenExamenRepository
from app.repositories.orden_repository import OrdenRepository
from app.repositories.factura_repository import FacturaRepository
from app.repositories.convenio_repository import ConvenioRepository
from app.schemas.examen import ExamenOrdenExamenRespuesta
from app.schemas.orden import OrdenActualizar, OrdenCrear, OrdenRespuesta
from app.services.orden_service import OrdenService

router = APIRouter(prefix="/ordenes", tags=["Órdenes de Laboratorio"])


def get_service(db: Session) -> OrdenService:
    return OrdenService(
        OrdenRepository(db),
        OrdenExamenRepository(db),
        ExamenRepository(db),
        FacturaRepository(db),
        ConvenioRepository(db),
    )


@router.get("/siguiente")
def siguiente_numero(db: Session = Depends(get_db)):
    svc = get_service(db)
    numero, consecutivo = svc.generar_numero_orden()
    return {
        "fecha": str(date.today()),
        "numero_orden": numero,
        "consecutivo": consecutivo,
    }


@router.get("/hoy")
def ordenes_hoy(db: Session = Depends(get_db)):
    svc = get_service(db)
    total = svc.contar_hoy()
    _, consecutivo = svc.generar_numero_orden()
    ordenes = svc.listar()
    hoy = date.today()
    ordenes_hoy = [
        o for o in ordenes
        if o.fecha_creacion.date() == hoy
    ]
    return {
        "fecha": str(hoy),
        "total": total,
        "siguiente_consecutivo": consecutivo,
        "ordenes": [OrdenRespuesta.model_validate(o).model_dump() for o in ordenes_hoy],
    }


@router.get("/fecha/{fecha_str}")
def ordenes_por_fecha(fecha_str: str, db: Session = Depends(get_db)):
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD.")
    svc = get_service(db)
    ordenes = svc.listar()
    filtradas = [
        o for o in ordenes
        if o.fecha_creacion.date() == fecha
    ]
    return {
        "fecha": str(fecha),
        "total": len(filtradas),
        "ordenes": [OrdenRespuesta.model_validate(o).model_dump() for o in filtradas],
    }


@router.get("/", response_model=list[OrdenRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{orden_id}", response_model=OrdenRespuesta)
def obtener(orden_id: int, db: Session = Depends(get_db)):
    orden = get_service(db).obtener_por_id(orden_id)
    if orden is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden


@router.get("/{orden_id}/examenes", response_model=list[ExamenOrdenExamenRespuesta])
def listar_examenes(orden_id: int, db: Session = Depends(get_db)):
    return get_service(db).listar_examenes(orden_id)


@router.post("/", response_model=OrdenRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: OrdenCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{orden_id}", response_model=OrdenRespuesta)
def actualizar(orden_id: int, datos: OrdenActualizar, db: Session = Depends(get_db)):
    orden = get_service(db).actualizar(orden_id, datos.model_dump())
    if orden is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden
