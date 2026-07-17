"""
LABSYS DIALIZAR
Archivo: app/services/export_excel_service.py
"""

from io import BytesIO
from openpyxl import Workbook

class ExportExcelService:

    def exportar_indicadores(self, indicadores: dict) -> bytes:
        wb = Workbook()
        ws = wb.active
        ws.title = "Indicadores"

        ws.append(["Indicador","Valor"])

        for k,v in indicadores.items():
            ws.append([k,v])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def exportar_tabla(self, titulo: str, columnas: list[str], filas: list[list]):
        wb = Workbook()
        ws = wb.active
        ws.title = titulo[:31]

        ws.append(columnas)

        for fila in filas:
            ws.append(fila)

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
