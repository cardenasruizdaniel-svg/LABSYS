"""
LABSYS DIALIZAR
Módulo: Agenda
Archivo: app/repositories/cupo_diario_repository.py
"""

from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cupo_diario import CupoDiario


class CupoDiarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_por_fecha(self, fecha: date) -> Optional[CupoDiario]:
        stmt = select(CupoDiario).where(CupoDiario.fecha == fecha)
        return self.db.scalar(stmt)

    def crear_o_actualizar(self, fecha: date, cupo_maximo: int) -> CupoDiario:
        existente = self.obtener_por_fecha(fecha)

        if existente:
            existente.cupo_maximo = cupo_maximo
            self.db.commit()
            self.db.refresh(existente)
            return existente

        nuevo = CupoDiario(fecha=fecha, cupo_maximo=cupo_maximo)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
