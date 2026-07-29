"""
LABSYS DIALIZAR
Servicio de lectura de documentos con codigo de barras
app/services/document_reader.py

Soporta:
  - Cedula de ciudadania colombiana (formato PDF417 pipe-delimited)
  - Disenado para extension futura: TI, CE, pasaporte, licencia,
    lectura OCR desde camara, lectura desde dispositivos moviles
"""

import logging
import re
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DocumentoLeido:
    tipo_documento: str = "CC"
    documento: str = ""
    primer_nombre: str = ""
    segundo_nombre: Optional[str] = None
    primer_apellido: str = ""
    segundo_apellido: Optional[str] = None
    sexo: str = ""
    fecha_nacimiento: Optional[str] = None
    rh: Optional[str] = None
    lugar_expedicion: Optional[str] = None
    fecha_expedicion: Optional[str] = None
    datos_crudos: str = ""
    formato_detectado: str = ""


FORMATOS_REGISTRADOS = {}


def registrar_formato(nombre):
    def decorador(func):
        FORMATOS_REGISTRADOS[nombre] = func
        return func
    return decorador


def detectar_formato(cadena: str) -> Optional[str]:
    if not cadena or not cadena.strip():
        return None
    limpia = cadena.strip()
    if "|" in limpia:
        partes = [p.strip() for p in limpia.split("|")]
        if len(partes) >= 4:
            return "pdf417_cedula_colombia"
    if limpia.startswith("CC") or limpia.startswith("CE"):
        return "pdf417_cedula_colombia"
    return None


@registrar_formato("pdf417_cedula_colombia")
def decodificar_pdf417_cedula_colombia(cadena: str) -> DocumentoLeido:
    limpia = cadena.strip().replace("\r", "").replace("\n", "")
    if "|" in limpia:
        partes = [p.strip() for p in limpia.split("|")]
    else:
        partes = re.split(r"[<\s]+", limpia)
        partes = [p for p in partes if p]

    doc = DocumentoLeido(datos_crudos=cadena, formato_detectado="pdf417_cedula_colombia")

    idx = 0

    if idx < len(partes) and partes[idx] in ("CC", "CE", "TI", "PA", "RC", "MS"):
        doc.tipo_documento = partes[idx]
        idx += 1

    if idx < len(partes):
        doc.documento = _extraer_numeros(partes[idx])
        idx += 1

    if idx < len(partes):
        doc.primer_apellido = partes[idx].upper()
        idx += 1

    if idx < len(partes):
        sig = partes[idx].upper()
        if sig and not _es_campo_fijo(sig) and not _es_posible_sexo(sig) and len(sig) > 1:
            doc.segundo_apellido = sig
            idx += 1

    if idx < len(partes):
        doc.primer_nombre = partes[idx].upper()
        idx += 1

    if idx < len(partes):
        sig = partes[idx].upper()
        if sig and not _es_campo_fijo(sig) and not _es_posible_sexo(sig) and len(sig) > 1:
            doc.segundo_nombre = sig
            idx += 1

    for i in range(idx, len(partes)):
        p = partes[i].upper().strip()
        if _es_posible_sexo(p):
            doc.sexo = "Masculino" if p == "M" else "Femenino" if p == "F" else p
            idx = i + 1
            break

    for i in range(idx, len(partes)):
        p = partes[i].strip()
        if _es_fecha_valida(p):
            doc.fecha_nacimiento = _normalizar_fecha(p)
            idx = i + 1
            break

    for i in range(idx, len(partes)):
        p = partes[i].strip().upper()
        if re.match(r"^(A|B|AB|O)[+-]$", p) or re.match(r"^(A|B|AB|O)\s*[+-]$", p.replace(" ", "")):
            doc.rh = p.replace(" ", "")
            idx = i + 1
            break

    if idx < len(partes):
        partes_resto = partes[idx:]
        for p in partes_resto:
            p = p.strip()
            if _es_fecha_valida(p) and doc.fecha_expedicion is None:
                doc.fecha_expedicion = _normalizar_fecha(p)
            else:
                if doc.lugar_expedicion is None:
                    doc.lugar_expedicion = p.upper()
                else:
                    doc.lugar_expedicion += ", " + p.upper()

    return doc


def _extraer_numeros(s: str) -> str:
    return re.sub(r"[^0-9]", "", s)


def _es_campo_fijo(s: str) -> bool:
    return s in ("COL", "COLOMBIA", "REGISTRADURIA", "RNEC", "")


def _es_posible_sexo(s: str) -> bool:
    return s in ("M", "F", "MASCULINO", "FEMENINO")


def _es_fecha_valida(s: str) -> bool:
    s = s.strip().replace("-", "").replace("/", "").replace(" ", "")
    if len(s) == 8 and s.isdigit():
        try:
            datetime.strptime(s, "%Y%m%d")
            return True
        except ValueError:
            pass
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            datetime.strptime(s, fmt)
            return True
        except ValueError:
            pass
    return False


def _normalizar_fecha(s: str) -> str:
    s = s.strip().replace("/", "-").replace(" ", "")
    if len(s) == 8 and s.isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(s.replace("/", "-"), fmt.replace("/", "-"))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return s


def procesar_lectura(cadena: str) -> dict:
    formato = detectar_formato(cadena)
    if not formato:
        logger.warning("Formato de documento no reconocido: %s", cadena[:50])
        return {
            "success": False,
            "error": "No fue posible interpretar el codigo de barras. Puede ingresar la informacion manualmente.",
            "datos_crudos": cadena,
        }

    decodificador = FORMATOS_REGISTRADOS.get(formato)
    if not decodificador:
        return {
            "success": False,
            "error": f"Formato '{formato}' no tiene decodificador implementado.",
            "datos_crudos": cadena,
        }

    try:
        doc = decodificador(cadena)
    except Exception as e:
        logger.exception("Error decodificando %s: %s", formato, e)
        return {
            "success": False,
            "error": "Error al decodificar el codigo de barras. Intente manualmente.",
            "datos_crudos": cadena,
        }

    datos = asdict(doc)
    datos["success"] = True

    if not datos.get("documento"):
        datos["success"] = False
        datos["error"] = "No se pudo extraer el numero de documento."

    return datos
