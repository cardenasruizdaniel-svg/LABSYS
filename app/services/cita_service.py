"""
LABSYS DIALIZAR
Módulo: Agenda
Archivo: app/services/cita_service.py
"""

from datetime import date

from app.config.settings import settings
from app.models.cita import Cita
from app.repositories.cita_repository import CitaRepository
from app.repositories.cupo_diario_repository import CupoDiarioRepository

ESTADOS_VALIDOS = {
    "PROGRAMADA",
    "CONFIRMADA",
    "ATENDIDA",
    "CANCELADA",
    "NO_ASISTIO",
}


class CitaService:

    def __init__(
        self,
        repository: CitaRepository,
        cupo_repository: CupoDiarioRepository,
    ):
        self.repository = repository
        self.cupo_repository = cupo_repository

    def listar(self) -> list[Cita]:
        return self.repository.listar()

    def obtener_por_id(self, cita_id: int):
        return self.repository.obtener_por_id(cita_id)

    def listar_por_fecha(self, fecha: date) -> list[Cita]:
        return self.repository.listar_por_fecha(fecha)

    def listar_por_paciente(self, paciente_id: int) -> list[Cita]:
        return self.repository.listar_por_paciente(paciente_id)

    def cupo_maximo_de(self, fecha: date) -> int:
        override = self.cupo_repository.obtener_por_fecha(fecha)
        if override:
            return override.cupo_maximo
        return settings.CUPO_DIARIO_DEFAULT

    def disponibilidad(self, fecha: date) -> dict:
        cupo_maximo = self.cupo_maximo_de(fecha)
        cupo_usado = self.repository.contar_activas_por_fecha(fecha)
        return {
            "fecha": fecha,
            "cupo_maximo": cupo_maximo,
            "cupo_usado": cupo_usado,
            "cupo_disponible": max(cupo_maximo - cupo_usado, 0),
        }

    def _validar_cupo_disponible(self, fecha: date) -> None:
        disp = self.disponibilidad(fecha)
        if disp["cupo_disponible"] <= 0:
            raise ValueError(
                f"No hay cupo disponible para el {fecha.isoformat()} "
                f"(cupo máximo: {disp['cupo_maximo']})."
            )

    def crear(self, datos: dict) -> Cita:
        self._validar_cupo_disponible(datos["fecha_cita"])

        orden_id = datos.get("orden_id")

        cita = Cita(
            paciente_id=datos["paciente_id"],
            orden_id=orden_id,
            medico_id=datos.get("medico_id"),
            fecha_cita=datos["fecha_cita"],
            hora_cita=datos.get("hora_cita"),
            observaciones=datos.get("observaciones"),
            tipo_atencion="CON_ORDEN" if orden_id else "PARTICULAR",
            es_particular=orden_id is None,
            estado="PROGRAMADA",
        )

        return self.repository.crear(cita)

    def asociar_orden(self, cita_id: int, orden_id: int):
        cita = self.repository.obtener_por_id(cita_id)
        if cita is None:
            return None

        cita.orden_id = orden_id
        cita.tipo_atencion = "CON_ORDEN"
        cita.es_particular = False

        return self.repository.actualizar(cita)

    def cambiar_estado(self, cita_id: int, estado: str):
        estado = estado.upper()
        if estado not in ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado '{estado}' no válido. Use uno de: "
                f"{', '.join(sorted(ESTADOS_VALIDOS))}."
            )

        cita = self.repository.obtener_por_id(cita_id)
        if cita is None:
            return None

        cita.estado = estado
        return self.repository.actualizar(cita)

    def actualizar(self, cita_id: int, datos: dict):
        cita = self.repository.obtener_por_id(cita_id)
        if cita is None:
            return None

        nueva_fecha = datos.get("fecha_cita")
        if nueva_fecha and nueva_fecha != cita.fecha_cita:
            self._validar_cupo_disponible(nueva_fecha)
            cita.fecha_cita = nueva_fecha

        if datos.get("medico_id") is not None:
            cita.medico_id = datos["medico_id"]

        if datos.get("hora_cita") is not None:
            cita.hora_cita = datos["hora_cita"]

        if datos.get("observaciones") is not None:
            cita.observaciones = datos["observaciones"]

        if datos.get("estado"):
            estado = datos["estado"].upper()
            if estado not in ESTADOS_VALIDOS:
                raise ValueError(f"Estado '{estado}' no válido.")
            cita.estado = estado

        return self.repository.actualizar(cita)

    def cancelar(self, cita_id: int):
        return self.cambiar_estado(cita_id, "CANCELADA")

    def configurar_cupo(self, fecha: date, cupo_maximo: int):
        return self.cupo_repository.crear_o_actualizar(fecha, cupo_maximo)
