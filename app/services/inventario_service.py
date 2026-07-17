"""
LABSYS DIALIZAR
Módulo: Inventario
Archivo: app/services/inventario_service.py
"""

from decimal import Decimal
from typing import Optional

from app.models.item_inventario import ItemInventario
from app.models.movimiento_inventario import MovimientoInventario
from app.repositories.item_inventario_repository import ItemInventarioRepository
from app.repositories.movimiento_inventario_repository import MovimientoInventarioRepository


class InventarioService:

    def __init__(
        self,
        item_repository: ItemInventarioRepository,
        movimiento_repository: MovimientoInventarioRepository,
    ):
        self.item_repository = item_repository
        self.movimiento_repository = movimiento_repository

    # --------------------------------------------------------
    # Ítems
    # --------------------------------------------------------

    def listar_items(self) -> list[ItemInventario]:
        return self.item_repository.listar()

    def obtener_item(self, item_id: int) -> Optional[ItemInventario]:
        return self.item_repository.obtener_por_id(item_id)

    def listar_stock_bajo(self) -> list[ItemInventario]:
        return self.item_repository.listar_stock_bajo()

    def crear_item(self, datos: dict) -> ItemInventario:
        if self.item_repository.obtener_por_codigo(datos["codigo"]):
            raise ValueError("Ya existe un ítem de inventario con ese código.")

        stock_inicial = Decimal(datos.pop("stock_inicial", 0) or 0)

        item = ItemInventario(**datos, stock_actual=stock_inicial, activo=True)
        item = self.item_repository.crear(item)

        if stock_inicial > 0:
            self._registrar_movimiento(
                item=item,
                tipo_movimiento="ENTRADA",
                cantidad=stock_inicial,
                motivo="Stock inicial",
                responsable=None,
                observaciones=None,
            )

        return item

    def actualizar_item(self, item_id: int, datos: dict) -> Optional[ItemInventario]:
        item = self.item_repository.obtener_por_id(item_id)
        if item is None:
            return None

        for campo, valor in datos.items():
            if valor is not None:
                setattr(item, campo, valor)

        return self.item_repository.actualizar(item)

    def desactivar_item(self, item_id: int) -> Optional[ItemInventario]:
        item = self.item_repository.obtener_por_id(item_id)
        if item is None:
            return None
        return self.item_repository.desactivar(item)

    # --------------------------------------------------------
    # Movimientos (kárdex)
    # --------------------------------------------------------

    def _registrar_movimiento(
        self,
        item: ItemInventario,
        tipo_movimiento: str,
        cantidad: Decimal,
        motivo: str,
        responsable: Optional[str],
        observaciones: Optional[str],
        costo_total: Optional[Decimal] = None,
    ) -> MovimientoInventario:
        movimiento = MovimientoInventario(
            item_id=item.id,
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad,
            stock_resultante=item.stock_actual,
            motivo=motivo,
            responsable=responsable,
            observaciones=observaciones,
            costo_total=costo_total,
        )
        return self.movimiento_repository.crear(movimiento)

    def listar_movimientos(self) -> list[MovimientoInventario]:
        return self.movimiento_repository.listar()

    def listar_movimientos_de_item(self, item_id: int) -> list[MovimientoInventario]:
        return self.movimiento_repository.listar_por_item(item_id)

    def registrar_movimiento(self, datos: dict) -> MovimientoInventario:
        item = self.item_repository.obtener_por_id(datos["item_id"])
        if item is None:
            raise ValueError("El ítem de inventario indicado no existe.")

        tipo = datos["tipo_movimiento"]
        cantidad = Decimal(datos["cantidad"])

        if tipo == "ENTRADA":
            item.stock_actual = item.stock_actual + cantidad
        elif tipo == "SALIDA":
            if cantidad > item.stock_actual:
                raise ValueError(
                    f"Stock insuficiente: hay {item.stock_actual} {item.unidad_medida} "
                    f"disponibles y se solicitaron {cantidad}."
                )
            item.stock_actual = item.stock_actual - cantidad
        elif tipo == "AJUSTE":
            # Para AJUSTE, 'cantidad' es el nuevo stock absoluto (conteo físico).
            item.stock_actual = cantidad
        else:
            raise ValueError(f"tipo_movimiento '{tipo}' no válido.")

        self.item_repository.actualizar(item)

        return self._registrar_movimiento(
            item=item,
            tipo_movimiento=tipo,
            cantidad=cantidad,
            motivo=datos["motivo"],
            responsable=datos.get("responsable"),
            observaciones=datos.get("observaciones"),
            costo_total=datos.get("costo_total"),
        )
