"""
LABSYS DIALIZAR
Modulo: Inventario
Archivo: app/routers/inventario.py

CRUD de items de inventario (reactivos/insumos) y registro de
movimientos (entradas, salidas, ajustes) con actualizacion
automatica de stock.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.item_inventario_repository import ItemInventarioRepository
from app.repositories.movimiento_inventario_repository import MovimientoInventarioRepository
from app.schemas.item_inventario import (
    ItemInventarioActualizar,
    ItemInventarioCrear,
    ItemInventarioRespuesta,
)
from app.schemas.movimiento_inventario import (
    MovimientoInventarioCrear,
    MovimientoInventarioRespuesta,
)
from app.services.cierre_mes_service import (
    CARPETA_CIERRES,
    ejecutar_cierre_mes,
    listar_cierres_generados,
)
from app.services.inventario_service import InventarioService

router = APIRouter(prefix="/inventario", tags=["Inventario"])


def get_service(db: Session) -> InventarioService:
    return InventarioService(ItemInventarioRepository(db), MovimientoInventarioRepository(db))


# ---------------------------------------------------------------
# Items
# ---------------------------------------------------------------

@router.get("/items", response_model=list[ItemInventarioRespuesta])
def listar_items(db: Session = Depends(get_db)):
    return get_service(db).listar_items()


@router.get("/items/stock-bajo", response_model=list[ItemInventarioRespuesta])
def listar_stock_bajo(db: Session = Depends(get_db)):
    return get_service(db).listar_stock_bajo()


@router.get("/items/{item_id}", response_model=ItemInventarioRespuesta)
def obtener_item(item_id: int, db: Session = Depends(get_db)):
    item = get_service(db).obtener_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Ítem de inventario no encontrado")
    return item


@router.post("/items", response_model=ItemInventarioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_item(datos: ItemInventarioCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).crear_item(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/items/{item_id}", response_model=ItemInventarioRespuesta)
def actualizar_item(item_id: int, datos: ItemInventarioActualizar, db: Session = Depends(get_db)):
    item = get_service(db).actualizar_item(item_id, datos.model_dump(exclude_unset=True))
    if item is None:
        raise HTTPException(status_code=404, detail="Ítem de inventario no encontrado")
    return item


@router.delete("/items/{item_id}")
def desactivar_item(item_id: int, db: Session = Depends(get_db)):
    item = get_service(db).desactivar_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Ítem de inventario no encontrado")
    return {"success": True, "message": "Ítem desactivado correctamente"}


# ---------------------------------------------------------------
# Movimientos (kárdex)
# ---------------------------------------------------------------

@router.get("/movimientos", response_model=list[MovimientoInventarioRespuesta])
def listar_movimientos(item_id: int | None = None, db: Session = Depends(get_db)):
    servicio = get_service(db)
    if item_id:
        return servicio.listar_movimientos_de_item(item_id)
    return servicio.listar_movimientos()


@router.post("/movimientos", response_model=MovimientoInventarioRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_movimiento(datos: MovimientoInventarioCrear, db: Session = Depends(get_db)):
    try:
        return get_service(db).registrar_movimiento(datos.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# ---------------------------------------------------------------
# Cierre de mes (archivar movimientos antiguos, mantener el
# sistema liviano)
# ---------------------------------------------------------------

@router.get("/cierres")
def listar_cierres():
    return listar_cierres_generados()


@router.post("/cierre-mes")
def cerrar_mes(db: Session = Depends(get_db)):
    return ejecutar_cierre_mes(db)


@router.get("/cierres/{nombre_archivo}/descargar")
def descargar_cierre(nombre_archivo: str):
    import os
    ruta = os.path.join(CARPETA_CIERRES, nombre_archivo)
    if ".." in nombre_archivo or not os.path.isfile(ruta):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    with open(ruta, "rb") as f:
        contenido = f.read()

    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )
