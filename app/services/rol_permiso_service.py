
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-006
Archivo: app/services/rol_permiso_service.py
"""

from app.models.rol_permiso import RolPermiso
from app.repositories.rol_permiso_repository import RolPermisoRepository


class RolPermisoService:

    def __init__(self, repository: RolPermisoRepository):
        self.repository = repository

    def listar(self):
        return self.repository.listar()

    def listar_por_rol(self, rol_id: int):
        return self.repository.listar_por_rol(rol_id)

    def asignar(self, datos: dict):
        existente = self.repository.obtener(
            datos["rol_id"],
            datos["permiso_id"],
        )

        if existente:
            raise ValueError("El rol ya tiene asignado ese permiso.")

        relacion = RolPermiso(
            rol_id=datos["rol_id"],
            permiso_id=datos["permiso_id"],
        )

        return self.repository.crear(relacion)

    def quitar(self, rol_id: int, permiso_id: int):
        relacion = self.repository.obtener(rol_id, permiso_id)

        if relacion is None:
            return None

        self.repository.eliminar(relacion)
        return True
