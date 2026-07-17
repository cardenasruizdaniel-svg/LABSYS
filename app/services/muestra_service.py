"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-012
Archivo: app/services/muestra_service.py
"""

from typing import Optional

from app.models.muestra import Muestra
from app.repositories.muestra_repository import MuestraRepository


class MuestraService:

    def __init__(self, repository: MuestraRepository):
        self.repository = repository

    def listar(self) -> list[Muestra]:
        return self.repository.listar()

    def obtener_por_id(self, muestra_id: int) -> Optional[Muestra]:
        return self.repository.obtener_por_id(muestra_id)

    def crear(self, datos: dict) -> Muestra:
        existente = self.repository.obtener_por_codigo_barras(
            datos["codigo_barras"]
        )
        if existente:
            raise ValueError("Ya existe una muestra con ese código de barras.")

        muestra = Muestra(**datos, estado="PENDIENTE")
        return self.repository.crear(muestra)

    def actualizar(self, muestra_id: int, datos: dict) -> Optional[Muestra]:
        muestra = self.repository.obtener_por_id(muestra_id)
        if muestra is None:
            return None

        for campo, valor in datos.items():
            if valor is not None:
                setattr(muestra, campo, valor)

        return self.repository.actualizar(muestra)
