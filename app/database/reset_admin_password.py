"""
LABSYS DIALIZAR
Archivo: app/database/reset_admin_password.py

Uso:
    python -m app.database.reset_admin_password

Resetea la contraseña del usuario 'admin' a la contraseña por
defecto (Admin123*), sin afectar ningún otro dato del sistema.
Útil si el usuario admin quedó creado con un hash de contraseña
generado antes de corregir la versión de bcrypt.
"""

from app.database.session import SessionLocal
from app.database.seed_data import PASSWORD_ADMIN_INICIAL, USUARIO_ADMIN
from app.models.usuario import Usuario
from app.security.password import generar_hash


def resetear_password_admin() -> None:
    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.usuario == USUARIO_ADMIN).first()

        if admin is None:
            print(f"[reset] No existe ningún usuario '{USUARIO_ADMIN}'. Ejecute create_tables primero.")
            return

        admin.password_hash = generar_hash(PASSWORD_ADMIN_INICIAL)
        admin.activo = True
        db.commit()
        print(f"[reset] Contraseña de '{USUARIO_ADMIN}' restablecida a: {PASSWORD_ADMIN_INICIAL}")
    finally:
        db.close()


if __name__ == "__main__":
    resetear_password_admin()
