"""
LABSYS DIALIZAR
Módulo: Inventario
Archivo: app/services/cierre_mes_service.py

Cierre de mes: mueve los movimientos de inventario (kárdex) de meses
anteriores a un archivo Excel en disco (data/cierres/), y los borra
de la base de datos activa para que esta se mantenga liviana.

IMPORTANTE: esto solo aplica a los MOVIMIENTOS de inventario (el
historial de entradas/salidas/ajustes). El stock_actual de cada
ítem NO se recalcula a partir de ese historial — ya es un valor
guardado aparte — así que archivar/borrar movimientos antiguos no
afecta el stock vigente.

Deliberadamente NO se aplica este mismo borrado a Órdenes, Muestras,
Resultados ni Facturas: son registros clínicos/financieros que
normalmente tienen requisitos legales de conservación, y borrarlos
sin ese análisis podría ser un problema de cumplimiento. Si se
necesita archivar esos módulos también, debe decidirse a propósito.
"""

import os
from datetime import date, datetime

from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item_inventario import ItemInventario
from app.models.movimiento_inventario import MovimientoInventario

CARPETA_CIERRES = os.path.join("data", "cierres")


def _primer_dia_mes_actual() -> date:
    hoy = date.today()
    return hoy.replace(day=1)


def listar_cierres_generados() -> list[dict]:
    if not os.path.isdir(CARPETA_CIERRES):
        return []

    archivos = []
    for nombre in sorted(os.listdir(CARPETA_CIERRES), reverse=True):
        if nombre.endswith(".xlsx"):
            ruta = os.path.join(CARPETA_CIERRES, nombre)
            archivos.append({
                "nombre_archivo": nombre,
                "tamano_kb": round(os.path.getsize(ruta) / 1024, 1),
                "fecha_generado": datetime.fromtimestamp(os.path.getmtime(ruta)).isoformat(),
            })
    return archivos


def ejecutar_cierre_mes(db: Session) -> dict:
    corte = _primer_dia_mes_actual()

    stmt = select(MovimientoInventario).where(MovimientoInventario.fecha_movimiento < corte)
    movimientos = list(db.scalars(stmt).all())

    if not movimientos:
        return {
            "archivado": 0,
            "mensaje": "No hay movimientos de inventario anteriores al mes actual para archivar.",
            "archivo": None,
        }

    items_por_id = {i.id: i for i in db.scalars(select(ItemInventario)).all()}

    wb = Workbook()
    ws = wb.active
    ws.title = "Movimientos"
    ws.append([
        "Fecha", "Ítem", "Código", "Tipo movimiento", "Cantidad",
        "Stock resultante", "Motivo", "Responsable", "Observaciones",
    ])

    for m in movimientos:
        item = items_por_id.get(m.item_id)
        ws.append([
            m.fecha_movimiento.strftime("%Y-%m-%d %H:%M") if m.fecha_movimiento else "",
            item.nombre if item else f"Ítem #{m.item_id}",
            item.codigo if item else "",
            m.tipo_movimiento,
            float(m.cantidad),
            float(m.stock_resultante),
            m.motivo,
            m.responsable or "",
            m.observaciones or "",
        ])

    os.makedirs(CARPETA_CIERRES, exist_ok=True)
    nombre_archivo = f"cierre_movimientos_{date.today().isoformat()}.xlsx"
    ruta_archivo = os.path.join(CARPETA_CIERRES, nombre_archivo)
    wb.save(ruta_archivo)

    cantidad = len(movimientos)
    for m in movimientos:
        db.delete(m)
    db.commit()

    return {
        "archivado": cantidad,
        "mensaje": f"Se archivaron {cantidad} movimiento(s) anteriores a {corte.isoformat()}.",
        "archivo": nombre_archivo,
    }
