"""
LABSYS DIALIZAR
Módulo: Configuración
Archivo: app/repositories/configuracion_laboratorio_repository.py
"""

from sqlalchemy.orm import Session

from app.models.configuracion_laboratorio import ConfiguracionLaboratorio


class ConfiguracionLaboratorioRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener(self) -> ConfiguracionLaboratorio:
        config = self.db.get(ConfiguracionLaboratorio, 1)

        if config is None:
            config = ConfiguracionLaboratorio(
                id=1,
                nombre_laboratorio="LABSYS DIALIZAR",
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)

        return config

    def actualizar(self, datos: dict) -> ConfiguracionLaboratorio:
        config = self.obtener()

        for campo, valor in datos.items():
            if valor is not None:
                setattr(config, campo, valor)

        self.db.commit()
        self.db.refresh(config)
        return config

    def actualizar_logo(self, logo_path: str) -> ConfiguracionLaboratorio:
        config = self.obtener()
        config.logo_path = logo_path
        self.db.commit()
        self.db.refresh(config)
        return config
