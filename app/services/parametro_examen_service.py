"""
LABSYS DIALIZAR
Módulo: Procesar y Validar
Archivo: app/services/parametro_examen_service.py
"""

from app.repositories.parametro_examen_repository import ParametroExamenRepository


class ParametroExamenService:

    def __init__(self, repository: ParametroExamenRepository):
        self.repository = repository

    def listar(self):
        return self.repository.listar()

    def obtener_por_id(self, parametro_id: int):
        return self.repository.obtener_por_id(parametro_id)

    def listar_por_examen(self, examen_id: int):
        return self.repository.listar_por_examen(examen_id)

    def listar_por_examenes(self, examenes_ids: list[int]):
        return self.repository.listar_por_examenes(examenes_ids)

    def crear(self, datos: dict):
        return self.repository.crear(datos)

    def actualizar(self, parametro_id: int, datos: dict):
        return self.repository.actualizar(parametro_id, datos)

    def eliminar(self, parametro_id: int):
        return self.repository.eliminar(parametro_id)
