"""
LABSYS DIALIZAR
Módulo: Configuración
Archivo: app/schemas/configuracion_laboratorio.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ConfiguracionLaboratorioActualizar(BaseModel):
    nombre_laboratorio: Optional[str] = None
    nit: Optional[str] = None
    resolucion_habilitacion: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    ciudad: Optional[str] = None
    pie_pagina: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: Optional[str] = None


class ConfiguracionLaboratorioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_laboratorio: str
    nit: Optional[str] = None
    resolucion_habilitacion: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    ciudad: Optional[str] = None
    logo_path: Optional[str] = None
    pie_pagina: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_from: Optional[str] = None
    fecha_actualizacion: datetime
