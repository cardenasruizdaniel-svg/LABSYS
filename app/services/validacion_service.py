"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-014
Archivo: app/services/validacion_service.py
"""

from typing import Optional
from datetime import datetime

from app.models.validacion import Validacion
from app.repositories.validacion_repository import ValidacionRepository


class ValidacionService:

    def __init__(self, repository: ValidacionRepository):
        self.repository = repository

    def listar(self) -> list[Validacion]:
        return self.repository.listar()

    def obtener_por_id(self, validacion_id: int) -> Optional[Validacion]:
        return self.repository.obtener_por_id(validacion_id)

    def crear(self, datos: dict) -> Validacion:
        existente = self.repository.obtener_por_procesamiento(
            datos["procesamiento_id"]
        )
        if existente:
            raise ValueError(
                "El procesamiento ya tiene una validación registrada."
            )

        validacion = Validacion(
            **datos,
            estado="PENDIENTE",
        )
        return self.repository.crear(validacion)

    def validar(
        self,
        validacion_id: int,
        validador: str,
        observaciones: str | None = None,
        validador_id: int | None = None,
    ) -> Optional[Validacion]:

        validacion = self.repository.obtener_por_id(validacion_id)

        if validacion is None:
            return None

        validacion.estado = "VALIDADO"
        validacion.validador = validador
        validacion.validador_id = validador_id
        validacion.observaciones = observaciones
        validacion.fecha_validacion = datetime.utcnow()

        return self.repository.actualizar(validacion)

    def actualizar(
        self,
        validacion_id: int,
        datos: dict,
    ) -> Optional[Validacion]:

        validacion = self.repository.obtener_por_id(validacion_id)

        if validacion is None:
            return None

        for campo, valor in datos.items():
            if valor is not None:
                setattr(validacion, campo, valor)

        return self.repository.actualizar(validacion)
