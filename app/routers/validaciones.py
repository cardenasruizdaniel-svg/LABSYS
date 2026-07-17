"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-014
Archivo: app/routers/validaciones.py

CRUD REST de validaciones.
"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.repositories.medico_repository import MedicoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.validacion_repository import ValidacionRepository
from app.repositories.resultado_repository import ResultadoRepository
from app.repositories.muestra_repository import MuestraRepository
from app.repositories.procesamiento_repository import ProcesamientoRepository
from app.repositories.orden_repository import OrdenRepository
from app.repositories.paciente_repository import PacienteRepository
from app.repositories.configuracion_laboratorio_repository import (
    ConfiguracionLaboratorioRepository,
)
from app.schemas.validacion import (
    ValidacionActualizar,
    ValidacionCrear,
    ValidacionRespuesta,
)
from app.services.validacion_service import ValidacionService
from app.services.email_service import EmailService
from app.services.resultado_pdf_service import ResultadoPdfService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/validaciones", tags=["Validaciones"])


class ValidarPayload(BaseModel):
    validador_id: int | None = None
    validador: str | None = None
    observaciones: str | None = None


def get_service(db: Session) -> ValidacionService:
    return ValidacionService(ValidacionRepository(db))


def _enviar_resultados_correo(validacion_id: int):
    """Tarea en background: enviar correo con resultados al paciente."""
    db = SessionLocal()
    try:
        validacion_repo = ValidacionRepository(db)
        resultado_repo = ResultadoRepository(db)
        procesamiento_repo = ProcesamientoRepository(db)
        muestra_repo = MuestraRepository(db)
        orden_repo = OrdenRepository(db)
        paciente_repo = PacienteRepository(db)
        medico_repo = MedicoRepository(db)
        config_repo = ConfiguracionLaboratorioRepository(db)

        validacion = validacion_repo.obtener_por_id(validacion_id)
        if not validacion:
            return

        procesamiento = procesamiento_repo.obtener_por_id(validacion.procesamiento_id)
        if not procesamiento:
            return

        muestra = muestra_repo.obtener_por_id(procesamiento.muestra_id)
        if not muestra:
            return

        orden = orden_repo.obtener_por_id(muestra.orden_id)
        if not orden:
            return

        paciente = paciente_repo.obtener_por_id(orden.paciente_id)
        if not paciente:
            return

        correo = paciente.correo
        if not correo:
            logger.info(
                "Paciente %s %s no tiene correo. No se envia resultado para orden %s.",
                paciente.primer_nombre, paciente.primer_apellido, orden.numero_orden,
            )
            return

        medico = medico_repo.obtener_por_id(orden.medico_id)
        medico_nombre = f"{medico.nombres} {medico.apellidos}" if medico else "Sin medico"

        nombre_paciente = " ".join(filter(None, [
            paciente.primer_nombre, paciente.segundo_nombre,
            paciente.primer_apellido, paciente.segundo_apellido,
        ]))

        resultados = resultado_repo.obtener_por_validacion(validacion_id)

        examenes_rows = ""
        for r in resultados:
            valor = r.resultado or (str(r.valor_numerico) if r.valor_numerico is not None else "-")
            critico_html = f' style="color:#d32f2f;font-weight:600;"' if r.critico else ""
            examenes_rows += f"""
            <tr style="border-bottom:1px solid #eee;">
                <td style="padding:6px 8px;font-weight:500;">{r.examen}</td>
                <td style="padding:6px 8px;">{r.examen_codigo or ''}</td>
                <td style="padding:6px 8px;text-align:center;"{critico_html}>{valor}</td>
                <td style="padding:6px 8px;text-align:center;">{r.unidad or ''}</td>
                <td style="padding:6px 8px;text-align:center;">{r.valor_referencia or ''}</td>
            </tr>"""

        pdf_bytes = None
        try:
            pdf_service = ResultadoPdfService(
                orden_repository=orden_repo,
                paciente_repository=paciente_repo,
                medico_repository=medico_repo,
                muestra_repository=muestra_repo,
                procesamiento_repository=procesamiento_repo,
                validacion_repository=validacion_repo,
                resultado_repository=resultado_repo,
                configuracion_repository=config_repo,
            )
            pdf_bytes = pdf_service.generar_pdf_orden(orden.id)
        except Exception as e:
            logger.warning("No se pudo generar PDF para correo: %s", e)

        email_svc = EmailService()
        ok = email_svc.enviar_resultados(
            correo_paciente=correo,
            nombre_paciente=nombre_paciente,
            numero_orden=orden.numero_orden,
            fecha_orden=orden.fecha_creacion.strftime("%Y-%m-%d"),
            medico_nombre=medico_nombre,
            examenes_html=examenes_rows,
            observaciones=validacion.observaciones,
            pdf_bytes=pdf_bytes,
            pdf_filename=f"Resultados_{orden.numero_orden}.pdf",
        )

        if ok:
            logger.info("Correo de resultados enviado a %s para orden %s", correo, orden.numero_orden)
        else:
            logger.warning("No se pudo enviar correo a %s para orden %s", correo, orden.numero_orden)

    except Exception as e:
        logger.error("Error al enviar correo de resultados: %s", e)
    finally:
        db.close()


@router.get("/", response_model=list[ValidacionRespuesta])
def listar(db: Session = Depends(get_db)):
    return get_service(db).listar()


@router.get("/{validacion_id}", response_model=ValidacionRespuesta)
def obtener(validacion_id: int, db: Session = Depends(get_db)):
    item = get_service(db).obtener_por_id(validacion_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Validación no encontrada")
    return item


@router.post("/", response_model=ValidacionRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: ValidacionCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{validacion_id}", response_model=ValidacionRespuesta)
def actualizar(validacion_id: int, datos: ValidacionActualizar, db: Session = Depends(get_db)):
    item = get_service(db).actualizar(validacion_id, datos.model_dump())
    if item is None:
        raise HTTPException(status_code=404, detail="Validación no encontrada")
    return item


@router.patch("/{validacion_id}/validar", response_model=ValidacionRespuesta)
def validar(
    validacion_id: int,
    datos: ValidarPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    validador_nombre = datos.validador

    if datos.validador_id and not validador_nombre:
        profesional = MedicoRepository(db).obtener_por_id(datos.validador_id)
        if profesional:
            validador_nombre = f"{profesional.nombres} {profesional.apellidos}"
        else:
            usuario = UsuarioRepository(db).obtener_por_id(datos.validador_id)
            if usuario:
                validador_nombre = f"{usuario.nombres} {usuario.apellidos}"

    if not validador_nombre:
        raise HTTPException(status_code=400, detail="Debe indicar quién valida (seleccione un bacteriólogo).")

    item = get_service(db).validar(validacion_id, validador_nombre, datos.observaciones, datos.validador_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Validación no encontrada")

    background_tasks.add_task(_enviar_resultados_correo, validacion_id)

    return item
