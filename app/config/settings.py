import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    APP_NAME = os.getenv("APP_NAME", "LABSYS DIALIZAR")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))

    SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-esta-clave-en-produccion")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    # Cupo máximo de citas por día cuando no hay una configuración
    # especial para esa fecha en la tabla cupos_diarios.
    CUPO_DIARIO_DEFAULT = int(os.getenv("CUPO_DIARIO_DEFAULT", "40"))

    # --- Configuracion SMTP (correo electronico) ---
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "LABSYS DIALIZAR <noreply@labsys.co>")

    # Si DATABASE_URL viene definida en el .env (ej. sqlite:///data/labsys.db)
    # se usa directamente. Si no, se arma una URL de Postgres a partir de
    # las variables sueltas (util para despliegues en produccion).
    _DATABASE_URL_ENV = os.getenv("DATABASE_URL")

    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "labsys_dializar")
    DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")

    @property
    def DATABASE_URL(self):
        if self._DATABASE_URL_ENV:
            return self._DATABASE_URL_ENV

        return (
            f"postgresql+psycopg://"
            f"{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/"
            f"{self.DATABASE_NAME}"
        )


settings = Settings()
