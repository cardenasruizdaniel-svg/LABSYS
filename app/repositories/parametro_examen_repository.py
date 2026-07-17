"""
LABSYS DIALIZAR
Módulo: Procesar y Validar
Archivo: app/repositories/parametro_examen_repository.py
"""

from sqlalchemy.orm import Session

from app.models.parametro_examen import ParametroExamen


class ParametroExamenRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[ParametroExamen]:
        return (
            self.db.query(ParametroExamen)
            .order_by(ParametroExamen.examen_id, ParametroExamen.orden)
            .all()
        )

    def obtener_por_id(self, parametro_id: int) -> ParametroExamen | None:
        return self.db.query(ParametroExamen).filter(
            ParametroExamen.id == parametro_id
        ).first()

    def listar_por_examen(self, examen_id: int) -> list[ParametroExamen]:
        return (
            self.db.query(ParametroExamen)
            .filter(ParametroExamen.examen_id == examen_id)
            .order_by(ParametroExamen.orden)
            .all()
        )

    def listar_por_examenes(self, examenes_ids: list[int]) -> list[ParametroExamen]:
        return (
            self.db.query(ParametroExamen)
            .filter(ParametroExamen.examen_id.in_(examenes_ids))
            .order_by(ParametroExamen.examen_id, ParametroExamen.orden)
            .all()
        )

    def crear(self, datos: dict) -> ParametroExamen:
        parametro = ParametroExamen(**datos)
        self.db.add(parametro)
        self.db.commit()
        self.db.refresh(parametro)
        return parametro

    def actualizar(self, parametro_id: int, datos: dict) -> ParametroExamen | None:
        parametro = self.obtener_por_id(parametro_id)
        if parametro is None:
            return None
        for clave, valor in datos.items():
            if hasattr(parametro, clave):
                setattr(parametro, clave, valor)
        self.db.commit()
        self.db.refresh(parametro)
        return parametro

    def eliminar(self, parametro_id: int) -> ParametroExamen | None:
        parametro = self.obtener_por_id(parametro_id)
        if parametro is None:
            return None
        self.db.delete(parametro)
        self.db.commit()
        return parametro
