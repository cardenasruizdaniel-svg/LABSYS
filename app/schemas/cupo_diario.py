"""
LABSYS DIALIZAR
Módulo: Agenda
Archivo: app/schemas/cupo_diario.py
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CupoDiarioCrear(BaseModel):
    fecha: date
    cupo_maximo: int = Field(gt=0)


class CupoDiarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: date
    cupo_maximo: int
