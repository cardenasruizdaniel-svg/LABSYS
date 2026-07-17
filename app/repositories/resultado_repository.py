"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-015
Archivo: app/repositories/resultado_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resultado import Resultado


class ResultadoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Resultado]:
        stmt = select(Resultado).order_by(Resultado.fecha_creacion.desc())
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, resultado_id: int) -> Optional[Resultado]:
        return self.db.get(Resultado, resultado_id)

    def obtener_por_validacion(self, validacion_id: int) -> list[Resultado]:
        stmt = select(Resultado).where(Resultado.validacion_id == validacion_id)
        return list(self.db.scalars(stmt).all())

    def crear(self, resultado: Resultado) -> Resultado:
        self.db.add(resultado)
        self.db.commit()
        self.db.refresh(resultado)
        return resultado

    def actualizar(self, resultado: Resultado) -> Resultado:
        self.db.commit()
        self.db.refresh(resultado)
        return resultado
