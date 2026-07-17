"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-015
Archivo: app/services/resultado_service.py
"""

from typing import Optional

from app.models.resultado import Resultado
from app.repositories.resultado_repository import ResultadoRepository


class ResultadoService:

    def __init__(self, repository: ResultadoRepository):
        self.repository = repository

    def listar(self) -> list[Resultado]:
        return self.repository.listar()

    def obtener_por_id(self, resultado_id: int) -> Optional[Resultado]:
        return self.repository.obtener_por_id(resultado_id)

    def crear(self, datos: dict) -> Resultado:
        resultado = Resultado(**datos)
        return self.repository.crear(resultado)

    def actualizar(self, resultado_id: int, datos: dict) -> Optional[Resultado]:
        resultado = self.repository.obtener_por_id(resultado_id)
        if resultado is None:
            return None

        for campo, valor in datos.items():
            if valor is not None:
                setattr(resultado, campo, valor)

        return self.repository.actualizar(resultado)

    def listar_por_validacion(self, validacion_id: int) -> list[Resultado]:
        return self.repository.obtener_por_validacion(validacion_id)
