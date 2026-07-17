"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-011
Archivo: app/repositories/orden_repository.py
"""

from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.orden import Orden


class OrdenRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Orden]:
        stmt = select(Orden).order_by(Orden.fecha_creacion.desc())
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, orden_id: int) -> Optional[Orden]:
        return self.db.get(Orden, orden_id)

    def obtener_por_numero(self, numero_orden: str) -> Optional[Orden]:
        stmt = select(Orden).where(Orden.numero_orden == numero_orden)
        return self.db.scalar(stmt)

    def listar_por_paciente(self, paciente_id: int) -> list[Orden]:
        stmt = (
            select(Orden)
            .where(Orden.paciente_id == paciente_id)
            .order_by(Orden.fecha_creacion.desc())
        )
        return list(self.db.scalars(stmt).all())

    def contar_hoy(self) -> int:
        hoy = date.today()
        return self.db.query(func.count(Orden.id)).filter(
            func.date(Orden.fecha_creacion) == hoy
        ).scalar() or 0

    def max_consecutivo(self) -> int:
        """Devuelve el mayor consecutivo global (extraído del número de orden).
        El consecutivo es secuencial independientemente del día."""
        resultados = self.db.query(Orden.numero_orden).all()
        if not resultados:
            return 0
        maximo = 0
        for (num,) in resultados:
            try:
                parte = num.split("-")[-1]
                n = int(parte)
                if n > maximo:
                    maximo = n
            except (ValueError, IndexError):
                pass
        return maximo

    def crear(self, orden: Orden) -> Orden:
        self.db.add(orden)
        self.db.commit()
        self.db.refresh(orden)
        return orden

    def actualizar(self, orden: Orden) -> Orden:
        self.db.commit()
        self.db.refresh(orden)
        return orden
