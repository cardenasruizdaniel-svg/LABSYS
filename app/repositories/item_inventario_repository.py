"""
LABSYS DIALIZAR
Módulo: Inventario
Archivo: app/repositories/item_inventario_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item_inventario import ItemInventario


class ItemInventarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[ItemInventario]:
        stmt = select(ItemInventario).order_by(ItemInventario.nombre)
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, item_id: int) -> Optional[ItemInventario]:
        return self.db.get(ItemInventario, item_id)

    def obtener_por_codigo(self, codigo: str) -> Optional[ItemInventario]:
        stmt = select(ItemInventario).where(ItemInventario.codigo == codigo)
        return self.db.scalar(stmt)

    def listar_stock_bajo(self) -> list[ItemInventario]:
        stmt = (
            select(ItemInventario)
            .where(
                ItemInventario.activo == True,  # noqa: E712
                ItemInventario.stock_actual <= ItemInventario.stock_minimo,
            )
            .order_by(ItemInventario.nombre)
        )
        return list(self.db.scalars(stmt).all())

    def crear(self, item: ItemInventario) -> ItemInventario:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def actualizar(self, item: ItemInventario) -> ItemInventario:
        self.db.commit()
        self.db.refresh(item)
        return item

    def desactivar(self, item: ItemInventario) -> ItemInventario:
        item.activo = False
        self.db.commit()
        self.db.refresh(item)
        return item
