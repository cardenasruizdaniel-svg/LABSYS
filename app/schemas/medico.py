"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-008
Archivo: app/schemas/medico.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

TIPOS_PROFESIONAL_VALIDOS = {"MEDICO", "ENFERMERO", "BACTERIOLOGO"}


class MedicoCrear(BaseModel):
    registro_medico: str
    nombres: str
    apellidos: str
    tipo_profesional: str = "MEDICO"
    especialidad: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None

    @field_validator("tipo_profesional")
    @classmethod
    def _validar_tipo(cls, v: str) -> str:
        v = v.upper()
        if v not in TIPOS_PROFESIONAL_VALIDOS:
            raise ValueError(f"tipo_profesional debe ser uno de: {', '.join(sorted(TIPOS_PROFESIONAL_VALIDOS))}")
        return v


class MedicoActualizar(MedicoCrear):
    activo: bool


class MedicoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registro_medico: str
    tipo_profesional: str
    nombres: str
    apellidos: str
    especialidad: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    firma_path: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
