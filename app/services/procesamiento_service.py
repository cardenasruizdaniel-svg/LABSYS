"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-013
Archivo: app/services/procesamiento_service.py
"""

from typing import Optional

from app.models.procesamiento import Procesamiento
from app.repositories.procesamiento_repository import ProcesamientoRepository


class ProcesamientoService:

    def __init__(self, repository: ProcesamientoRepository):
        self.repository = repository

    def listar(self) -> list[Procesamiento]:
        return self.repository.listar()

    def obtener_por_id(self, procesamiento_id: int) -> Optional[Procesamiento]:
        return self.repository.obtener_por_id(procesamiento_id)

    def crear(self, datos: dict) -> Procesamiento:
        existente = self.repository.obtener_por_muestra(datos["muestra_id"])
        if existente:
            raise ValueError("La muestra ya tiene un procesamiento asociado.")

        procesamiento = Procesamiento(
            **datos,
            estado="EN_PROCESO",
        )
        return self.repository.crear(procesamiento)

    def actualizar(
        self,
        procesamiento_id: int,
        datos: dict,
    ) -> Optional[Procesamiento]:
        procesamiento = self.repository.obtener_por_id(procesamiento_id)

        if procesamiento is None:
            return None

        for campo, valor in datos.items():
            if valor is not None:
                setattr(procesamiento, campo, valor)

        return self.repository.actualizar(procesamiento)
