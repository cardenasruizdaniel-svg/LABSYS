"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-009
Archivo: app/services/eps_service.py
"""

from typing import Optional

from app.models.eps import EPS
from app.repositories.eps_repository import EPSRepository


class EPSService:

    def __init__(self, repository: EPSRepository):
        self.repository = repository

    def listar(self) -> list[EPS]:
        return self.repository.listar()

    def obtener_por_id(self, eps_id: int) -> Optional[EPS]:
        return self.repository.obtener_por_id(eps_id)

    def crear(self, datos: dict) -> EPS:
        existente = self.repository.obtener_por_codigo(datos["codigo"])
        if existente:
            raise ValueError("Ya existe una EPS con ese código.")

        eps = EPS(**datos, activo=True)
        return self.repository.crear(eps)

    def actualizar(self, eps_id: int, datos: dict) -> Optional[EPS]:
        eps = self.repository.obtener_por_id(eps_id)
        if eps is None:
            return None

        for campo, valor in datos.items():
            setattr(eps, campo, valor)

        return self.repository.actualizar(eps)

    def eliminar(self, eps_id: int) -> Optional[EPS]:
        eps = self.repository.obtener_por_id(eps_id)
        if eps is None:
            return None

        return self.repository.desactivar(eps)
