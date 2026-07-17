
"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-004
Archivo: app/services/permiso_service.py
"""

from typing import Optional

from app.models.permiso import Permiso
from app.repositories.permiso_repository import PermisoRepository


class PermisoService:

    def __init__(self, repository: PermisoRepository):
        self.repository = repository

    def listar(self) -> list[Permiso]:
        return self.repository.listar()

    def obtener_por_id(self, permiso_id: int) -> Optional[Permiso]:
        return self.repository.obtener_por_id(permiso_id)

    def crear(self, datos: dict) -> Permiso:
        existente = self.repository.obtener_por_codigo(datos["codigo"])
        if existente:
            raise ValueError("Ya existe un permiso con ese código.")

        permiso = Permiso(
            codigo=datos["codigo"],
            nombre=datos["nombre"],
            descripcion=datos.get("descripcion"),
            modulo=datos["modulo"],
            activo=True,
        )
        return self.repository.crear(permiso)

    def actualizar(self, permiso_id: int, datos: dict) -> Optional[Permiso]:
        permiso = self.repository.obtener_por_id(permiso_id)
        if permiso is None:
            return None

        permiso.codigo = datos["codigo"]
        permiso.nombre = datos["nombre"]
        permiso.descripcion = datos.get("descripcion")
        permiso.modulo = datos["modulo"]
        permiso.activo = datos["activo"]

        return self.repository.actualizar(permiso)

    def eliminar(self, permiso_id: int) -> Optional[Permiso]:
        permiso = self.repository.obtener_por_id(permiso_id)
        if permiso is None:
            return None

        return self.repository.desactivar(permiso)
