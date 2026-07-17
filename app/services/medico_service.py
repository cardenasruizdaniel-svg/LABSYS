"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-008
Archivo: app/services/medico_service.py
"""

from typing import Optional

from app.models.medico import Medico
from app.repositories.medico_repository import MedicoRepository


class MedicoService:

    def __init__(self, repository: MedicoRepository):
        self.repository = repository

    def listar(self) -> list[Medico]:
        return self.repository.listar()

    def obtener_por_id(self, medico_id: int) -> Optional[Medico]:
        return self.repository.obtener_por_id(medico_id)

    def crear(self, datos: dict) -> Medico:
        existente = self.repository.obtener_por_registro(
            datos["registro_medico"]
        )
        if existente:
            raise ValueError(
                "Ya existe un médico con ese registro profesional."
            )

        medico = Medico(**datos, activo=True)
        return self.repository.crear(medico)

    def actualizar(
        self,
        medico_id: int,
        datos: dict,
    ) -> Optional[Medico]:

        medico = self.repository.obtener_por_id(medico_id)

        if medico is None:
            return None

        for campo, valor in datos.items():
            setattr(medico, campo, valor)

        return self.repository.actualizar(medico)

    def eliminar(
        self,
        medico_id: int,
    ) -> Optional[Medico]:

        medico = self.repository.obtener_por_id(medico_id)

        if medico is None:
            return None

        return self.repository.desactivar(medico)

    def actualizar_firma(self, medico_id: int, firma_path: str) -> Optional[Medico]:
        medico = self.repository.obtener_por_id(medico_id)
        if medico is None:
            return None
        medico.firma_path = firma_path
        return self.repository.actualizar(medico)
