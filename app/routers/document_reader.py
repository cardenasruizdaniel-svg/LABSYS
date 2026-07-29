"""
LABSYS DIALIZAR
API de lectura de documentos con codigo de barras
app/routers/document_reader.py
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.paciente_repository import PacienteRepository
from app.security.sesion import UsuarioSesion, usuario_actual
from app.services.document_reader import procesar_lectura

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lector", tags=["Lector de documentos"])


class LecturaPayload(BaseModel):
    datos_crudos: str


class VerificarDocumentoPayload(BaseModel):
    tipo_documento: str = "CC"
    documento: str = ""


@router.post("/leer-cedula")
def leer_cedula(
    payload: LecturaPayload,
    sesion: UsuarioSesion = Depends(usuario_actual),
    db: Session = Depends(get_db),
):
    if not payload.datos_crudos or not payload.datos_crudos.strip():
        raise HTTPException(status_code=400, detail="No se recibieron datos del lector.")

    resultado = procesar_lectura(payload.datos_crudos)

    logger.info(
        "Lectura de cedula | usuario=%s | success=%s | doc=%s",
        sesion.usuario,
        resultado.get("success"),
        resultado.get("documento", "N/A"),
    )

    if not resultado.get("success"):
        return resultado

    repo = PacienteRepository(db)
    existente = repo.buscar_por_documento(
        resultado["tipo_documento"], resultado["documento"]
    )

    resultado["paciente_existente"] = existente is not None
    if existente:
        resultado["paciente_id"] = existente.id
        resultado["paciente_nombre"] = (
            f"{existente.primer_nombre} {existente.primer_apellido}"
        )

    return resultado


@router.post("/verificar-documento")
def verificar_documento(
    payload: VerificarDocumentoPayload,
    db: Session = Depends(get_db),
):
    repo = PacienteRepository(db)
    existente = repo.buscar_por_documento(payload.tipo_documento, payload.documento)

    if existente:
        return {
            "existe": True,
            "paciente_id": existente.id,
            "tipo_documento": existente.tipo_documento,
            "documento": existente.documento,
            "primer_nombre": existente.primer_nombre,
            "segundo_nombre": existente.segundo_nombre,
            "primer_apellido": existente.primer_apellido,
            "segundo_apellido": existente.segundo_apellido,
            "sexo": existente.sexo,
            "fecha_nacimiento": str(existente.fecha_nacimiento),
            "telefono": existente.telefono,
            "celular": existente.celular,
            "direccion": existente.direccion,
        }

    return {"existe": False}
