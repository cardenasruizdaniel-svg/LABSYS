"""
==========================================================
LABSYS DIALIZAR
Router Reportes Gerenciales
Archivo:
app/routers/reportes.py
==========================================================
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.export_excel_service import ExportExcelService
from app.services.export_pdf_service import ExportPDFService
from app.services.reportes_service import ReportesService

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes Gerenciales"]
)


def get_service(db: Session) -> ReportesService:
    return ReportesService(db)


@router.get("/indicadores")
def indicadores(
    db: Session = Depends(get_db)
):
    return get_service(db).indicadores_generales()


@router.get("/produccion")
def produccion(
    db: Session = Depends(get_db)
):
    return get_service(db).produccion_laboratorio()


@router.get("/financiero")
def financiero(
    db: Session = Depends(get_db)
):
    return get_service(db).resumen_financiero()


@router.get("/ordenes-estado")
def ordenes_estado(
    db: Session = Depends(get_db)
):
    return get_service(db).ordenes_por_estado()


@router.get("/facturas-estado")
def facturas_estado(
    db: Session = Depends(get_db)
):
    return get_service(db).facturas_por_estado()


@router.get("/indicadores/pdf")
def indicadores_pdf(db: Session = Depends(get_db)):
    indicadores = get_service(db).indicadores_generales()
    pdf_bytes = ExportPDFService().exportar_indicadores("Indicadores Generales - LABSYS DIALIZAR", indicadores)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="reporte_indicadores.pdf"'},
    )


@router.get("/indicadores/excel")
def indicadores_excel(db: Session = Depends(get_db)):
    indicadores = get_service(db).indicadores_generales()
    excel_bytes = ExportExcelService().exportar_indicadores(indicadores)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="reporte_indicadores.xlsx"'},
    )