import os

from sqlalchemy import create_engine

from app.config.settings import settings

_database_url = settings.DATABASE_URL

print(f"[DB] DATABASE_URL env raw: '{os.environ.get('DATABASE_URL', '(no definida)')}'", flush=True)
print(f"[DB] All DB env vars:", flush=True)
for k, v in sorted(os.environ.items()):
    if "DATABASE" in k.upper() or "DB_" in k.upper() or "POSTGRES" in k.upper():
        print(f"  {k}={v}", flush=True)
print(f"[DB] Final URL: {_database_url}", flush=True)

engine = create_engine(
    _database_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
print("[DB] Engine created successfully", flush=True)
