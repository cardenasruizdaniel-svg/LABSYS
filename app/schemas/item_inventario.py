"""
LABSYS DIALIZAR
Módulo: Inventario
Archivo: app/schemas/item_inventario.py
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

CATEGORIAS_VALIDAS = {"REACTIVO", "INSUMO", "PAPELERIA", "ASEO", "UTENSILIO", "EQUIPO", "OTRO"}


class ItemInventarioCrear(BaseModel):
    codigo: str
    nombre: str
    categoria: str = "INSUMO"
    unidad_medida: str
    stock_minimo: Decimal = Decimal("0")
    precio_unitario: Optional[Decimal] = None
    proveedor: Optional[str] = None
    fecha_vencimiento: Optional[date] = None
    stock_inicial: Decimal = Decimal("0")

    @field_validator("categoria")
    @classmethod
    def _validar_categoria(cls, v: str) -> str:
        v = v.upper()
        if v not in CATEGORIAS_VALIDAS:
            raise ValueError(f"categoria debe ser una de: {', '.join(sorted(CATEGORIAS_VALIDAS))}")
        return v


class ItemInventarioActualizar(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    unidad_medida: Optional[str] = None
    stock_minimo: Optional[Decimal] = None
    precio_unitario: Optional[Decimal] = None
    proveedor: Optional[str] = None
    fecha_vencimiento: Optional[date] = None


class ItemInventarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    categoria: str
    unidad_medida: str
    stock_actual: Decimal
    stock_minimo: Decimal
    precio_unitario: Optional[Decimal] = None
    proveedor: Optional[str] = None
    fecha_vencimiento: Optional[date] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
