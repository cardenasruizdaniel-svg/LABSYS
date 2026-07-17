"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-015
Archivo: app/routers/resultados.py
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.configuracion_laboratorio_repository import (
    ConfiguracionLaboratorioRepository,
)
from app.repositories.medico_repository import MedicoRepository
from app.repositories.muestra_repository import MuestraRepository
from app.repositories.orden_repository import OrdenRepository
from app.repositories.paciente_repository import PacienteRepository
from app.repositories.procesamiento_repository import ProcesamientoRepository
from app.repositories.resultado_repository import ResultadoRepository
from app.repositories.validacion_repository import ValidacionRepository
from app.schemas.resultado import (
    ResultadoActualizar,
    ResultadoCrear,
    ResultadoRespuesta,
)
from app.services.resultado_pdf_service import ResultadoPdfService
from app.services.resultado_service import ResultadoService

router = APIRouter(prefix="/resultados", tags=["Resultados"])


def get_service(db: Session) -> ResultadoService:
    return ResultadoService(ResultadoRepository(db))


def get_pdf_service(db: Session) -> ResultadoPdfService:
    return ResultadoPdfService(
        OrdenRepository(db),
        PacienteRepository(db),
        MedicoRepository(db),
        MuestraRepository(db),
        ProcesamientoRepository(db),
        ValidacionRepository(db),
        ResultadoRepository(db),
        ConfiguracionLaboratorioRepository(db),
    )


@router.get("/", response_model=list[ResultadoRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{resultado_id}", response_model=ResultadoRespuesta)
def obtener(resultado_id: int, db: Session = Depends(get_db)):
    resultado = get_service(db).obtener_por_id(resultado_id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")
    return resultado


@router.post("/", response_model=ResultadoRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: ResultadoCrear, db: Session = Depends(get_db)):
    return get_service(db).crear(datos.model_dump())


@router.put("/{resultado_id}", response_model=ResultadoRespuesta)
def actualizar(resultado_id: int, datos: ResultadoActualizar, db: Session = Depends(get_db)):
    resultado = get_service(db).actualizar(resultado_id, datos.model_dump())
    if resultado is None:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")
    return resultado


# ---------------------------------------------------------------
# Impresión (PDF) e historial por paciente
# ---------------------------------------------------------------

@router.get("/orden/{orden_id}/pdf")
def imprimir_resultados_orden(orden_id: int, db: Session = Depends(get_db)):
    try:
        pdf_bytes = get_pdf_service(db).generar_pdf_orden(orden_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="resultados_orden_{orden_id}.pdf"'},
    )


@router.get("/paciente/{paciente_id}/historial")
def historial_paciente(paciente_id: int, db: Session = Depends(get_db)):
    return get_pdf_service(db).historial_json(paciente_id)


@router.get("/paciente/{paciente_id}/historial/pdf")
def imprimir_historial_paciente(paciente_id: int, db: Session = Depends(get_db)):
    orden_repository = OrdenRepository(db)
    ordenes = orden_repository.listar_por_paciente(paciente_id)
    orden_ids = [o.id for o in ordenes]

    try:
        pdf_bytes = get_pdf_service(db).generar_pdf_historial_paciente(paciente_id, orden_ids)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="historial_paciente_{paciente_id}.pdf"'
        },
    )
