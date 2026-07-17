"""
LABSYS DIALIZAR
Modulo: Laboratorio Clinico
Historia: HU-016
Archivo: app/services/factura_service.py
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from app.models.factura import Factura
from app.repositories.convenio_repository import ConvenioRepository
from app.repositories.factura_repository import FacturaRepository
from app.repositories.orden_repository import OrdenRepository
from app.repositories.paciente_repository import PacienteRepository


class FacturaService:

    def __init__(
        self,
        repository: FacturaRepository,
        convenio_repository: Optional[ConvenioRepository] = None,
        orden_repository: Optional[OrdenRepository] = None,
        paciente_repository: Optional[PacienteRepository] = None,
    ):
        self.repository = repository
        self.convenio_repository = convenio_repository
        self.orden_repository = orden_repository
        self.paciente_repository = paciente_repository

    def listar(self) -> list[Factura]:
        return self.repository.listar()

    def obtener_por_id(self, factura_id: int) -> Optional[Factura]:
        return self.repository.obtener_por_id(factura_id)

    def generar_numero_factura(self) -> tuple[str, int]:
        hoy = date.today()
        total_hoy = self.repository.contar_hoy()
        siguiente = total_hoy + 1
        numero = f"FAC-{hoy.strftime('%Y%m%d')}-{siguiente:02d}"
        return numero, siguiente

    def _paciente_tiene_copago(self, orden_id: int) -> Optional[bool]:
        """
        Si se puede determinar el paciente de la orden, devuelve su
        preferencia de copago (True/False). Si no se puede determinar
        (faltan repositorios o datos), devuelve None y se usa la
        configuración del convenio tal cual.
        """
        if not (self.orden_repository and self.paciente_repository):
            return None

        orden = self.orden_repository.obtener_por_id(orden_id)
        if orden is None:
            return None

        paciente = self.paciente_repository.obtener_por_id(orden.paciente_id)
        if paciente is None:
            return None

        return paciente.tiene_copago

    def _calcular_copago(self, convenio_id: int, total: Decimal, orden_id: Optional[int] = None) -> tuple[Decimal, Decimal]:
        """
        Devuelve (valor_copago, valor_cubierto_convenio). Si el paciente
        de la orden tiene marcado "no debe copago" (tiene_copago=False),
        eso tiene prioridad sobre la configuración del convenio: se
        factura 100% cubierto sin copago.
        """
        if orden_id is not None:
            preferencia_paciente = self._paciente_tiene_copago(orden_id)
            if preferencia_paciente is False:
                return Decimal("0.00"), total

        if self.convenio_repository is None:
            return Decimal("0.00"), total

        convenio = self.convenio_repository.obtener_por_id(convenio_id)
        if convenio is None:
            raise ValueError("El convenio indicado no existe.")

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

    def crear(self, datos: dict) -> Factura:
        if self.repository.obtener_por_numero(datos["numero"]):
            raise ValueError("Ya existe una factura con ese número.")

        subtotal = Decimal(datos.get("subtotal", 0))
        impuestos = Decimal(datos.get("impuestos", 0))
        total = subtotal + impuestos
        datos["total"] = total
        datos["estado"] = "BORRADOR"

        valor_copago, valor_cubierto = self._calcular_copago(
            datos["convenio_id"], total, datos.get("orden_id")
        )
        datos["valor_copago"] = valor_copago
        datos["valor_cubierto_convenio"] = valor_cubierto
        datos["copago_pagado"] = False

        return self.repository.crear(Factura(**datos))

    def actualizar(self, factura_id: int, datos: dict) -> Optional[Factura]:
        factura = self.repository.obtener_por_id(factura_id)
        if factura is None:
            return None

        for k, v in datos.items():
            setattr(factura, k, v)

        factura.total = Decimal(factura.subtotal) + Decimal(factura.impuestos)

        valor_copago, valor_cubierto = self._calcular_copago(
            factura.convenio_id, factura.total, factura.orden_id
        )
        factura.valor_copago = valor_copago
        factura.valor_cubierto_convenio = valor_cubierto

        return self.repository.actualizar(factura)

    def registrar_pago_copago(self, factura_id: int) -> Optional[Factura]:
        factura = self.repository.obtener_por_id(factura_id)
        if factura is None:
            return None

        if factura.copago_pagado:
            raise ValueError("El copago de esta factura ya estaba registrado como pagado.")

        factura.copago_pagado = True
        factura.fecha_pago_copago = datetime.now(timezone.utc)

        return self.repository.actualizar(factura)

    def cambiar_estado(self, factura_id: int, nuevo_estado: str) -> Optional[Factura]:
        factura = self.repository.obtener_por_id(factura_id)
        if factura is None:
            return None

        estados_validos = ("PENDIENTE", "PAGADO")
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado inválido. Use: {', '.join(estados_validos)}")

        factura.estado = nuevo_estado
        return self.repository.actualizar(factura)
