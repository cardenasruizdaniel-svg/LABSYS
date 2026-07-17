"""
LABSYS DIALIZAR
Modulo: Agenda
Archivo: app/routers/agenda.py

Programacion de citas para examenes (con orden medica previa
o particulares) y consulta/configuracion de cupos diarios.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.cita_repository import CitaRepository
from app.repositories.cupo_diario_repository import CupoDiarioRepository
from app.schemas.cita import (
    CitaActualizar,
    CitaAsociarOrden,
    CitaCambiarEstado,
    CitaCrear,
    CitaRespuesta,
    DisponibilidadRespuesta,
)
from app.schemas.cupo_diario import CupoDiarioCrear, CupoDiarioRespuesta
from app.services.cita_service import CitaService

router = APIRouter(prefix="/agenda", tags=["Agenda"])


def get_service(db: Session) -> CitaService:
    return CitaService(CitaRepository(db), CupoDiarioRepository(db))


# ---------------------------------------------------------------
# Disponibilidad / cupos
# ---------------------------------------------------------------

@router.get("/disponibilidad/{fecha}", response_model=DisponibilidadRespuesta)
def consultar_disponibilidad(fecha: date, db: Session = Depends(get_db)):
    return get_service(db).disponibilidad(fecha)


@router.post(
    "/cupos",
    response_model=CupoDiarioRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def configurar_cupo(datos: CupoDiarioCrear, db: Session = Depends(get_db)):
    return get_service(db).configurar_cupo(datos.fecha, datos.cupo_maximo)


# ---------------------------------------------------------------
# Citas
# ---------------------------------------------------------------

@router.get("/citas", response_model=list[CitaRespuesta])
def listar(
    fecha: date | None = None,
    paciente_id: int | None = None,
    db: Session = Depends(get_db),
):
    servicio = get_service(db)

    if fecha:
        return servicio.listar_por_fecha(fecha)
    if paciente_id:
        return servicio.listar_por_paciente(paciente_id)
    return servicio.listar()


@router.get("/citas/{cita_id}", response_model=CitaRespuesta)
def obtener(cita_id: int, db: Session = Depends(get_db)):
    cita = get_service(db).obtener_por_id(cita_id)
    if cita is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return cita


@router.post("/citas", response_model=CitaRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: CitaCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/citas/{cita_id}", response_model=CitaRespuesta)
def actualizar(cita_id: int, datos: CitaActualizar, db: Session = Depends(get_db)):
    try:
        cita = get_service(db).actualizar(
            cita_id, datos.model_dump(exclude_unset=True)
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if cita is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return cita


@router.patch("/citas/{cita_id}/orden", response_model=CitaRespuesta)
def asociar_orden(cita_id: int, datos: CitaAsociarOrden, db: Session = Depends(get_db)):
    cita = get_service(db).asociar_orden(cita_id, datos.orden_id)
    if cita is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return cita


@router.patch("/citas/{cita_id}/estado", response_model=CitaRespuesta)
def cambiar_estado(cita_id: int, datos: CitaCambiarEstado, db: Session = Depends(get_db)):
    try:
        cita = get_service(db).cambiar_estado(cita_id, datos.estado)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if cita is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return cita


@router.delete("/citas/{cita_id}")
def cancelar(cita_id: int, db: Session = Depends(get_db)):
    cita = get_service(db).cancelar(cita_id)
    if cita is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return {"success": True, "message": "Cita cancelada correctamente"}
