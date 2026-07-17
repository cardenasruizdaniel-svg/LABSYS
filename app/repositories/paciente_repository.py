
"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-007
Archivo: app/repositories/paciente_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.paciente import Paciente


class PacienteRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Paciente]:
        stmt = select(Paciente).order_by(
            Paciente.primer_apellido,
            Paciente.primer_nombre,
        )
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, paciente_id: int) -> Optional[Paciente]:
        return self.db.get(Paciente, paciente_id)

    def obtener_por_documento(self, documento: str) -> Optional[Paciente]:
        stmt = select(Paciente).where(Paciente.documento == documento)
        return self.db.scalar(stmt)

    def crear(self, paciente: Paciente) -> Paciente:
        self.db.add(paciente)
        self.db.commit()
        self.db.refresh(paciente)
        return paciente

    def actualizar(self, paciente: Paciente) -> Paciente:
        self.db.commit()
        self.db.refresh(paciente)
        return paciente

    def desactivar(self, paciente: Paciente) -> Paciente:
        paciente.activo = False
        self.db.commit()
        self.db.refresh(paciente)
        return paciente
