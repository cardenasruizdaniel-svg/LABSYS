
"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-007
Archivo: app/services/paciente_service.py

Lógica de negocio del módulo de pacientes.
"""

from typing import Optional

from app.models.paciente import Paciente
from app.repositories.paciente_repository import PacienteRepository


class PacienteService:

    def __init__(self, repository: PacienteRepository):
        self.repository = repository

    def listar(self) -> list[Paciente]:
        return self.repository.listar()

    def obtener_por_id(self, paciente_id: int) -> Optional[Paciente]:
        return self.repository.obtener_por_id(paciente_id)

    def crear(self, datos: dict) -> Paciente:
        existente = self.repository.obtener_por_documento(
            datos["documento"]
        )

        if existente:
            raise ValueError(
                "Ya existe un paciente con ese documento."
            )

        paciente = Paciente(
            **datos,
            activo=True,
        )

        return self.repository.crear(paciente)

    def actualizar(
        self,
        paciente_id: int,
        datos: dict,
    ) -> Optional[Paciente]:

        paciente = self.repository.obtener_por_id(
            paciente_id
        )

        if paciente is None:
            return None

        for campo, valor in datos.items():
            setattr(paciente, campo, valor)

        return self.repository.actualizar(paciente)

    def eliminar(
        self,
        paciente_id: int,
    ) -> Optional[Paciente]:

        paciente = self.repository.obtener_por_id(
            paciente_id
        )

        if paciente is None:
            return None

        return self.repository.desactivar(paciente)
