"""
LABSYS DIALIZAR
Modulo: Dashboard Ejecutivo
Archivo: app/services/dashboard_service.py

Servicio completo de analytics para el dashboard ejecutivo.
"""

from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.eps import EPS
from app.models.examen import Examen
from app.models.factura import Factura
from app.models.gasto import Gasto
from app.models.item_inventario import ItemInventario
from app.models.medico import Medico
from app.models.movimiento_inventario import MovimientoInventario
from app.models.muestra import Muestra
from app.models.orden import Orden
from app.models.orden_examen import OrdenExamen
from app.models.paciente import Paciente
from app.models.procesamiento import Procesamiento
from app.models.validacion import Validacion
from app.models.resultado import Resultado
from app.models.caja_apertura import CajaApertura
from app.models.caja_cierre import CajaCierre


class DashboardService:

    def __init__(self, db: Session):
        self.db = db

    def _contar(self, modelo, *filtros) -> int:
        stmt = select(func.count()).select_from(modelo)
        if filtros:
            stmt = stmt.where(*filtros)
        return self.db.execute(stmt).scalar() or 0

    def _suma(self, modelo, columna, *filtros) -> float:
        stmt = select(func.coalesce(func.sum(columna), 0))
        if filtros:
            stmt = stmt.where(*filtros)
        return float(self.db.execute(stmt).scalar() or 0)

    # ================================================================
    # 1. KPIs PRINCIPALES
    # ================================================================

    def indicadores(self) -> dict:
        hoy = date.today()
        hoy_inicio = datetime.combine(hoy, datetime.min.time())
        hoy_fin = datetime.combine(hoy, datetime.max.time())

        primer_dia_mes = hoy.replace(day=1)
        if primer_dia_mes.month == 12:
            primer_dia_siguiente = primer_dia_mes.replace(year=primer_dia_mes.year + 1, month=1)
        else:
            primer_dia_siguiente = primer_dia_mes.replace(month=primer_dia_mes.month + 1)

        facturado_hoy = self._suma(
            Factura, Factura.total,
            Factura.fecha_emision >= hoy_inicio,
            Factura.fecha_emision <= hoy_fin,
        )
        facturado_mes = self._suma(
            Factura, Factura.total,
            Factura.fecha_emision >= primer_dia_mes,
            Factura.fecha_emision < primer_dia_siguiente,
        )
        copagos_pendientes = self._suma(
            Factura, Factura.valor_copago,
            Factura.copago_pagado == False,  # noqa: E712
        )

        ordenes_hoy = self._contar(
            Orden,
            Orden.fecha_creacion >= hoy_inicio,
            Orden.fecha_creacion <= hoy_fin,
            Orden.estado != "CANCELADA",
        )
        ordenes_mes = self._contar(
            Orden,
            Orden.fecha_creacion >= primer_dia_mes,
            Orden.fecha_creacion < primer_dia_siguiente,
            Orden.estado != "CANCELADA",
        )

        return {
            "pacientes": self._contar(Paciente, Paciente.activo == True),  # noqa: E712
            "ordenes_hoy": ordenes_hoy,
            "ordenes_mes": ordenes_mes,
            "facturado_hoy": facturado_hoy,
            "facturado_mes": facturado_mes,
            "copagos_pendientes": copagos_pendientes,
            "inventario_bajo": self._contar(
                ItemInventario,
                ItemInventario.activo == True,  # noqa: E712
                ItemInventario.stock_actual <= ItemInventario.stock_minimo,
            ),
        }

    # ================================================================
    # 2. INGRESOS Y FINANZAS
    # ================================================================

    def ingresos_vs_gastos(self, dias: int = 30) -> dict:
        hoy = date.today()
        desde = hoy - timedelta(days=dias)

        facturas = self.db.execute(
            select(
                func.date(Factura.fecha_emision).label("dia"),
                func.coalesce(func.sum(Factura.total), 0).label("total"),
            )
            .where(Factura.fecha_emision >= datetime.combine(desde, datetime.min.time()))
            .group_by(func.date(Factura.fecha_emision))
            .order_by(func.date(Factura.fecha_emision))
        ).all()

        gastos = self.db.execute(
            select(
                func.date(Gasto.fecha_gasto).label("dia"),
                func.coalesce(func.sum(Gasto.valor), 0).label("total"),
            )
            .where(Gasto.fecha_gasto >= datetime.combine(desde, datetime.min.time()))
            .group_by(func.date(Gasto.fecha_gasto))
            .order_by(func.date(Gasto.fecha_gasto))
        ).all()

        ingresos_map = {str(r.dia): float(r.total) for r in facturas}
        gastos_map = {str(r.dia): float(r.total) for r in gastos}

        fechas = []
        d = desde
        while d <= hoy:
            fechas.append(str(d))
            d += timedelta(days=1)

        return {
            "fechas": fechas,
            "ingresos": [ingresos_map.get(f, 0) for f in fechas],
            "gastos": [gastos_map.get(f, 0) for f in fechas],
        }

    def gastos_por_categoria(self, fecha_desde: date = None, fecha_hasta: date = None) -> dict:
        filtros = [Gasto.activo == True]  # noqa: E712
        if fecha_desde:
            filtros.append(Gasto.fecha_gasto >= datetime.combine(fecha_desde, datetime.min.time()))
        if fecha_hasta:
            filtros.append(Gasto.fecha_gasto <= datetime.combine(fecha_hasta, datetime.max.time()))

        rows = self.db.execute(
            select(
                Gasto.categoria,
                func.coalesce(func.sum(Gasto.valor), 0).label("total"),
            )
            .where(*filtros)
            .group_by(Gasto.categoria)
            .order_by(func.sum(Gasto.valor).desc())
        ).all()

        return {
            "categorias": [r.categoria for r in rows],
            "valores": [float(r.total) for r in rows],
        }

    def caja_estado(self) -> dict:
        apertura = self.db.execute(
            select(CajaApertura)
            .where(CajaApertura.estado == "ABIERTA")
            .order_by(CajaApertura.fecha_apertura.desc())
            .limit(1)
        ).scalars().first()

        if not apertura:
            return {"abierta": False, "mensaje": "Sin caja abierta"}

        cierre = self.db.execute(
            select(CajaCierre)
            .where(CajaCierre.apertura_id == apertura.id)
        ).scalars().first()

        return {
            "abierta": True,
            "monto_inicial": float(apertura.monto_inicial),
            "fecha_apertura": apertura.fecha_apertura.isoformat() if apertura.fecha_apertura else None,
            "cerrada": cierre is not None,
        }

    # ================================================================
    # 3. OPERACIONES DEL LABORATORIO
    # ================================================================

    def ordenes_hoy_por_estado(self) -> dict:
        hoy = date.today()
        hoy_inicio = datetime.combine(hoy, datetime.min.time())
        hoy_fin = datetime.combine(hoy, datetime.max.time())

        ordenes_hoy = self.db.execute(
            select(Orden).where(
                Orden.fecha_creacion >= hoy_inicio,
                Orden.fecha_creacion <= hoy_fin,
                Orden.estado != "CANCELADA",
            )
        ).scalars().all()

        orden_ids = [o.id for o in ordenes_hoy]
        if not orden_ids:
            return {"por_estado": {}, "total": 0, "ordenes": []}

        muestras_map = {}
        for m in self.db.execute(
            select(Muestra).where(Muestra.orden_id.in_(orden_ids))
        ).scalars().all():
            muestras_map[m.orden_id] = m

        muestra_ids = [m.id for m in muestras_map.values()]
        procs_map = {}
        if muestra_ids:
            for p in self.db.execute(
                select(Procesamiento).where(Procesamiento.muestra_id.in_(muestra_ids))
            ).scalars().all():
                procs_map[p.muestra_id] = p

        proc_ids = [p.id for p in procs_map.values()]
        vals_map = {}
        if proc_ids:
            for v in self.db.execute(
                select(Validacion).where(Validacion.procesamiento_id.in_(proc_ids))
            ).scalars().all():
                vals_map[v.procesamiento_id] = v

        paciente_ids = list({o.paciente_id for o in ordenes_hoy})
        pacientes_map = {}
        if paciente_ids:
            for p in self.db.execute(
                select(Paciente).where(Paciente.id.in_(paciente_ids))
            ).scalars().all():
                pacientes_map[p.id] = p

        por_estado = {"REGISTRADA": 0, "EN_MUESTRA": 0, "EN_PROCESAMIENTO": 0, "VALIDADO": 0}
        ordenes_detalle = []

        for o in ordenes_hoy:
            muestra = muestras_map.get(o.id)
            if not muestra:
                estado_calc = "REGISTRADA"
            elif not procs_map.get(muestra.id):
                estado_calc = "EN_MUESTRA"
            else:
                proc = procs_map[muestra.id]
                if proc and proc.id in vals_map:
                    estado_calc = "VALIDADO"
                else:
                    estado_calc = "EN_PROCESAMIENTO"

            por_estado[estado_calc] += 1
            paciente = pacientes_map.get(o.paciente_id)
            ordenes_detalle.append({
                "id": o.id,
                "numero_orden": o.numero_orden,
                "estado": estado_calc,
                "paciente": f"{paciente.primer_nombre} {paciente.primer_apellido}" if paciente else "-",
                "prioridad": o.prioridad,
            })

        return {"por_estado": por_estado, "total": len(ordenes_hoy), "ordenes": ordenes_detalle}

    def ordenes_por_dia(self, dias: int = 7) -> dict:
        hoy = date.today()
        desde = hoy - timedelta(days=dias - 1)

        rows = self.db.execute(
            select(
                func.date(Orden.fecha_creacion).label("dia"),
                func.count(Orden.id).label("total"),
            )
            .where(
                Orden.fecha_creacion >= datetime.combine(desde, datetime.min.time()),
                Orden.estado != "CANCELADA",
            )
            .group_by(func.date(Orden.fecha_creacion))
            .order_by(func.date(Orden.fecha_creacion))
        ).all()

        datos_map = {str(r.dia): r.total for r in rows}

        fechas = []
        d = desde
        while d <= hoy:
            fechas.append(d.strftime("%d/%m"))
            d += timedelta(days=1)

        fechas_completas = []
        d = desde
        while d <= hoy:
            fechas_completas.append(str(d))
            d += timedelta(days=1)

        return {
            "fechas": fechas,
            "totales": [datos_map.get(f, 0) for f in fechas_completas],
        }

    def examenes_top(self, limite: int = 8) -> dict:
        rows = self.db.execute(
            select(
                Examen.nombre,
                func.count(OrdenExamen.id).label("total"),
            )
            .join(Examen, OrdenExamen.examen_id == Examen.id)
            .group_by(Examen.nombre)
            .order_by(func.count(OrdenExamen.id).desc())
            .limit(limite)
        ).all()

        return {
            "nombres": [r.nombre[:25] for r in rows],
            "totales": [r.total for r in rows],
        }

    def medicos_top(self, limite: int = 8) -> dict:
        rows = self.db.execute(
            select(
                Medico.nombres,
                Medico.apellidos,
                func.count(Orden.id).label("total"),
            )
            .join(Medico, Orden.medico_id == Medico.id)
            .group_by(Medico.id)
            .order_by(func.count(Orden.id).desc())
            .limit(limite)
        ).all()

        return {
            "nombres": [f"{r.nombres} {r.apellidos}"[:25] for r in rows],
            "totales": [r.total for r in rows],
        }

    # ================================================================
    # 4. ANÁLISIS DE PACIENTES
    # ================================================================

    def pacientes_nuevos_por_mes(self, meses: int = 6) -> dict:
        hoy = date.today()
        desde = hoy.replace(day=1)
        for _ in range(meses - 1):
            if desde.month == 1:
                desde = desde.replace(year=desde.year - 1, month=12)
            else:
                desde = desde.replace(month=desde.month - 1)

        rows = self.db.execute(
            select(
                func.to_char(Paciente.fecha_creacion, 'YYYY-MM').label("mes"),
                func.count(Paciente.id).label("total"),
            )
            .where(Paciente.fecha_creacion >= datetime.combine(desde, datetime.min.time()))
            .group_by(func.to_char(Paciente.fecha_creacion, 'YYYY-MM'))
            .order_by(func.to_char(Paciente.fecha_creacion, 'YYYY-MM'))
        ).all()

        meses_nombres = {
            "01": "Ene", "02": "Feb", "03": "Mar", "04": "Abr",
            "05": "May", "06": "Jun", "07": "Jul", "08": "Ago",
            "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dic",
        }

        datos_map = {}
        for r in rows:
            partes = r.mes.split("-")
            clave = f"{meses_nombres.get(partes[1], partes[1])}/{partes[0][2:]}"
            datos_map[clave] = r.total

        labels = []
        d = desde
        while d <= hoy:
            clave = f"{meses_nombres.get(str(d.month).zfill(2), str(d.month))}/{str(d.year)[2:]}"
            labels.append(clave)
            if d.month == 12:
                d = d.replace(year=d.year + 1, month=1)
            else:
                d = d.replace(month=d.month + 1)

        return {
            "labels": labels,
            "totales": [datos_map.get(l, 0) for l in labels],
        }

    def pacientes_por_eps(self) -> dict:
        rows = self.db.execute(
            select(
                EPS.nombre,
                func.count(Paciente.id).label("total"),
            )
            .outerjoin(EPS, Paciente.eps_id == EPS.id)
            .where(Paciente.activo == True)  # noqa: E712
            .group_by(Paciente.eps_id)
            .order_by(func.count(Paciente.id).desc())
            .limit(10)
        ).all()

        nombres = []
        totales = []
        for r in rows:
            nombres.append(r.nombre or "Sin EPS")
            totales.append(r.total)

        return {"nombres": nombres, "totales": totales}

    # ================================================================
    # 5. INVENTARIO
    # ================================================================

    def inventario_por_categoria(self) -> dict:
        rows = self.db.execute(
            select(
                ItemInventario.categoria,
                func.count(ItemInventario.id).label("total_items"),
                func.coalesce(func.sum(ItemInventario.stock_actual), 0).label("stock_total"),
            )
            .where(ItemInventario.activo == True)  # noqa: E712
            .group_by(ItemInventario.categoria)
            .order_by(func.count(ItemInventario.id).desc())
        ).all()

        return {
            "categorias": [r.categoria for r in rows],
            "items": [r.total_items for r in rows],
            "stock": [float(r.stock_total) for r in rows],
        }

    def inventario_stock_bajo(self) -> list[dict]:
        items = self.db.execute(
            select(ItemInventario)
            .where(
                ItemInventario.activo == True,  # noqa: E712
                ItemInventario.stock_actual <= ItemInventario.stock_minimo,
            )
            .order_by(ItemInventario.stock_actual.asc())
            .limit(10)
        ).scalars().all()

        return [
            {
                "nombre": i.nombre,
                "categoria": i.categoria,
                "stock_actual": float(i.stock_actual),
                "stock_minimo": float(i.stock_minimo),
                "proveedor": i.proveedor or "-",
            }
            for i in items
        ]

    # ================================================================
    # 6. ALERTAS Y ACTIVIDAD
    # ================================================================

    def alertas(self) -> list[dict]:
        resultado = []

        items_bajos = self.db.execute(
            select(ItemInventario.nombre)
            .where(
                ItemInventario.activo == True,  # noqa: E712
                ItemInventario.stock_actual <= ItemInventario.stock_minimo,
            )
            .limit(5)
        ).scalars().all()
        if items_bajos:
            resultado.append({
                "titulo": "Inventario bajo",
                "mensaje": "Stock bajo en: " + ", ".join(items_bajos),
                "tipo": "warning",
            })

        copagos_pendientes = self._contar(Factura, Factura.copago_pagado == False)  # noqa: E712
        if copagos_pendientes:
            resultado.append({
                "titulo": "Copagos pendientes",
                "mensaje": f"Hay {copagos_pendientes} factura(s) con copago sin cobrar.",
                "tipo": "info",
            })

        apertura_abierta = self._contar(CajaApertura, CajaApertura.estado == "ABIERTA")
        cierre_hoy = self._contar(
            CajaCierre,
            func.date(CajaCierre.fecha_creacion) == date.today(),
        )
        if apertura_abierta > 0 and cierre_hoy == 0:
            resultado.append({
                "titulo": "Caja abierta",
                "mensaje": "Hay una caja abierta sin cierre de hoy.",
                "tipo": "warning",
            })

        if not resultado:
            resultado.append({
                "titulo": "Todo en orden",
                "mensaje": "Sin alertas críticas por el momento.",
                "tipo": "success",
            })

        return resultado

    def actividad_reciente(self) -> list[dict]:
        actividad = []

        ordenes_recientes = self.db.execute(
            select(Orden).order_by(Orden.fecha_creacion.desc()).limit(5)
        ).scalars().all()
        for o in ordenes_recientes:
            actividad.append({
                "fecha": o.fecha_creacion,
                "modulo": "Orden",
                "descripcion": f"Orden {o.numero_orden} creada (estado: {o.estado})",
            })

        facturas_recientes = self.db.execute(
            select(Factura).order_by(Factura.fecha_emision.desc()).limit(5)
        ).scalars().all()
        for f in facturas_recientes:
            actividad.append({
                "fecha": f.fecha_emision,
                "modulo": "Facturación",
                "descripcion": f"Factura {f.numero} por ${f.total:,.0f}",
            })

        gastos_recientes = self.db.execute(
            select(Gasto).order_by(Gasto.fecha_gasto.desc()).limit(5)
        ).scalars().all()
        for g in gastos_recientes:
            actividad.append({
                "fecha": g.fecha_gasto,
                "modulo": "Gastos",
                "descripcion": f"{g.categoria}: ${g.valor:,.0f} - {g.descripcion[:40]}",
            })

        movimientos_recientes = self.db.execute(
            select(MovimientoInventario).order_by(MovimientoInventario.fecha_movimiento.desc()).limit(5)
        ).scalars().all()
        for m in movimientos_recientes:
            actividad.append({
                "fecha": m.fecha_movimiento,
                "modulo": "Inventario",
                "descripcion": f"{m.tipo_movimiento}: {m.motivo[:40]}",
            })

        actividad.sort(key=lambda x: x["fecha"] or datetime.min, reverse=True)
        return actividad[:15]

    # ================================================================
    # DASHBOARD COMPLETO
    # ================================================================

    def dashboard(self) -> dict:
        return {
            "indicadores": self.indicadores(),
            "finanzas": {
                "ingresos_gastos": self.ingresos_vs_gastos(),
                "gastos_categoria": self.gastos_por_categoria(),
                "caja": self.caja_estado(),
            },
            "operaciones": {
                "ordenes_hoy": self.ordenes_hoy_por_estado(),
                "ordenes_dia": self.ordenes_por_dia(),
                "examenes_top": self.examenes_top(),
                "medicos_top": self.medicos_top(),
            },
            "pacientes": {
                "nuevos_mes": self.pacientes_nuevos_por_mes(),
                "por_eps": self.pacientes_por_eps(),
            },
            "inventario": {
                "por_categoria": self.inventario_por_categoria(),
                "stock_bajo": self.inventario_stock_bajo(),
            },
            "alertas": self.alertas(),
            "actividad": self.actividad_reciente(),
        }
