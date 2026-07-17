
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-003
Archivo: app/services/rol_service.py
"""

from typing import Optional

from app.models.rol import Rol
from app.repositories.rol_repository import RolRepository


class RolService:

    def __init__(self, repository: RolRepository):
        self.repository = repository

    def listar(self) -> list[Rol]:
        return self.repository.listar()

    def obtener_por_id(self, rol_id: int) -> Optional[Rol]:
        return self.repository.obtener_por_id(rol_id)

    def crear(self, datos: dict) -> Rol:
        existente = self.repository.obtener_por_nombre(datos["nombre"])
        if existente:
            raise ValueError("Ya existe un rol con ese nombre.")

        rol = Rol(
            nombre=datos["nombre"],
            descripcion=datos.get("descripcion"),
            activo=True,
        )
        return self.repository.crear(rol)

    def actualizar(self, rol_id: int, datos: dict) -> Optional[Rol]:
        rol = self.repository.obtener_por_id(rol_id)
        if rol is None:
            return None

        rol.nombre = datos["nombre"]
        rol.descripcion = datos.get("descripcion")
        rol.activo = datos["activo"]

        return self.repository.actualizar(rol)

    def eliminar(self, rol_id: int) -> Optional[Rol]:
        rol = self.repository.obtener_por_id(rol_id)
        if rol is None:
            return None
        return self.repository.desactivar(rol)
