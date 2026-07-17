"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-011
Archivo: app/services/orden_service.py
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from app.models.examen import Examen
from app.models.factura import Factura
from app.models.orden import Orden
from app.models.orden_examen import OrdenExamen
from app.repositories.examen_repository import ExamenRepository
from app.repositories.orden_examen_repository import OrdenExamenRepository
from app.repositories.orden_repository import OrdenRepository
from app.repositories.factura_repository import FacturaRepository
from app.repositories.convenio_repository import ConvenioRepository


class OrdenService:

    def __init__(
        self,
        repository: OrdenRepository,
        orden_examen_repository: Optional[OrdenExamenRepository] = None,
        examen_repository: Optional[ExamenRepository] = None,
        factura_repository: Optional[FacturaRepository] = None,
        convenio_repository: Optional[ConvenioRepository] = None,
    ):
        self.repository = repository
        self.orden_examen_repository = orden_examen_repository
        self.examen_repository = examen_repository
        self.factura_repository = factura_repository
        self.convenio_repository = convenio_repository

    def listar(self) -> list[Orden]:
        return self.repository.listar()

    def obtener_por_id(self, orden_id: int) -> Optional[Orden]:
        return self.repository.obtener_por_id(orden_id)

    def generar_numero_orden(self) -> tuple[str, int]:
        """Genera el siguiente número de orden para hoy. Devuelve (numero, consecutivo)."""
        maximo = self.repository.max_consecutivo()
        siguiente = maximo + 1
        hoy = date.today()
        numero = f"ORD-{hoy.strftime('%Y%m%d')}-{siguiente:02d}"
        return numero, siguiente

    def contar_hoy(self) -> int:
        return self.repository.contar_hoy()

    def crear(self, datos: dict) -> Orden:
        numero, _ = self.generar_numero_orden()

        examenes_ids = datos.pop("examenes_ids", None) or []

        convenio_id = datos.get("convenio_id")

        if examenes_ids and self.examen_repository:
            for examen_id in examenes_ids:
                if self.examen_repository.obtener_por_id(examen_id) is None:
                    raise ValueError(f"El examen con id {examen_id} no existe.")

        ahora = datetime.now()
        orden = Orden(
            numero_orden=numero,
            paciente_id=datos["paciente_id"],
            medico_id=datos["medico_id"],
            eps_id=datos["eps_id"],
            convenio_id=convenio_id,
            prioridad=datos.get("prioridad", "NORMAL"),
            observaciones=datos.get("observaciones"),
            estado="REGISTRADA",
            fecha_creacion=ahora,
            fecha_actualizacion=ahora,
        )
        orden = self.repository.crear(orden)

        examenes_obj = []
        if examenes_ids and self.orden_examen_repository:
            for examen_id in examenes_ids:
                self.orden_examen_repository.crear(
                    OrdenExamen(orden_id=orden.id, examen_id=examen_id)
                )
                examen = self.examen_repository.obtener_por_id(examen_id)
                if examen:
                    examenes_obj.append(examen)
            self.orden_examen_repository.guardar_cambios()

        try:
            self._crear_factura_automatica(orden, convenio_id, examenes_obj)
        except Exception:
            pass

        return orden

    def _crear_factura_automatica(
        self,
        orden: Orden,
        convenio_id: Optional[int],
        examenes: list,
    ) -> Optional[Factura]:
        if not self.factura_repository or not convenio_id:
            return None

        subtotal = sum(Decimal(str(e.precio or 0)) for e in examenes)

        numero_factura, _ = self._generar_numero_factura()

        copago, cubierto = self._calcular_copago(convenio_id, subtotal)

        factura = Factura(
            numero=numero_factura,
            orden_id=orden.id,
            convenio_id=convenio_id,
            estado="PENDIENTE",
            subtotal=subtotal,
            impuestos=Decimal("0.00"),
            total=subtotal,
            valor_copago=copago,
            valor_cubierto_convenio=cubierto,
            copago_pagado=False,
        )
        return self.factura_repository.crear(factura)

    def _generar_numero_factura(self) -> tuple[str, int]:
        hoy = date.today()
        max_numero = self.factura_repository.max_numero_hoy()
        siguiente = max_numero + 1
        numero = f"FAC-{hoy.strftime('%Y%m%d')}-{siguiente:02d}"
        return numero, siguiente

    def _calcular_copago(
        self, convenio_id: int, total: Decimal
    ) -> tuple[Decimal, Decimal]:
        if not self.convenio_repository:
            return Decimal("0.00"), total

        convenio = self.convenio_repository.obtener_por_id(convenio_id)
        if convenio is None:
            return Decimal("0.00"), total

        tipo = convenio.tipo_copago
        valor_config = Decimal(convenio.valor_copago or 0)

        if tipo == "PORCENTAJE":
            valor_copago = (total * valor_config / Decimal("100")).quantize(Decimal("0.01"))
        elif tipo == "FIJO":
            valor_copago = min(valor_config, total)
        else:
            valor_copago = Decimal("0.00")

        valor_cubierto = total - valor_copago
        return valor_copago, valor_cubierto

    def actualizar(self, orden_id: int, datos: dict) -> Optional[Orden]:
        orden = self.repository.obtener_por_id(orden_id)
        if orden is None:
            return None

        for campo, valor in datos.items():
            setattr(orden, campo, valor)

        return self.repository.actualizar(orden)

    def listar_examenes(self, orden_id: int) -> list[dict]:
        if not (self.orden_examen_repository and self.examen_repository):
            return []

        relaciones = self.orden_examen_repository.listar_por_orden(orden_id)
        examenes = []
        for rel in relaciones:
            examen = self.examen_repository.obtener_por_id(rel.examen_id)
            if examen:
                examenes.append({
                    "orden_examen_id": rel.id,
                    "id": examen.id,
                    "codigo": examen.codigo,
                    "nombre": examen.nombre,
                    "categoria": examen.categoria,
                    "precio": examen.precio,
                    "tipo_muestra": examen.tipo_muestra,
                    "recipiente": examen.recipiente,
                    "activo": examen.activo,
                    "fecha_creacion": examen.fecha_creacion,
                    "fecha_actualizacion": examen.fecha_actualizacion,
                })
        return examenes
