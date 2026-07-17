"""
LABSYS DIALIZAR
Módulo: Seguridad
Historia: HU-005
Archivo: app/services/usuario_rol_service.py
"""

from app.models.usuario_rol import UsuarioRol
from app.repositories.usuario_rol_repository import UsuarioRolRepository


class UsuarioRolService:

    def __init__(self, repository: UsuarioRolRepository):
        self.repository = repository

    def listar(self):
        return self.repository.listar()

    def listar_por_usuario(self, usuario_id: int):
        return self.repository.listar_por_usuario(usuario_id)

    def asignar(self, datos: dict):
        existente = self.repository.obtener(
            datos["usuario_id"],
            datos["rol_id"],
        )

        if existente:
            raise ValueError("El usuario ya tiene asignado ese rol.")

        relacion = UsuarioRol(
            usuario_id=datos["usuario_id"],
            rol_id=datos["rol_id"],
        )

        return self.repository.crear(relacion)

    def quitar(self, usuario_id: int, rol_id: int):
        relacion = self.repository.obtener(usuario_id, rol_id)

        if relacion is None:
            return None

        self.repository.eliminar(relacion)
        return True
