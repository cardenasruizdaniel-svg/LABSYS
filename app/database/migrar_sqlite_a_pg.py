"""
LABSYS DIALIZAR
Migracion: Exporta datos de SQLite a PostgreSQL.
Solo migra tablas que tengan datos en SQLite.
Convierte booleanos de SQLite (0/1) a PostgreSQL (true/false).
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.database.session import SessionLocal
from sqlalchemy import text, inspect

SQLITE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "labsys.db"))

SKIP_TABLES = {"sqlite_sequence"}

# Orden por dependencias FK
TABLE_ORDER = [
    "departamentos", "ciudades", "eps", "roles", "permisos", "rol_permisos",
    "usuarios", "usuario_roles", "medicos", "convenios", "pacientes",
    "configuracion_laboratorio", "examenes", "parametros_examen",
    "ordenes", "orden_examenes", "muestras", "procesamientos", "validaciones",
    "resultados", "facturas", "caja_aperturas", "caja_cierres", "caja_ingresos",
    "citas", "items_inventario", "movimientos_inventario", "cupos_diarios",
]


def _is_bool_column(table_name, col_name):
    """Detecta columnas boolean por nombre comun."""
    bool_cols = {
        "activo", "cambiar_password", "copago_pagado", "critico",
        "es_particular", "tiene_copago", "acceso_movil",
    }
    return col_name in bool_cols


def migrar():
    if not os.path.exists(SQLITE_PATH):
        print(f"SQLite no encontrado: {SQLITE_PATH}")
        return

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    pg_session = SessionLocal()

    inspector = inspect(pg_session.get_bind())
    pg_tables = set(inspector.get_table_names())

    cursor = sqlite_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    all_tables = set(row[0] for row in cursor.fetchall())

    tables = [t for t in TABLE_ORDER if t in all_tables]
    tables += sorted(all_tables - set(tables) - SKIP_TABLES)

    total_rows = 0

    for table in tables:
        if table in SKIP_TABLES:
            continue

        if table not in pg_tables:
            print(f"  [SKIP] {table} - no existe en PostgreSQL")
            continue

        rows = sqlite_conn.execute(f'SELECT * FROM "{table}"').fetchall()
        if not rows:
            print(f"  [VACIO] {table}")
            continue

        col_names = [description[0] for description in sqlite_conn.execute(f'SELECT * FROM "{table}" LIMIT 0').description]

        pg_session.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))

        inserted = 0
        for row in rows:
            values = {}
            for i, col in enumerate(col_names):
                val = row[i]
                if _is_bool_column(table, col) and val is not None:
                    val = bool(val)
                values[col] = val

            placeholders = ", ".join([f":{c}" for c in col_names])
            columns = ", ".join([f'"{c}"' for c in col_names])
            sql = text(f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})')

            try:
                pg_session.execute(sql, values)
                inserted += 1
            except Exception as e:
                print(f"  [ERROR] {table}: {e}")
                pg_session.rollback()
                break
        else:
            pg_session.commit()
            total_rows += inserted
            print(f"  [OK] {table}: {inserted} filas")

    sqlite_conn.close()
    pg_session.close()

    print(f"\nMigracion completada: {total_rows} filas migradas.")

if __name__ == "__main__":
    migrar()
