"""
LABSYS DIALIZAR
Módulo: Gastos
Archivo: app/services/gasto_service.py
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.models.gasto import Gasto
from app.repositories.gasto_repository import GastoRepository


CATEGORIAS_GASTOS = [
    "Insumos médicos",
    "Reactivos",
    "Papelería y oficina",
    "Aseo y limpieza",
    "Mantenimiento equipos",
    "Servicios públicos",
    "Arriendo",
    "Nómina y prestaciones",
    "Transporte y logística",
    "Capacitación",
    "Imprevistos",
    "Otros",
]


class GastoService:

    def __init__(self, repository: GastoRepository):
        self.repository = repository

    def listar(self) -> list[Gasto]:
        return self.repository.listar()

    def obtener_por_id(self, gasto_id: int) -> Optional[Gasto]:
        return self.repository.obtener_por_id(gasto_id)

    def crear(self, datos: dict, usuario_id: Optional[int] = None) -> Gasto:
        gasto = Gasto(
            categoria=datos["categoria"],
            descripcion=datos["descripcion"],
            valor=Decimal(str(datos["valor"])),
            proveedor=datos.get("proveedor"),
            usuario_id=usuario_id,
            observaciones=datos.get("observaciones"),
        )
        return self.repository.crear(gasto)

    def actualizar(self, gasto_id: int, datos: dict) -> Optional[Gasto]:
        gasto = self.repository.obtener_por_id(gasto_id)
        if gasto is None:
            return None
        for k, v in datos.items():
            if v is not None:
                if k == "valor":
                    setattr(gasto, k, Decimal(str(v)))
                else:
                    setattr(gasto, k, v)
        return self.repository.actualizar(gasto)

    def eliminar(self, gasto_id: int) -> bool:
        return self.repository.eliminar(gasto_id)

    def total_gastos_hoy(self) -> Decimal:
        return self.repository.total_gastos_hoy()

    def gastos_por_categoria(self, desde: Optional[datetime] = None, hasta: Optional[datetime] = None) -> list[dict]:
        return self.repository.gastos_por_categoria(desde, hasta)

    def categorias_disponibles(self) -> list[str]:
        return CATEGORIAS_GASTOS
