"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-010
Archivo: app/schemas/convenio.py
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

TIPOS_COPAGO_VALIDOS = {"NINGUNO", "FIJO", "PORCENTAJE"}


class ConvenioCrear(BaseModel):
    eps_id: int
    codigo: str
    nombre: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    observaciones: Optional[str] = None
    tipo_copago: str = "NINGUNO"
    valor_copago: Decimal = Decimal("0.00")

    @field_validator("tipo_copago")
    @classmethod
    def _validar_tipo_copago(cls, v: str) -> str:
        v = v.upper()
        if v not in TIPOS_COPAGO_VALIDOS:
            raise ValueError(
                f"tipo_copago debe ser uno de: {', '.join(sorted(TIPOS_COPAGO_VALIDOS))}"
            )
        return v

    @model_validator(mode="after")
    def _validar_porcentaje(self):
        if self.tipo_copago == "PORCENTAJE" and not (0 <= self.valor_copago <= 100):
            raise ValueError("Si tipo_copago es PORCENTAJE, valor_copago debe estar entre 0 y 100.")
        if self.valor_copago < 0:
            raise ValueError("valor_copago no puede ser negativo.")
        return self


class ConvenioActualizar(ConvenioCrear):
    activo: bool


class ConvenioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    eps_id: int
    codigo: str
    nombre: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    observaciones: Optional[str] = None
    tipo_copago: str
    valor_copago: Decimal
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
