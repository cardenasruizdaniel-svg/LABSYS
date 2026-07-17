"""
LABSYS DIALIZAR
Migracion: Agrega columnas SMTP a configuracion_laboratorio
"""
import sqlite3
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "labsys.db")

COLUMNS = [
    ("smtp_host", "TEXT"),
    ("smtp_port", "INTEGER"),
    ("smtp_user", "TEXT"),
    ("smtp_password", "TEXT"),
    ("smtp_from", "TEXT"),
]

def migrar():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("PRAGMA table_info(configuracion_laboratorio)")
    existing = {row[1] for row in cursor.fetchall()}

    for col, typedef in COLUMNS:
        if col not in existing:
            cursor.execute(f"ALTER TABLE configuracion_laboratorio ADD COLUMN {col} {typedef}")
            print(f"  + Columna agregada: {col} ({typedef})")
        else:
            print(f"  - Columna ya existe: {col}")

    conn.commit()
    conn.close()
    print("Migracion completada.")

if __name__ == "__main__":
    migrar()
