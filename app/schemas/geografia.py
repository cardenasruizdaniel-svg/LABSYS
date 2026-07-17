"""
LABSYS DIALIZAR
Modulo: Catalogos geograficos
Archivo: app/schemas/geografia.py
"""

from pydantic import BaseModel, ConfigDict


class DepartamentoCrear(BaseModel):
    nombre: str


class DepartamentoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str


class CiudadCrear(BaseModel):
    nombre: str
    departamento_id: int


class CiudadRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    departamento_id: int
