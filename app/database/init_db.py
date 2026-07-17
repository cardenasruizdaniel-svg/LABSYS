"""
LABSYS DIALIZAR
Archivo: app/database/init_db.py

Crea todas las tablas registradas en app/models a partir de los
modelos de SQLAlchemy. Es seguro ejecutarlo varias veces: solo
crea las tablas que todavia no existan.
"""

from app.database.base import Base
from app.database.connection import engine

# Importa (y por lo tanto registra en Base.metadata) todos los modelos.
import app.database.register_models  # noqa: F401


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)

    from app.database.seed_data import (
        seed_datos_particular,
        seed_usuario_admin,
        seed_examenes_base,
        seed_geografia_colombia,
        seed_roles_y_permisos,
        seed_parametros_examen,
    )
    seed_datos_particular()
    seed_usuario_admin()
    seed_examenes_base()
    seed_geografia_colombia()
    seed_roles_y_permisos()
    seed_parametros_examen()


if __name__ == "__main__":
    initialize_database()
