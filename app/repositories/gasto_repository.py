"""
LABSYS DIALIZAR
Módulo: Gastos
Archivo: app/repositories/gasto_repository.py
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.gasto import Gasto


class GastoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Gasto]:
        stmt = select(Gasto).order_by(Gasto.fecha_gasto.desc())
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, gasto_id: int) -> Optional[Gasto]:
        return self.db.get(Gasto, gasto_id)

    def crear(self, gasto: Gasto) -> Gasto:
        self.db.add(gasto)
        self.db.commit()
        self.db.refresh(gasto)
        return gasto

    def actualizar(self, gasto: Gasto) -> Gasto:
        self.db.commit()
        self.db.refresh(gasto)
        return gasto

    def eliminar(self, gasto_id: int) -> bool:
        gasto = self.db.get(Gasto, gasto_id)
        if gasto is None:
            return False
        self.db.delete(gasto)
        self.db.commit()
        return True

    def total_gastos_hoy(self) -> Decimal:
        hoy = date.today()
        resultado = self.db.query(func.coalesce(func.sum(Gasto.valor), 0)).filter(
            func.date(Gasto.fecha_gasto) == hoy
        ).scalar()
        return Decimal(str(resultado))

    def gastos_por_categoria(self, desde: Optional[datetime] = None, hasta: Optional[datetime] = None) -> list[dict]:
        stmt = select(Gasto.categoria, func.sum(Gasto.valor).label("total"))
        if desde:
            stmt = stmt.where(Gasto.fecha_gasto >= desde)
        if hasta:
            stmt = stmt.where(Gasto.fecha_gasto <= hasta)
        stmt = stmt.group_by(Gasto.categoria).order_by(func.sum(Gasto.valor).desc())
        resultados = self.db.execute(stmt).all()
        return [{"categoria": r[0], "total": Decimal(str(r[1]))} for r in resultados]
