"""
Registro central de modelos.

Cada nuevo modelo deberá importarse aquí para que SQLAlchemy
lo registre automáticamente antes de crear las tablas.
"""

from app.models.base import BaseModel

# Seguridad
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.permiso import Permiso
from app.models.rol_permiso import RolPermiso
from app.models.usuario_rol import UsuarioRol

# Catálogos / terceros
from app.models.eps import EPS
from app.models.convenio import Convenio
from app.models.medico import Medico
from app.models.departamento import Departamento
from app.models.ciudad import Ciudad

# Proceso clínico
from app.models.paciente import Paciente
from app.models.orden import Orden
from app.models.examen import Examen
from app.models.orden_examen import OrdenExamen
from app.models.muestra import Muestra
from app.models.procesamiento import Procesamiento
from app.models.validacion import Validacion
from app.models.resultado import Resultado

# Agenda
from app.models.cita import Cita
from app.models.cupo_diario import CupoDiario

# Facturación
from app.models.factura import Factura

# Configuración
from app.models.configuracion_laboratorio import ConfiguracionLaboratorio

# Inventario
from app.models.item_inventario import ItemInventario
from app.models.movimiento_inventario import MovimientoInventario

# Caja
from app.models.caja_apertura import CajaApertura
from app.models.caja_cierre import CajaCierre
from app.models.caja_ingreso import CajaIngreso

# Gastos
from app.models.gasto import Gasto

# Parámetros de exámenes (formularios pre-diseñados)
from app.models.parametro_examen import ParametroExamen

__all__ = [
    "BaseModel",
    "Usuario",
    "Rol",
    "Permiso",
    "RolPermiso",
    "UsuarioRol",
    "EPS",
    "Convenio",
    "Medico",
    "Departamento",
    "Ciudad",
    "Paciente",
    "Orden",
    "Examen",
    "OrdenExamen",
    "Muestra",
    "Procesamiento",
    "Validacion",
    "Resultado",
    "Cita",
    "CupoDiario",
    "Factura",
    "ConfiguracionLaboratorio",
    "ItemInventario",
    "MovimientoInventario",
    "CajaApertura",
    "CajaCierre",
    "CajaIngreso",
    "Gasto",
    "ParametroExamen",
]
