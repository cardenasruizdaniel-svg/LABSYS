"""
==========================================================
LABSYS DIALIZAR
Reportes Gerenciales
reportes_service.py
==========================================================
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.paciente import Paciente
from app.models.orden import Orden
from app.models.muestra import Muestra
from app.models.procesamiento import Procesamiento
from app.models.validacion import Validacion
from app.models.resultado import Resultado
from app.models.factura import Factura


class ReportesService:

    def __init__(self, db: Session):
        self.db = db

    def indicadores_generales(self):

        return {

            "pacientes":
                self.db.query(func.count(Paciente.id)).scalar() or 0,

            "ordenes":
                self.db.query(func.count(Orden.id)).scalar() or 0,

            "muestras":
                self.db.query(func.count(Muestra.id)).scalar() or 0,

            "procesamientos":
                self.db.query(func.count(Procesamiento.id)).scalar() or 0,

            "validaciones":
                self.db.query(func.count(Validacion.id)).scalar() or 0,

            "resultados":
                self.db.query(func.count(Resultado.id)).scalar() or 0,

            "facturas":
                self.db.query(func.count(Factura.id)).scalar() or 0,

            "facturacion_total":

                float(

                    self.db.query(

                        func.coalesce(

                            func.sum(Factura.total),

                            0

                        )

                    ).scalar()

                )

        }

    def ordenes_por_estado(self):

        return (

            self.db.query(

                Orden.estado,

                func.count(Orden.id)

            )

            .group_by(Orden.estado)

            .all()

        )

    def facturas_por_estado(self):

        return (

            self.db.query(

                Factura.estado,

                func.count(Factura.id)

            )

            .group_by(Factura.estado)

            .all()

        )

    def produccion_laboratorio(self):

        return {

            "muestras_pendientes":

                self.db.query(

                    func.count(Muestra.id)

                ).filter(

                    Muestra.estado == "PENDIENTE"

                ).scalar(),

            "muestras_procesadas":

                self.db.query(

                    func.count(Muestra.id)

                ).filter(

                    Muestra.estado == "PROCESADA"

                ).scalar(),

            "resultados_emitidos":

                self.db.query(

                    func.count(Resultado.id)

                ).scalar()

        }

    def resumen_financiero(self):

        return {

            "facturacion":

                float(

                    self.db.query(

                        func.coalesce(

                            func.sum(Factura.total),

                            0

                        )

                    ).scalar()

                ),

            "facturas_con_copago_pagado":

                self.db.query(

                    func.count(Factura.id)

                ).filter(

                    Factura.copago_pagado == True  # noqa: E712

                ).scalar(),

            "facturas_con_copago_pendiente":

                self.db.query(

                    func.count(Factura.id)

                ).filter(

                    Factura.copago_pagado == False  # noqa: E712

                ).scalar()

        }