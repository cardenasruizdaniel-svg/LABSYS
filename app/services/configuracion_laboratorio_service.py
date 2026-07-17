"""
LABSYS DIALIZAR
Módulo: Configuración
Archivo: app/services/configuracion_laboratorio_service.py
"""

from app.models.configuracion_laboratorio import ConfiguracionLaboratorio
from app.repositories.configuracion_laboratorio_repository import (
    ConfiguracionLaboratorioRepository,
)


class ConfiguracionLaboratorioService:

    def __init__(self, repository: ConfiguracionLaboratorioRepository):
        self.repository = repository

    def obtener(self) -> ConfiguracionLaboratorio:
        return self.repository.obtener()

    def actualizar(self, datos: dict) -> ConfiguracionLaboratorio:
        return self.repository.actualizar(datos)

    def actualizar_logo(self, logo_path: str) -> ConfiguracionLaboratorio:
        return self.repository.actualizar_logo(logo_path)
