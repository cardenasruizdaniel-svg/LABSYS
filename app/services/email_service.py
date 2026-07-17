"""
LABSYS DIALIZAR
Modulo: Resultados
Archivo: app/services/email_service.py

Servicio de envio de correos electronicos via SMTP.
Se usa para enviar resultados de examenes a los pacientes
cuando una validacion es confirmada.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_addr = settings.SMTP_FROM
        self._load_db_config()

    def _load_db_config(self):
        """Carga configuracion SMTP desde la base de datos (sobreescribe .env)."""
        try:
            from app.database.session import SessionLocal
            from app.repositories.configuracion_laboratorio_repository import (
                ConfiguracionLaboratorioRepository,
            )
            db = SessionLocal()
            config = ConfiguracionLaboratorioRepository(db).obtener()
            db.close()
            if config:
                if config.smtp_host:
                    self.host = config.smtp_host
                if config.smtp_port:
                    self.port = config.smtp_port
                if config.smtp_user:
                    self.user = config.smtp_user
                if config.smtp_password:
                    self.password = config.smtp_password
                if config.smtp_from:
                    self.from_addr = config.smtp_from
        except Exception:
            pass

    @property
    def is_configured(self):
        return bool(self.user and self.password)

    def _crear_conexion(self):
        server = smtplib.SMTP(self.host, self.port, timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.user, self.password)
        return server

    def enviar_resultados(
        self,
        correo_paciente: str,
        nombre_paciente: str,
        numero_orden: str,
        fecha_orden: str,
        medico_nombre: str,
        examenes_html: str,
        observaciones: str | None = None,
        pdf_bytes: bytes | None = None,
        pdf_filename: str = "resultados.pdf",
    ) -> bool:
        """
        Envia un correo con los resultados de examenes al paciente.

        Args:
            correo_paciente: Direccion de correo del paciente
            nombre_paciente: Nombre completo del paciente
            numero_orden: Numero de la orden (ej. ORD-20260715-01)
            fecha_orden: Fecha de la orden formateada
            medico_nombre: Nombre del medico remitente
            examenes_html: Tabla HTML con los resultados
            observaciones: Observaciones generales (opcional)
            pdf_bytes: Bytes del PDF de resultados (opcional, se adjunta)
            pdf_filename: Nombre del archivo PDF adjunto

        Returns:
            True si se envio correctamente, False si hubo error
        """
        if not self.is_configured:
            logger.warning("SMTP no configurado. No se puede enviar correo.")
            return False

        if not correo_paciente:
            logger.warning("Paciente %s no tiene correo. No se envia resultado.", nombre_paciente)
            return False

        msg = MIMEMultipart("mixed")
        msg["From"] = self.from_addr
        msg["To"] = correo_paciente
        msg["Subject"] = f"Resultados de laboratorio - {numero_orden}"

        html_body = self._construir_html(
            nombre_paciente=nombre_paciente,
            numero_orden=numero_orden,
            fecha_orden=fecha_orden,
            medico_nombre=medico_nombre,
            examenes_html=examenes_html,
            observaciones=observaciones,
        )

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        if pdf_bytes:
            attachment = MIMEBase("application", "pdf")
            attachment.set_payload(pdf_bytes)
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                f'attachment; filename="{pdf_filename}"',
            )
            msg.attach(attachment)

        try:
            server = self._crear_conexion()
            server.sendmail(self.from_addr, [correo_paciente], msg.as_string())
            server.quit()
            logger.info("Correo enviado a %s para orden %s", correo_paciente, numero_orden)
            return True
        except smtplib.SMTPException as e:
            logger.error("Error SMTP al enviar correo a %s: %s", correo_paciente, e)
            return False
        except Exception as e:
            logger.error("Error inesperado al enviar correo a %s: %s", correo_paciente, e)
            return False

    def _construir_html(
        self,
        nombre_paciente: str,
        numero_orden: str,
        fecha_orden: str,
        medico_nombre: str,
        examenes_html: str,
        observaciones: str | None,
    ) -> str:
        from app.repositories.configuracion_laboratorio_repository import (
            ConfiguracionLaboratorioRepository,
        )
        from app.database.session import SessionLocal

        config = None
        try:
            db = SessionLocal()
            config = ConfiguracionLaboratorioRepository(db).obtener()
            db.close()
        except Exception:
            pass

        lab_name = config.nombre_laboratorio if config else "LABSYS DIALIZAR"
        lab_nit = config.nit if config and config.nit else ""
        lab_direccion = config.direccion if config and config.direccion else ""
        lab_ciudad = config.ciudad if config and config.ciudad else ""
        lab_telefono = config.telefono if config and config.telefono else ""
        lab_correo = config.correo if config and config.correo else ""
        pie_pagina = config.pie_pagina if config and config.pie_pagina else ""

        logo_url = ""
        if config and config.logo_path:
            logo_url = f"http://127.0.0.1:8089/static/{config.logo_path}"

        logo_html = ""
        if logo_url:
            logo_html = f'<img src="{logo_url}" style="height:60px;max-width:90px;object-fit:contain;" alt="{lab_name}">'
        else:
            logo_html = f'<div style="width:55px;height:55px;border:2px solid #0B5ED7;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:bold;color:#0B5ED7;">LAB</div>'

        info_lineas = []
        if lab_nit:
            info_lineas.append(f"NIT: {lab_nit}")
        if lab_direccion:
            info_lineas.append(lab_direccion)
        if lab_ciudad:
            info_lineas.append(lab_ciudad)
        if lab_telefono:
            info_lineas.append(f"Tel: {lab_telefono}")
        info_lab = "<br>".join(info_lineas)

        obs_html = ""
        if observaciones:
            obs_html = f"""
            <div style="margin-top:16px;padding:12px;background:#f0f7ff;border-left:3px solid #0B5ED7;border-radius:4px;">
                <strong style="color:#333;">Observaciones:</strong>
                <p style="margin:4px 0 0;color:#555;">{observaciones}</p>
            </div>"""

        return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">
<div style="max-width:600px;margin:20px auto;background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

    <!-- Cabecera -->
    <div style="background:linear-gradient(135deg,#0B5ED7 0%,#0a4fc0 100%);padding:20px 24px;color:#fff;">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="flex-shrink:0;">{logo_html}</div>
            <div>
                <div style="font-size:18px;font-weight:700;">{lab_name}</div>
                <div style="font-size:11px;opacity:0.85;">{info_lab}</div>
            </div>
        </div>
    </div>

    <!-- Titulo -->
    <div style="padding:20px 24px 0;">
        <h2 style="margin:0;color:#0B5ED7;font-size:16px;">Resultados de Laboratorio Clinico</h2>
        <p style="margin:4px 0 0;color:#888;font-size:13px;">Se han validado los resultados de sus examenes</p>
    </div>

    <!-- Datos del paciente -->
    <div style="padding:16px 24px;">
        <div style="display:flex;gap:12px;font-size:13px;color:#333;">
            <div style="flex:1;background:#f9fafb;padding:10px 12px;border-radius:6px;border:1px solid #eee;">
                <strong>Paciente:</strong> {nombre_paciente}<br>
                <strong>Orden:</strong> {numero_orden}<br>
                <strong>Fecha:</strong> {fecha_orden}
            </div>
            <div style="flex:1;background:#f9fafb;padding:10px 12px;border-radius:6px;border:1px solid #eee;">
                <strong>Medico:</strong> {medico_nombre}<br>
                <strong>Fecha validacion:</strong> {fecha_orden}
            </div>
        </div>
    </div>

    <!-- Resultados -->
    <div style="padding:0 24px 16px;">
        <h3 style="margin:0 0 8px;font-size:14px;color:#333;">Resultados</h3>
        <table style="width:100%;border-collapse:collapse;font-size:12px;">
            <thead>
                <tr style="background:#0B5ED7;color:#fff;">
                    <th style="padding:8px 10px;text-align:left;">Examen</th>
                    <th style="padding:8px 10px;text-align:left;">Parametro</th>
                    <th style="padding:8px 10px;text-align:center;">Resultado</th>
                    <th style="padding:8px 10px;text-align:center;">Unidad</th>
                    <th style="padding:8px 10px;text-align:center;">Referencia</th>
                </tr>
            </thead>
            <tbody>
                {examenes_html}
            </tbody>
        </table>
    </div>

    {obs_html}

    <!-- Nota -->
    <div style="padding:0 24px 16px;">
        <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:6px;padding:10px 12px;font-size:11px;color:#795548;">
            <strong>Nota:</strong> Este correo es informativo. El resultado definitivo se encuentra
            en el documento PDF adjunto a este mensaje, el cual cuenta con la firma y sello del laboratorio.
        </div>
    </div>

    <!-- Pie -->
    <div style="background:#f4f6f8;padding:16px 24px;text-align:center;font-size:11px;color:#999;border-top:1px solid #eee;">
        {f'<div style="margin-bottom:4px;">{pie_pagina}</div>' if pie_pagina else ''}
        <div>Documento generado automaticamente por {lab_name}</div>
        <div style="margin-top:2px;">Este correo fue enviado porque sus resultados fueron validados por el laboratorio.</div>
    </div>

</div>
</body>
</html>"""
