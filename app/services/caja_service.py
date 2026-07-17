"""
LABSYS DIALIZAR
Módulo: Facturación / Caja
Archivo: app/services/caja_service.py

Apertura y cierre de caja, con cuadre: cuánto se esperaba tener
(monto inicial + copagos cobrados + ingresos manuales − compras de inventario
pagadas en efectivo − gastos) contra cuánto se contó físicamente al cierre.
"""

import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.caja_apertura import CajaApertura
from app.models.caja_cierre import CajaCierre
from app.models.caja_ingreso import CajaIngreso
from app.models.factura import Factura
from app.models.gasto import Gasto
from app.models.movimiento_inventario import MovimientoInventario


class CajaService:

    def __init__(self, db: Session):
        self.db = db

    def apertura_activa(self) -> Optional[CajaApertura]:
        stmt = select(CajaApertura).where(CajaApertura.estado == "ABIERTA")
        return self.db.scalar(stmt)

    def listar_aperturas(self) -> list[CajaApertura]:
        stmt = select(CajaApertura).order_by(CajaApertura.fecha_apertura.desc())
        return list(self.db.scalars(stmt).all())

    def abrir_caja(self, monto_inicial: Decimal, usuario_id: Optional[int], observaciones: Optional[str]) -> CajaApertura:
        if self.apertura_activa() is not None:
            raise ValueError("Ya hay una caja abierta. Debe cerrarla antes de abrir una nueva.")

        apertura = CajaApertura(
            monto_inicial=monto_inicial,
            usuario_id=usuario_id,
            observaciones=observaciones,
            estado="ABIERTA",
        )
        self.db.add(apertura)
        self.db.commit()
        self.db.refresh(apertura)
        return apertura

    def _totales_del_periodo(self, desde: datetime, hasta: datetime) -> dict:
        copagos_stmt = select(Factura).where(
            Factura.copago_pagado == True,
            Factura.fecha_pago_copago >= desde,
            Factura.fecha_pago_copago <= hasta,
        )
        facturas_copago = list(self.db.scalars(copagos_stmt).all())
        total_copagos = sum((f.valor_copago for f in facturas_copago), Decimal("0"))

        facturado_stmt = select(Factura).where(
            Factura.fecha_emision >= desde,
            Factura.fecha_emision <= hasta,
        )
        facturas_emitidas = list(self.db.scalars(facturado_stmt).all())
        total_facturado = sum((f.total for f in facturas_emitidas), Decimal("0"))

        compras_stmt = select(MovimientoInventario).where(
            MovimientoInventario.tipo_movimiento == "ENTRADA",
            MovimientoInventario.costo_total.isnot(None),
            MovimientoInventario.fecha_movimiento >= desde,
            MovimientoInventario.fecha_movimiento <= hasta,
        )
        compras = list(self.db.scalars(compras_stmt).all())
        total_compras = sum((m.costo_total for m in compras), Decimal("0"))

        gastos_stmt = select(Gasto).where(
            Gasto.fecha_gasto >= desde,
            Gasto.fecha_gasto <= hasta,
        )
        gastos = list(self.db.scalars(gastos_stmt).all())
        total_gastos = sum((g.valor for g in gastos), Decimal("0"))

        ingresos_stmt = select(CajaIngreso).where(
            CajaIngreso.fecha_ingreso >= desde,
            CajaIngreso.fecha_ingreso <= hasta,
        )
        ingresos = list(self.db.scalars(ingresos_stmt).all())
        total_ingresos = sum((i.valor for i in ingresos), Decimal("0"))

        return {
            "total_copagos_cobrados": total_copagos,
            "total_facturado": total_facturado,
            "total_compras_inventario": total_compras,
            "total_gastos": total_gastos,
            "total_ingresos_manuales": total_ingresos,
            "cantidad_facturas": len(facturas_emitidas),
            "cantidad_compras": len(compras),
            "cantidad_gastos": len(gastos),
            "cantidad_ingresos": len(ingresos),
            "_facturas_detalle": facturas_emitidas,
            "_gastos_detalle": gastos,
            "_compras_detalle": compras,
            "_ingresos_detalle": ingresos,
        }

    def registrar_ingreso(self, apertura_id: int, valor: Decimal, origen: str, descripcion: Optional[str] = None, usuario_id: Optional[int] = None) -> CajaIngreso:
        ingreso = CajaIngreso(
            apertura_id=apertura_id,
            valor=valor,
            origen=origen,
            descripcion=descripcion,
            usuario_id=usuario_id,
        )
        self.db.add(ingreso)
        self.db.commit()
        self.db.refresh(ingreso)
        return ingreso

    def listar_ingresos(self, apertura_id: Optional[int] = None) -> list[CajaIngreso]:
        stmt = select(CajaIngreso).order_by(CajaIngreso.fecha_ingreso.desc())
        if apertura_id is not None:
            stmt = stmt.where(CajaIngreso.apertura_id == apertura_id)
        return list(self.db.scalars(stmt).all())

    def reporte_actual(self) -> dict:
        apertura = self.apertura_activa()
        if apertura is None:
            return {"hay_caja_abierta": False}

        ahora = datetime.now(timezone.utc)
        totales = self._totales_del_periodo(apertura.fecha_apertura, ahora)

        monto_esperado = (
            Decimal(apertura.monto_inicial)
            + totales["total_copagos_cobrados"]
            + totales["total_ingresos_manuales"]
            - totales["total_compras_inventario"]
            - totales["total_gastos"]
        )

        return {
            "hay_caja_abierta": True,
            "apertura_id": apertura.id,
            "fecha_apertura": apertura.fecha_apertura,
            "monto_inicial": apertura.monto_inicial,
            "monto_esperado_ahora": monto_esperado,
            **totales,
        }

    def cerrar_caja(self, monto_contado: Decimal, usuario_id: Optional[int], observaciones: Optional[str], denominaciones: Optional[dict] = None) -> CajaCierre:
        apertura = self.apertura_activa()
        if apertura is None:
            raise ValueError("No hay ninguna caja abierta para cerrar.")

        ahora = datetime.now(timezone.utc)
        totales = self._totales_del_periodo(apertura.fecha_apertura, ahora)

        monto_esperado = (
            Decimal(apertura.monto_inicial)
            + totales["total_copagos_cobrados"]
            + totales["total_ingresos_manuales"]
            - totales["total_compras_inventario"]
            - totales["total_gastos"]
        )
        diferencia = Decimal(monto_contado) - monto_esperado

        denominaciones_json = json.dumps(denominaciones) if denominaciones else None

        cierre = CajaCierre(
            apertura_id=apertura.id,
            monto_esperado=monto_esperado,
            monto_contado=monto_contado,
            diferencia=diferencia,
            total_copagos_cobrados=totales["total_copagos_cobrados"],
            total_facturado=totales["total_facturado"],
            total_compras_inventario=totales["total_compras_inventario"],
            total_gastos=totales["total_gastos"],
            denominaciones=denominaciones_json,
            usuario_id=usuario_id,
            observaciones=observaciones,
        )
        self.db.add(cierre)

        apertura.estado = "CERRADA"

        self.db.commit()
        self.db.refresh(cierre)
        return cierre

    def listar_cierres(self) -> list[CajaCierre]:
        stmt = select(CajaCierre).order_by(CajaCierre.fecha_cierre.desc())
        return list(self.db.scalars(stmt).all())

    def _rango_dia(self, d: date) -> tuple[datetime, datetime]:
        inicio = datetime.combine(d, datetime.min.time())
        fin = datetime.combine(d, datetime.max.time())
        return inicio, fin

    def cuadre_dia(self, d: date) -> dict:
        desde, hasta = self._rango_dia(d)
        totales = self._totales_del_periodo(desde, hasta)

        apertura = self.db.execute(
            select(CajaApertura).where(
                CajaApertura.fecha_apertura >= desde,
                CajaApertura.fecha_apertura <= hasta,
            )
        ).scalar_one_or_none()

        cierre = self.db.execute(
            select(CajaCierre).where(
                CajaCierre.fecha_cierre >= desde,
                CajaCierre.fecha_cierre <= hasta,
            )
        ).scalar_one_or_none()

        monto_inicial = float(apertura.monto_inicial) if apertura else 0

        facturas_detalle = []
        for f in totales["_facturas_detalle"]:
            facturas_detalle.append({
                "numero": f.numero,
                "total": float(f.total),
                "valor_copago": float(f.valor_copago),
                "estado": f.estado,
                "fecha": str(f.fecha_emision),
            })

        gastos_detalle = []
        for g in totales["_gastos_detalle"]:
            gastos_detalle.append({
                "categoria": g.categoria,
                "descripcion": g.descripcion,
                "valor": float(g.valor),
                "proveedor": g.proveedor or "",
                "fecha": str(g.fecha_gasto),
            })

        compras_detalle = []
        for m in totales["_compras_detalle"]:
            compras_detalle.append({
                "descripcion": getattr(m, "descripcion", None) or f"Movimiento #{m.id}",
                "costo_total": float(m.costo_total) if m.costo_total else 0,
                "fecha": str(m.fecha_movimiento),
            })

        ingresos_detalle = []
        for i in totales["_ingresos_detalle"]:
            ingresos_detalle.append({
                "origen": i.origen,
                "descripcion": i.descripcion or "",
                "valor": float(i.valor),
                "fecha": str(i.fecha_ingreso),
            })

        total_ingresos = float(totales["total_ingresos_manuales"])

        monto_esperado_calc = (
            monto_inicial
            + float(totales["total_copagos_cobrados"])
            + total_ingresos
            - float(totales["total_compras_inventario"])
            - float(totales["total_gastos"])
        )

        return {
            "fecha": str(d),
            "monto_inicial": monto_inicial,
            "facturacion": {
                "total_facturado": float(totales["total_facturado"]),
                "cantidad_facturas": totales["cantidad_facturas"],
                "detalle": facturas_detalle,
            },
            "copagos": {
                "total_cobrado": float(totales["total_copagos_cobrados"]),
            },
            "ingresos_manuales": {
                "total": total_ingresos,
                "cantidad": totales["cantidad_ingresos"],
                "detalle": ingresos_detalle,
            },
            "gastos": {
                "total": float(totales["total_gastos"]),
                "cantidad": totales["cantidad_gastos"],
                "detalle": gastos_detalle,
            },
            "compras_inventario": {
                "total": float(totales["total_compras_inventario"]),
                "cantidad": totales["cantidad_compras"],
                "detalle": compras_detalle,
            },
            "monto_esperado_calculado": monto_esperado_calc,
            "cuadre": {
                "monto_esperado": float(cierre.monto_esperado) if cierre else None,
                "monto_contado": float(cierre.monto_contado) if cierre else None,
                "diferencia": float(cierre.diferencia) if cierre else None,
                "denominaciones": json.loads(cierre.denominaciones) if cierre and cierre.denominaciones else None,
                "observaciones": cierre.observaciones if cierre else None,
                "fecha_cierre": str(cierre.fecha_cierre) if cierre else None,
            } if cierre else None,
        }

    def resumen_por_periodo(self, agrupacion: str) -> list[dict]:
        hoy = date.today()

        if agrupacion == "dia":
            inicio = hoy - timedelta(days=29)
            periodos = [(inicio + timedelta(days=i)) for i in range(30)]
            claves = [str(p) for p in periodos]
            groups = [(datetime.combine(p, datetime.min.time()), datetime.combine(p, datetime.max.time())) for p in periodos]

        elif agrupacion == "semana":
            inicio = hoy - timedelta(weeks=11)
            lunes_inicio = inicio - timedelta(days=inicio.weekday())
            periodos = []
            for i in range(12):
                lunes = lunes_inicio + timedelta(weeks=i)
                domingo = lunes + timedelta(days=6)
                periodos.append((lunes, domingo))
            claves = [f"{lunes.strftime('%d/%m')} - {domingo.strftime('%d/%m')}" for lunes, domingo in periodos]
            groups = [(datetime.combine(lunes, datetime.min.time()), datetime.combine(domingo, datetime.max.time())) for lunes, domingo in periodos]

        elif agrupacion == "mes":
            periodos = []
            for i in range(12):
                mes = (hoy.month - 11 + i) % 12 or 12
                anio = hoy.year if mes <= hoy.month else hoy.year - 1
                primer_dia = date(anio, mes, 1)
                if mes == 12:
                    ultimo_dia = date(anio + 1, 1, 1) - timedelta(days=1)
                else:
                    ultimo_dia = date(anio, mes + 1, 1) - timedelta(days=1)
                periodos.append((primer_dia, ultimo_dia))
            claves = [f"{p[0].strftime('%b %Y')}" for p in periodos]
            groups = [(datetime.combine(p[0], datetime.min.time()), datetime.combine(p[1], datetime.max.time())) for p in periodos]

        elif agrupacion == "anio":
            periodos = []
            for i in range(5):
                anio = hoy.year - 4 + i
                primer_dia = date(anio, 1, 1)
                ultimo_dia = date(anio, 12, 31)
                periodos.append((primer_dia, ultimo_dia))
            claves = [str(p[0].year) for p in periodos]
            groups = [(datetime.combine(p[0], datetime.min.time()), datetime.combine(p[1], datetime.max.time())) for p in periodos]

        else:
            return []

        resultado = []
        for clave, (desde, hasta) in zip(claves, groups):
            totales = self._totales_del_periodo(desde, hasta)
            resultado.append({
                "periodo": clave,
                "facturado": float(totales["total_facturado"]),
                "copagos_cobrados": float(totales["total_copagos_cobrados"]),
                "gastos": float(totales["total_gastos"]),
                "compras_inventario": float(totales["total_compras_inventario"]),
                "cantidad_facturas": totales["cantidad_facturas"],
                "cantidad_gastos": totales["cantidad_gastos"],
            })

        return resultado

    def resumen_por_rango(self, desde_str: str, hasta_str: str) -> list[dict]:
        desde = datetime.combine(date.fromisoformat(desde_str), datetime.min.time())
        hasta = datetime.combine(date.fromisoformat(hasta_str), datetime.max.time())

        totales = self._totales_del_periodo(desde, hasta)

        facturas_stmt = select(Factura).where(
            Factura.fecha_emision >= desde,
            Factura.fecha_emision <= hasta,
        )
        facturas = list(self.db.scalars(facturas_stmt).all())

        gastos_stmt = select(Gasto).where(
            Gasto.fecha_gasto >= desde,
            Gasto.fecha_gasto <= hasta,
        )
        gastos_list = list(self.db.scalars(gastos_stmt).all())

        por_categoria = {}
        for g in gastos_list:
            cat = g.categoria or "Otros"
            por_categoria[cat] = por_categoria.get(cat, 0) + float(g.valor or 0)

        return [{
            "periodo": f"{desde_str} al {hasta_str}",
            "facturado": float(totales["total_facturado"]),
            "copagos_cobrados": float(totales["total_copagos_cobrados"]),
            "gastos": float(totales["total_gastos"]),
            "compras_inventario": float(totales["total_compras_inventario"]),
            "cantidad_facturas": totales["cantidad_facturas"],
            "cantidad_gastos": totales["cantidad_gastos"],
            "gastos_por_categoria": [{"categoria": k, "total": v} for k, v in sorted(por_categoria.items(), key=lambda x: -x[1])],
        }]
