"""
LABSYS DIALIZAR
Archivo: app/services/export_pdf_service.py
"""

from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors


class ExportPDFService:

    def exportar_indicadores(self, titulo:str, indicadores:dict)->bytes:
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer)
        styles=getSampleStyleSheet()
        elementos=[Paragraph(f"<b>{titulo}</b>", styles["Title"])]

        data=[["Indicador","Valor"]]
        for k,v in indicadores.items():
            data.append([str(k),str(v)])

        tabla=Table(data)
        tabla.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b5ed7")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BOTTOMPADDING",(0,0),(-1,0),8),
        ]))
        elementos.append(tabla)
        doc.build(elementos)
        return buffer.getvalue()

    def exportar_tabla(self,titulo:str,columnas:list,filas:list)->bytes:
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer)
        styles=getSampleStyleSheet()
        elementos=[Paragraph(f"<b>{titulo}</b>", styles["Title"])]
        tabla=Table([columnas]+filas)
        tabla.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b5ed7")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ]))
        elementos.append(tabla)
        doc.build(elementos)
        return buffer.getvalue()
