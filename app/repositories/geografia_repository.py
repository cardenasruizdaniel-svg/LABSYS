"""
LABSYS DIALIZAR
Modulo: Catalogos geograficos
Archivo: app/repositories/geografia_repository.py
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ciudad import Ciudad
from app.models.departamento import Departamento


class DepartamentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Departamento]:
        return list(self.db.scalars(select(Departamento).order_by(Departamento.nombre)).all())

    def obtener_por_id(self, dep_id: int) -> Optional[Departamento]:
        return self.db.get(Departamento, dep_id)

    def obtener_por_nombre(self, nombre: str) -> Optional[Departamento]:
        return self.db.scalar(select(Departamento).where(Departamento.nombre == nombre))

    def crear(self, dep: Departamento) -> Departamento:
        self.db.add(dep)
        self.db.commit()
        self.db.refresh(dep)
        return dep

    def eliminar(self, dep: Departamento) -> None:
        self.db.delete(dep)
        self.db.commit()


class CiudadRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Ciudad]:
        return list(self.db.scalars(select(Ciudad).order_by(Ciudad.nombre)).all())

    def listar_por_departamento(self, departamento_id: int) -> list[Ciudad]:
        stmt = select(Ciudad).where(Ciudad.departamento_id == departamento_id).order_by(Ciudad.nombre)
        return list(self.db.scalars(stmt).all())

    def obtener_por_id(self, ciudad_id: int) -> Optional[Ciudad]:
        return self.db.get(Ciudad, ciudad_id)

    def obtener_por_nombre_y_departamento(self, nombre: str, departamento_id: int) -> Optional[Ciudad]:
        stmt = select(Ciudad).where(Ciudad.nombre == nombre, Ciudad.departamento_id == departamento_id)
        return self.db.scalar(stmt)

    def crear(self, ciudad: Ciudad) -> Ciudad:
        self.db.add(ciudad)
        self.db.commit()
        self.db.refresh(ciudad)
        return ciudad

    def eliminar(self, ciudad: Ciudad) -> None:
        self.db.delete(ciudad)
        self.db.commit()
