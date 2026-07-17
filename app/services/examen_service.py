"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Archivo: app/services/examen_service.py
"""

from typing import Optional

from app.models.examen import Examen
from app.repositories.examen_repository import ExamenRepository


class ExamenService:

    def __init__(self, repository: ExamenRepository):
        self.repository = repository

    def listar(self) -> list[Examen]:
        return self.repository.listar()

    def obtener_por_id(self, examen_id: int) -> Optional[Examen]:
        return self.repository.obtener_por_id(examen_id)

    def crear(self, datos: dict) -> Examen:
        if self.repository.obtener_por_codigo(datos["codigo"]):
            raise ValueError("Ya existe un examen con ese código.")

        examen = Examen(**datos, activo=True)
        return self.repository.crear(examen)

    def actualizar(self, examen_id: int, datos: dict) -> Optional[Examen]:
        examen = self.repository.obtener_por_id(examen_id)
        if examen is None:
            return None

        for campo, valor in datos.items():
            if valor is not None:
                setattr(examen, campo, valor)

        return self.repository.actualizar(examen)
