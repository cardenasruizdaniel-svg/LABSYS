"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-010
Archivo: app/services/convenio_service.py
"""

from typing import Optional

from app.models.convenio import Convenio
from app.repositories.convenio_repository import ConvenioRepository


class ConvenioService:

    def __init__(self, repository: ConvenioRepository):
        self.repository = repository

    def listar(self) -> list[Convenio]:
        return self.repository.listar()

    def obtener_por_id(self, convenio_id: int) -> Optional[Convenio]:
        return self.repository.obtener_por_id(convenio_id)

    def crear(self, datos: dict) -> Convenio:
        existente = self.repository.obtener_por_codigo(datos["codigo"])
        if existente:
            raise ValueError("Ya existe un convenio con ese código.")

        convenio = Convenio(**datos, activo=True)
        return self.repository.crear(convenio)

    def actualizar(self, convenio_id: int, datos: dict) -> Optional[Convenio]:
        convenio = self.repository.obtener_por_id(convenio_id)
        if convenio is None:
            return None

        for campo, valor in datos.items():
            setattr(convenio, campo, valor)

        return self.repository.actualizar(convenio)

    def eliminar(self, convenio_id: int) -> Optional[Convenio]:
        convenio = self.repository.obtener_por_id(convenio_id)
        if convenio is None:
            return None

        return self.repository.desactivar(convenio)
