"""
LABSYS DIALIZAR
Módulo: Resultados
Archivo: app/services/resultado_pdf_service.py

Genera el PDF imprimible de resultados de una orden de laboratorio,
con membrete (logo + datos del laboratorio), datos del paciente y
del médico remitente, y la tabla de resultados por examen.
También arma el PDF de historial de resultados de un paciente
(varias órdenes en un mismo documento).
"""

import os
from datetime import date, datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.configuracion_laboratorio import ConfiguracionLaboratorio
from app.models.orden import Orden
from app.models.paciente import Paciente
from app.repositories.configuracion_laboratorio_repository import (
    ConfiguracionLaboratorioRepository,
)
from app.repositories.medico_repository import MedicoRepository
from app.repositories.muestra_repository import MuestraRepository
from app.repositories.orden_repository import OrdenRepository
from app.repositories.paciente_repository import PacienteRepository
from app.repositories.procesamiento_repository import ProcesamientoRepository
from app.repositories.resultado_repository import ResultadoRepository
from app.repositories.validacion_repository import ValidacionRepository

AZUL_LAB = colors.HexColor("#0B5ED7")
GRIS_TEXTO = colors.HexColor("#333333")


class ResultadoPdfService:

    def __init__(
        self,
        orden_repository: OrdenRepository,
        paciente_repository: PacienteRepository,
        medico_repository: MedicoRepository,
        muestra_repository: MuestraRepository,
        procesamiento_repository: ProcesamientoRepository,
        validacion_repository: ValidacionRepository,
        resultado_repository: ResultadoRepository,
        configuracion_repository: ConfiguracionLaboratorioRepository,
    ):
        self.orden_repository = orden_repository
        self.paciente_repository = paciente_repository
        self.medico_repository = medico_repository
        self.muestra_repository = muestra_repository
        self.procesamiento_repository = procesamiento_repository
        self.validacion_repository = validacion_repository
        self.resultado_repository = resultado_repository
        self.configuracion_repository = configuracion_repository

    # ------------------------------------------------------------
    # Recolección de datos
    # ------------------------------------------------------------

    def _resultados_de_orden(self, orden_id: int) -> list[dict]:
        filas = []

        muestras = self.muestra_repository.listar_por_orden(orden_id)

        for muestra in muestras:
            procesamiento = self.procesamiento_repository.obtener_por_muestra(muestra.id)
            if procesamiento is None:
                continue

            validacion = self.validacion_repository.obtener_por_procesamiento(procesamiento.id)
            if validacion is None:
                continue

            resultados = self.resultado_repository.obtener_por_validacion(validacion.id)

            for resultado in resultados:
                filas.append({
                    "examen": resultado.examen,
                    "resultado": resultado.resultado,
                    "valor_numerico": resultado.valor_numerico,
                    "unidad": resultado.unidad or "",
                    "valor_referencia": resultado.valor_referencia or "",
                    "critico": resultado.critico,
                    "tipo_muestra": muestra.tipo_muestra,
                    "validador": validacion.validador or "",
                    "validador_id": validacion.validador_id,
                    "estado_validacion": validacion.estado,
                    "fecha_validacion": validacion.fecha_validacion,
                })

        return filas

    def _edad(self, fecha_nacimiento: date) -> str:
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )
        return f"{edad} años"

    # ------------------------------------------------------------
    # Construcción del PDF
    # ------------------------------------------------------------

    def _encabezado(self, story, styles, config: ConfiguracionLaboratorio):
        if config.logo_path:
            ruta_logo = os.path.join("app", "static", config.logo_path)
            if os.path.exists(ruta_logo):
                try:
                    logo = Image(ruta_logo, width=3.2 * cm, height=3.2 * cm)
                except Exception:
                    logo = Paragraph("", styles["Normal"])
            else:
                logo = Paragraph("", styles["Normal"])
        else:
            logo = Paragraph("", styles["Normal"])

        datos_lab = [Paragraph(f"<b>{config.nombre_laboratorio}</b>", styles["LabNombre"])]
        if config.nit:
            datos_lab.append(Paragraph(f"NIT: {config.nit}", styles["LabDato"]))
        if config.resolucion_habilitacion:
            datos_lab.append(Paragraph(f"Resolución: {config.resolucion_habilitacion}", styles["LabDato"]))
        if config.direccion:
            datos_lab.append(Paragraph(config.direccion, styles["LabDato"]))
        contacto = " · ".join(filter(None, [config.telefono, config.correo]))
        if contacto:
            datos_lab.append(Paragraph(contacto, styles["LabDato"]))

        tabla_header = Table([[logo, datos_lab]], colWidths=[3 * cm, 14 * cm])
        tabla_header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))

        story.append(tabla_header)
        story.append(Spacer(1, 6))
        linea = Table([[""]], colWidths=[17 * cm], rowHeights=[2])
        linea.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AZUL_LAB)]))
        story.append(linea)
        story.append(Spacer(1, 12))

    def _bloque_paciente(self, story, styles, paciente: Paciente, medico, orden: Orden):
        nombre_completo = " ".join(filter(None, [
            paciente.primer_nombre, paciente.segundo_nombre,
            paciente.primer_apellido, paciente.segundo_apellido,
        ]))

        datos = [
            ["Paciente:", nombre_completo, "Documento:", f"{paciente.tipo_documento} {paciente.documento}"],
            ["Edad:", self._edad(paciente.fecha_nacimiento), "Sexo:", paciente.sexo],
            ["Orden N.°:", orden.numero_orden, "Fecha orden:", orden.fecha_creacion.strftime("%Y-%m-%d")],
            ["Médico remitente:", f"{medico.nombres} {medico.apellidos}" if medico else "-",
             "Registro:", medico.registro_medico if medico else "-"],
        ]

        tabla = Table(datos, colWidths=[3.3 * cm, 5.2 * cm, 3.3 * cm, 5.2 * cm])
        tabla.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (-1, -1), GRIS_TEXTO),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#eeeeee")),
        ]))

        story.append(tabla)
        story.append(Spacer(1, 16))

    def _tabla_resultados(self, story, styles, filas: list[dict]):
        encabezados = ["Examen", "Resultado", "Unidad", "Valor de referencia"]
        cuerpo = [encabezados]

        for fila in filas:
            valor = fila["resultado"] or (
                str(fila["valor_numerico"]) if fila["valor_numerico"] is not None else "-"
            )
            if fila["critico"]:
                valor = f"<b>{valor} *</b>"

            cuerpo.append([
                Paragraph(fila["examen"], styles["Celda"]),
                Paragraph(str(valor), styles["Celda"]),
                Paragraph(fila["unidad"], styles["Celda"]),
                Paragraph(fila["valor_referencia"], styles["Celda"]),
            ])

        tabla = Table(cuerpo, colWidths=[6 * cm, 4 * cm, 2.5 * cm, 4.5 * cm], repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZUL_LAB),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fc")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(tabla)

        if any(f["critico"] for f in filas):
            story.append(Spacer(1, 8))
            story.append(Paragraph(
                "* Valor crítico: fuera del rango de referencia esperado.",
                styles["Nota"],
            ))

    def _pie_firma(self, story, styles, filas: list[dict], config: ConfiguracionLaboratorio):
        story.append(Spacer(1, 24))

        validadores = sorted({f["validador"] for f in filas if f["validador"]})
        ids_validadores = {f["validador_id"] for f in filas if f.get("validador_id")}

        if len(ids_validadores) == 1 and self.medico_repository:
            profesional = self.medico_repository.obtener_por_id(next(iter(ids_validadores)))
            if profesional and profesional.firma_path:
                ruta_firma = os.path.join("app", "static", profesional.firma_path)
                if os.path.exists(ruta_firma):
                    try:
                        story.append(Image(ruta_firma, width=3.5 * cm, height=1.8 * cm))
                    except Exception:
                        pass

        if validadores:
            story.append(Paragraph("_" * 40, styles["Normal"]))
            story.append(Paragraph(f"Validado por: {', '.join(validadores)}", styles["LabDato"]))

        if config.pie_pagina:
            story.append(Spacer(1, 10))
            story.append(Paragraph(config.pie_pagina, styles["Nota"]))

        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"Documento generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}. "
            "Este resultado es válido únicamente con la firma y sello del laboratorio.",
            styles["Nota"],
        ))

    def _estilos(self):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            "LabNombre", parent=styles["Normal"], fontSize=13, textColor=AZUL_LAB, leading=16,
        ))
        styles.add(ParagraphStyle(
            "LabDato", parent=styles["Normal"], fontSize=8.5, textColor=GRIS_TEXTO, leading=11,
        ))
        styles.add(ParagraphStyle(
            "Celda", parent=styles["Normal"], fontSize=9, leading=11,
        ))
        styles.add(ParagraphStyle(
            "Nota", parent=styles["Normal"], fontSize=7.5, textColor=colors.HexColor("#777777"),
        ))
        return styles

    # ------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------

    def historial_json(self, paciente_id: int) -> list[dict]:
        """
        Historial de resultados de un paciente a través del tiempo,
        agrupado por orden, para mostrarlo en pantalla (no PDF).
        """
        ordenes = self.orden_repository.listar_por_paciente(paciente_id)

        historial = []
        for orden in ordenes:
            filas = self._resultados_de_orden(orden.id)
            if not filas:
                continue

            historial.append({
                "orden_id": orden.id,
                "numero_orden": orden.numero_orden,
                "fecha_orden": orden.fecha_creacion,
                "estado_orden": orden.estado,
                "resultados": filas,
            })

        return historial

    def generar_pdf_orden(self, orden_id: int) -> bytes:
        orden = self.orden_repository.obtener_por_id(orden_id)
        if orden is None:
            raise ValueError("La orden indicada no existe.")

        paciente = self.paciente_repository.obtener_por_id(orden.paciente_id)
        medico = self.medico_repository.obtener_por_id(orden.medico_id)
        config = self.configuracion_repository.obtener()

        filas = self._resultados_de_orden(orden_id)
        if not filas:
            raise ValueError("Esta orden todavía no tiene resultados validados para imprimir.")

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
            leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        )
        styles = self._estilos()
        story = []

        self._encabezado(story, styles, config)
        self._bloque_paciente(story, styles, paciente, medico, orden)
        story.append(Paragraph("Resultados de laboratorio", styles["Heading2"]))
        story.append(Spacer(1, 8))
        self._tabla_resultados(story, styles, filas)
        self._pie_firma(story, styles, filas, config)

        doc.build(story)
        return buffer.getvalue()

    def generar_pdf_historial_paciente(self, paciente_id: int, orden_ids: list[int]) -> bytes:
        paciente = self.paciente_repository.obtener_por_id(paciente_id)
        if paciente is None:
            raise ValueError("El paciente indicado no existe.")

        config = self.configuracion_repository.obtener()
        styles = self._estilos()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
            leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        )
        story = []

        alguna_orden_con_resultados = False

        for i, orden_id in enumerate(orden_ids):
            orden = self.orden_repository.obtener_por_id(orden_id)
            if orden is None:
                continue

            filas = self._resultados_de_orden(orden_id)
            if not filas:
                continue

            alguna_orden_con_resultados = True
            medico = self.medico_repository.obtener_por_id(orden.medico_id)

            if i > 0:
                story.append(PageBreak())

            self._encabezado(story, styles, config)
            self._bloque_paciente(story, styles, paciente, medico, orden)
            story.append(Paragraph("Resultados de laboratorio", styles["Heading2"]))
            story.append(Spacer(1, 8))
            self._tabla_resultados(story, styles, filas)
            self._pie_firma(story, styles, filas, config)

        if not alguna_orden_con_resultados:
            raise ValueError("El paciente no tiene resultados validados para imprimir.")

        doc.build(story)
        return buffer.getvalue()
