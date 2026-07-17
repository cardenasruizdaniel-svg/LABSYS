"""
LABSYS DIALIZAR
Modulo: Usuarios
Archivo: app/services/usuario_service.py
"""

from typing import Optional

from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.security.password import generar_hash


class UsuarioService:

    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def listar(self) -> list[Usuario]:
        return self.repository.listar()

    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.repository.obtener_por_id(usuario_id)

    def crear(self, datos: dict) -> Usuario:
        if self.repository.obtener_por_usuario(datos["usuario"]):
            raise ValueError("Ya existe un usuario con ese nombre de usuario.")

        if self.repository.obtener_por_documento(datos["documento"]):
            raise ValueError("Ya existe un usuario con ese documento.")

        entidad = Usuario(
            tipo_documento=datos["tipo_documento"],
            documento=datos["documento"],
            nombres=datos["nombres"],
            apellidos=datos["apellidos"],
            correo=datos["correo"],
            celular=datos.get("celular"),
            cargo=datos["cargo"],
            usuario=datos["usuario"],
            password_hash=generar_hash(datos["password"]),
            cambiar_password=True,
            activo=True,
            acceso_movil=datos.get("acceso_movil", False),
        )
        return self.repository.crear(entidad)

    def actualizar(self, usuario_id: int, datos: dict) -> Optional[Usuario]:
        entidad = self.repository.obtener_por_id(usuario_id)
        if entidad is None:
            return None

        entidad.tipo_documento = datos["tipo_documento"]
        entidad.documento = datos["documento"]
        entidad.nombres = datos["nombres"]
        entidad.apellidos = datos["apellidos"]
        entidad.correo = datos["correo"]
        entidad.celular = datos.get("celular")
        entidad.cargo = datos["cargo"]
        entidad.activo = datos["activo"]
        entidad.acceso_movil = datos.get("acceso_movil", False)

        return self.repository.actualizar(entidad)

    def resetear_password(self, usuario_id: int, nueva_password: str) -> Optional[Usuario]:
        entidad = self.repository.obtener_por_id(usuario_id)
        if entidad is None:
            return None

        entidad.password_hash = generar_hash(nueva_password)
        entidad.cambiar_password = True
        return self.repository.actualizar(entidad)

    def eliminar(self, usuario_id: int) -> Optional[Usuario]:
        entidad = self.repository.obtener_por_id(usuario_id)
        if entidad is None:
            return None
        return self.repository.desactivar(entidad)
