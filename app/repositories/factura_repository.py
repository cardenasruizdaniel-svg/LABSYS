"""
LABSYS DIALIZAR
Módulo: Laboratorio Clínico
Historia: HU-016
Archivo: app/repositories/factura_repository.py
"""

from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.factura import Factura


class FacturaRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Factura]:
        stmt = select(Factura).order_by(Factura.fecha_emision.desc())
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, factura_id: int) -> Optional[Factura]:
        return self.db.get(Factura, factura_id)

    def obtener_por_numero(self, numero: str) -> Optional[Factura]:
        stmt = select(Factura).where(Factura.numero == numero)
        return self.db.scalar(stmt)

    def contar_hoy(self) -> int:
        hoy = date.today()
        return self.db.query(func.count(Factura.id)).filter(
            func.date(Factura.fecha_emision) == hoy
        ).scalar() or 0

    def max_numero_hoy(self) -> int:
        """Devuelve el mayor consecutivo de facturas creadas hoy (0 si no hay ninguna)."""
        hoy = date.today()
        like_pattern = f"FAC-{hoy.strftime('%Y%m%d')}-%"
        resultado = self.db.query(
            func.max(Factura.numero)
        ).filter(
            Factura.numero.like(like_pattern)
        ).scalar()
        if not resultado:
            return 0
        try:
            return int(resultado.rsplit("-", 1)[-1])
        except (ValueError, IndexError):
            return 0

    def crear(self, factura: Factura) -> Factura:
        self.db.add(factura)
        self.db.commit()
        self.db.refresh(factura)
        return factura

    def actualizar(self, factura: Factura) -> Factura:
        self.db.commit()
        self.db.refresh(factura)
        return factura
