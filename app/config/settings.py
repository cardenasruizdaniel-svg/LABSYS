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

    CUPO_DIARIO_DEFAULT = int(os.getenv("CUPO_DIARIO_DEFAULT", "40"))

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "LABSYS DIALIZAR <noreply@labsys.co>")

    @property
    def DATABASE_URL(self):
        url = os.environ.get("DATABASE_URL")
        if url and url.strip():
            return url.strip()
        host = os.getenv("DATABASE_HOST", "localhost")
        port = os.getenv("DATABASE_PORT", "5432")
        name = os.getenv("DATABASE_NAME", "labsys_dializar")
        user = os.getenv("DATABASE_USER", "postgres")
        password = os.getenv("DATABASE_PASSWORD", "postgres")
        return (
            f"postgresql+psycopg://"
            f"{user}:{password}"
            f"@{host}:{port}/"
            f"{name}"
        )


settings = Settings()
