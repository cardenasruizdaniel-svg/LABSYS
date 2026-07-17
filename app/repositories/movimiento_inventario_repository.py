"""
LABSYS DIALIZAR
Módulo: Inventario
Archivo: app/repositories/movimiento_inventario_repository.py
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movimiento_inventario import MovimientoInventario


class MovimientoInventarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[MovimientoInventario]:
        stmt = select(MovimientoInventario).order_by(MovimientoInventario.fecha_movimiento.desc())
        return list(self.db.scalars(stmt).all())

    def listar_por_item(self, item_id: int) -> list[MovimientoInventario]:
        stmt = (
            select(MovimientoInventario)
            .where(MovimientoInventario.item_id == item_id)
            .order_by(MovimientoInventario.fecha_movimiento.desc())
        )
        return list(self.db.scalars(stmt).all())

    def crear(self, movimiento: MovimientoInventario) -> MovimientoInventario:
        self.db.add(movimiento)
        self.db.commit()
        self.db.refresh(movimiento)
        return movimiento
