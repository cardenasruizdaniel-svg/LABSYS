"""
LABSYS DIALIZAR
Modulo: Dashboard
Archivo: app/routers/dashboard.py
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/")
def dashboard(db: Session = Depends(get_db)):
    return DashboardService(db).dashboard()


@router.get("/indicadores")
def indicadores(db: Session = Depends(get_db)):
    return DashboardService(db).indicadores()
