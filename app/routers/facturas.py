"""
LABSYS DIALIZAR
Historia: HU-016
Archivo: app/routers/facturas.py
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import TypeAdapter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.factura import Factura
from app.repositories.convenio_repository import ConvenioRepository
from app.repositories.factura_repository import FacturaRepository
from app.repositories.orden_repository import OrdenRepository
from app.repositories.paciente_repository import PacienteRepository
from app.schemas.factura import FacturaCrear, FacturaActualizar, FacturaRespuesta
from app.services.factura_service import FacturaService

router = APIRouter(prefix="/facturas", tags=["Facturas"])


def get_service(db: Session) -> FacturaService:
    return FacturaService(
        FacturaRepository(db),
        ConvenioRepository(db),
        OrdenRepository(db),
        PacienteRepository(db),
    )


_response_list_adapter = TypeAdapter(list[FacturaRespuesta])


def _enrich(factura: Factura, db: Session) -> dict:
    data = {c.name: getattr(factura, c.name) for c in Factura.__table__.columns}
    orden_repo = OrdenRepository(db)
    paciente_repo = PacienteRepository(db)
    es_particular = False
    orden = orden_repo.obtener_por_id(factura.orden_id)
    if orden:
        paciente = paciente_repo.obtener_por_id(orden.paciente_id)
        if paciente:
            es_particular = paciente.es_particular
    data["es_particular"] = es_particular
    return data


@router.get("/siguiente")
def siguiente_numero(db: Session = Depends(get_db)):
    svc = get_service(db)
    numero, consecutivo = svc.generar_numero_factura()
    return {
        "fecha": str(date.today()),
        "numero_factura": numero,
        "consecutivo": consecutivo,
    }


@router.get("/")
def listar(db: Session = Depends(get_db)):
    facturas = get_service(db).listar()
    return _response_list_adapter.validate_python(
        [_enrich(f, db) for f in facturas]
    )


@router.get("/{factura_id}", response_model=FacturaRespuesta)
def obtener(factura_id: int, db: Session = Depends(get_db)):
    f = get_service(db).obtener_por_id(factura_id)
    if not f:
        raise HTTPException(404, "Factura no encontrada")
    return FacturaRespuesta(**_enrich(f, db))


@router.post("/", response_model=FacturaRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: FacturaCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{factura_id}", response_model=FacturaRespuesta)
def actualizar(factura_id: int, datos: FacturaActualizar, db: Session = Depends(get_db)):
    try:
        f = get_service(db).actualizar(factura_id, datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if not f:
        raise HTTPException(404, "Factura no encontrada")
    return FacturaRespuesta(**_enrich(f, db))


@router.patch("/{factura_id}/pagar-copago", response_model=FacturaRespuesta)
def pagar_copago(factura_id: int, db: Session = Depends(get_db)):
    try:
        f = get_service(db).registrar_pago_copago(factura_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if not f:
        raise HTTPException(404, "Factura no encontrada")
    return FacturaRespuesta(**_enrich(f, db))


@router.patch("/{factura_id}/estado", response_model=FacturaRespuesta)
def cambiar_estado(factura_id: int, datos: dict, db: Session = Depends(get_db)):
    nuevo_estado = datos.get("estado", "")
    try:
        f = get_service(db).cambiar_estado(factura_id, nuevo_estado)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if not f:
        raise HTTPException(404, "Factura no encontrada")
    return FacturaRespuesta(**_enrich(f, db))
