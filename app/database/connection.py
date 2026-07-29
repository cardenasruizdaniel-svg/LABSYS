import os

from sqlalchemy import create_engine

from app.config.settings import settings

print(f"[DB] Connecting to: {settings.DATABASE_URL}", flush=True)

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
