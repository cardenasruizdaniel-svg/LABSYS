"""
LABSYS DIALIZAR
Módulo: Facturación / Caja
Archivo: app/routers/caja.py
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.sesion import UsuarioSesion, usuario_actual_opcional
from app.services.caja_service import CajaService

router = APIRouter(prefix="/caja", tags=["Caja"])


class AbrirCajaPayload(BaseModel):
    monto_inicial: Decimal
    observaciones: Optional[str] = None


class CerrarCajaPayload(BaseModel):
    monto_contado: Decimal
    denominaciones: Optional[dict] = None
    observaciones: Optional[str] = None


def get_service(db: Session) -> CajaService:
    return CajaService(db)


@router.get("/estado")
def estado_actual(db: Session = Depends(get_db)):
    return get_service(db).reporte_actual()


@router.get("/aperturas")
def listar_aperturas(db: Session = Depends(get_db)):
    return get_service(db).listar_aperturas()


@router.get("/cierres")
def listar_cierres(db: Session = Depends(get_db)):
    return get_service(db).listar_cierres()


@router.post("/abrir", status_code=status.HTTP_201_CREATED)
def abrir_caja(
    datos: AbrirCajaPayload,
    db: Session = Depends(get_db),
    sesion: Optional[UsuarioSesion] = Depends(usuario_actual_opcional),
):
    try:
        usuario_id = sesion.usuario.id if sesion else None
        return get_service(db).abrir_caja(datos.monto_inicial, usuario_id, datos.observaciones)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/cerrar", status_code=status.HTTP_201_CREATED)
def cerrar_caja(
    datos: CerrarCajaPayload,
    db: Session = Depends(get_db),
    sesion: Optional[UsuarioSesion] = Depends(usuario_actual_opcional),
):
    try:
        usuario_id = sesion.usuario.id if sesion else None
        return get_service(db).cerrar_caja(
            datos.monto_contado, usuario_id, datos.observaciones, datos.denominaciones
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/cuadre-dia")
def cuadre_dia(
    fecha: Optional[str] = Query(None, description="Fecha YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    d = date.fromisoformat(fecha) if fecha else date.today()
    return get_service(db).cuadre_dia(d)


@router.get("/resumen")
def resumen(
    agrupacion: str = Query("dia", pattern="^(dia|semana|mes|anio)$"),
    db: Session = Depends(get_db),
):
    return get_service(db).resumen_por_periodo(agrupacion)


@router.get("/resumen-rango")
def resumen_rango(
    desde: str = Query(..., description="Fecha inicio YYYY-MM-DD"),
    hasta: str = Query(..., description="Fecha fin YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    return get_service(db).resumen_por_rango(desde, hasta)


class IngresoCajaPayload(BaseModel):
    valor: Decimal
    origen: str
    descripcion: Optional[str] = None


@router.post("/ingresos", status_code=status.HTTP_201_CREATED)
def registrar_ingreso(
    datos: IngresoCajaPayload,
    db: Session = Depends(get_db),
    sesion: Optional[UsuarioSesion] = Depends(usuario_actual_opcional),
):
    svc = get_service(db)
    apertura = svc.apertura_activa()
    if apertura is None:
        raise HTTPException(status_code=400, detail="No hay caja abierta. Abra una caja primero.")
    try:
        usuario_id = sesion.usuario.id if sesion else None
        return svc.registrar_ingreso(apertura.id, datos.valor, datos.origen, datos.descripcion, usuario_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/ingresos")
def listar_ingresos(
    apertura_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return get_service(db).listar_ingresos(apertura_id)
