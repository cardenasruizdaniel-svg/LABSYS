"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-007
Archivo: app/schemas/paciente.py
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class PacienteCrear(BaseModel):
    tipo_documento: str
    documento: str
    primer_nombre: str
    segundo_nombre: Optional[str] = None
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: date
    sexo: str
    telefono: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[str] = None
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    es_particular: bool = True
    eps_id: Optional[int] = None
    tiene_copago: bool = False


class PacienteActualizar(PacienteCrear):
    activo: bool


class PacienteRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_documento: str
    documento: str
    primer_nombre: str
    segundo_nombre: Optional[str] = None
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: date
    sexo: str
    telefono: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[str] = None
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    es_particular: bool
    eps_id: Optional[int] = None
    tiene_copago: bool
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
