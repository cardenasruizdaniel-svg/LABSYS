"""
LABSYS DIALIZAR
Archivo: app/database/seed_data.py

Crea los registros base necesarios para poder atender y facturar
pacientes PARTICULARES (los que llegan por Agenda sin orden médica
ni EPS, y pagan el examen directamente):

  - EPS "PARTICULAR"
  - Convenio "PARTICULAR" (tipo_copago=PORCENTAJE, valor_copago=100,
    es decir: el paciente paga el 100% del valor, el "convenio" no
    cubre nada — es solo un contenedor para poder usar el mismo
    flujo de Ordenes/Facturas que ya existe para pacientes con EPS)
  - Médico "PARTICULAR" (placeholder para órdenes que no tienen un
    médico remitente real, ya que Orden.medico_id es obligatorio)

Es seguro ejecutar esta función varias veces: si los registros ya
existen, no hace nada.
"""

from datetime import date
from decimal import Decimal

from app.database.session import SessionLocal
from app.models.convenio import Convenio
from app.models.eps import EPS
from app.models.examen import Examen
from app.models.medico import Medico
from app.models.usuario import Usuario
from app.security.password import generar_hash

CODIGO_EPS_PARTICULAR = "PARTICULAR"
CODIGO_CONVENIO_PARTICULAR = "PARTICULAR"
REGISTRO_MEDICO_PARTICULAR = "PARTICULAR"

USUARIO_ADMIN = "admin"
PASSWORD_ADMIN_INICIAL = "Admin123*"

EXAMENES_BASE = [
    # ── Hematología ──────────────────────────────────────────────
    # (codigo, nombre, categoria, precio, tipo_muestra, recipiente)
    ("HEM001", "Hemograma completo", "Hematología", "15000", "SANGRE", "Tubo tapa lila (EDTA)"),
    ("HEM002", "Hemoglobina glicosilada (HbA1c)", "Hematología", "35000", "SANGRE", "Tubo tapa lila (EDTA)"),
    ("HEM003", "Velocidad de sedimentación (VSG)", "Hematología", "12000", "SANGRE", "Tubo tapa negra (citrato)"),
    ("HEM004", "Reticulocitos", "Hematología", "18000", "SANGRE", "Tubo tapa lila (EDTA)"),
    ("HEM005", "Grupo sanguíneo y factor Rh", "Hematología", "20000", "SANGRE", "Tubo tapa lila (EDTA)"),
    ("HEM006", "Prueba de Coombs directa", "Hematología", "25000", "SANGRE", "Tubo tapa lila (EDTA)"),
    ("HEM007", "Prueba de Coombs indirecta", "Hematología", "25000", "SANGRE", "Tubo tapa lila (EDTA)"),
    ("HEM008", "Frotis de sangre periférica", "Hematología", "15000", "SANGRE", "Tubo tapa lila (EDTA)"),
    ("HEM009", "Tiempo de protrombina (TP)", "Hematología", "18000", "SANGRE", "Tubo tapa azul (citrato Na)"),
    ("HEM010", "Tiempo de tromboplastina parcial (TTP)", "Hematología", "18000", "SANGRE", "Tubo tapa azul (citrato Na)"),
    ("HEM011", "Fibrinógeno", "Hematología", "22000", "SANGRE", "Tubo tapa azul (citrato Na)"),
    ("HEM012", "Dímero D", "Hematología", "45000", "SANGRE", "Tubo tapa azul (citrato Na)"),
    # ── Química sanguínea ───────────────────────────────────────
    ("GLU001", "Glucosa en ayunas", "Química sanguínea", "12000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI001", "Perfil lipídico (colesterol + TG + HDL + LDL)", "Química sanguínea", "38000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("CRE001", "Creatinina", "Química sanguínea", "12000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("URE001", "Nitrógeno ureico (BUN)", "Química sanguínea", "12000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI002", "Ácido úrico", "Química sanguínea", "13000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI003", "Bilirrubina total", "Química sanguínea", "13000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI004", "Bilirrubina directa", "Química sanguínea", "13000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI005", "Bilirrubina indirecta", "Química sanguínea", "13000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI006", "Transaminasas TGO (AST)", "Química sanguínea", "14000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI007", "Transaminasas TGP (ALT)", "Química sanguínea", "14000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI008", "Fosfatasa alcalina", "Química sanguínea", "15000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI009", "GGT (Gamma-glutamil transferasa)", "Química sanguínea", "16000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI010", "Proteínas totales", "Química sanguínea", "12000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI011", "Albúmina", "Química sanguínea", "12000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI012", "Calcio sérico", "Química sanguínea", "14000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI013", "Fósforo sérico", "Química sanguínea", "14000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI014", "Magnesio sérico", "Química sanguínea", "16000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI015", "Hierro sérico", "Química sanguínea", "16000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI016", "Ferritina", "Química sanguínea", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI017", "Transferrina", "Química sanguínea", "28000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI018", "Lactato deshidrogenasa (LDH)", "Química sanguínea", "16000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI019", "Amilasa sérica", "Química sanguínea", "18000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI020", "Lipasa sérica", "Química sanguínea", "20000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI021", "CK (Creatina fosfoquinasa)", "Química sanguínea", "16000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI022", "CK-MB", "Química sanguínea", "22000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI023", "Troponina I", "Química sanguínea", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("QUI024", "Gasometría arterial (pH, pO2, pCO2, HCO3, SatO2)", "Química sanguínea", "32000", "SANGRE", "Jeringa heparinizada"),
    # ── Perfiles ─────────────────────────────────────────────────
    ("PER001", "Perfil hepático completo", "Perfiles", "55000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("PER002", "Perfil renal completo", "Perfiles", "40000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("PER003", "Perfil tiroideo completo (TSH + T3 + T4L)", "Perfiles", "75000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("PER004", "Perfil preoperatorio", "Perfiles", "65000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("PER005", "Perfil prenatal", "Perfiles", "80000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("PER006", "Perfil metabólico completo", "Perfiles", "95000", "SANGRE", "Tubo tapa amarilla (gel)"),
    # ── Inmunología ─────────────────────────────────────────────
    ("PCR001", "Proteína C reactiva (PCR)", "Inmunología", "25000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM001", "Complemento C3", "Inmunología", "28000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM002", "Complemento C4", "Inmunología", "28000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM003", "Factor reumatoide", "Inmunología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM004", "Anti-nucleares (ANA)", "Inmunología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM005", "Anti-DNA de doble cadena", "Inmunología", "40000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM006", "Anti-streptolisina O (ASLO)", "Inmunología", "28000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM007", "IgA", "Inmunología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM008", "IgE total", "Inmunología", "32000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM009", "IgG", "Inmunología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM010", "IgM", "Inmunología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM011", "Anticuerpos anti-tiroglobulina", "Inmunología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM012", "Anticuerpos anti-TPO", "Inmunología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM013", "Factor anti-nuclear (FAN)", "Inmunología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("INM014", "VSG (repetido — referido a HEM003)", "Inmunología", "12000", "SANGRE", "Tubo tapa negra (citrato)"),
    # ── Endocrinología ──────────────────────────────────────────
    ("TSH001", "TSH", "Endocrinología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END001", "T3 libre", "Endocrinología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END002", "T4 libre", "Endocrinología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END003", "T3 total", "Endocrinología", "28000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END004", "T4 total", "Endocrinología", "28000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END005", "Insulina", "Endocrinología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END006", "Cortisol", "Endocrinología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END007", "PTH (Hormona paratiroidea)", "Endocrinología", "40000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END008", "Testosterona", "Endocrinología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END009", "Estradiol", "Endocrinología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END010", "Progesterona", "Endocrinología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END011", "FSH", "Endocrinología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END012", "LH", "Endocrinología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END013", "Prolactina", "Endocrinología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END014", "Vitamina D (25-OH)", "Endocrinología", "45000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END015", "Vitamina B12", "Endocrinología", "40000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("END016", "Acido fólico", "Endocrinología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    # ── Uroanálisis ─────────────────────────────────────────────
    ("ORI001", "Parcial de orina", "Uroanálisis", "10000", "ORINA", "Frasco estéril"),
    ("URO001", "Urocultivo con antibiograma", "Uroanálisis", "22000", "ORINA", "Frasco estéril"),
    ("URO002", "Clearance de creatinina", "Uroanálisis", "25000", "ORINA", "Recipiente 24h"),
    ("URO003", "Proteinuria en 24 horas", "Uroanálisis", "20000", "ORINA", "Recipiente 24h"),
    ("URO004", "Microalbuminuria", "Uroanálisis", "28000", "ORINA", "Frasco estéril"),
    # ── Coproparasitoscópico ────────────────────────────────────
    ("COP001", "Coproanálisis completo", "Coproparasitología", "12000", "HECES", "Frasco tapa rosca estéril"),
    ("COP002", "Búsqueda de parásitos (3 muestras)", "Coproparasitología", "18000", "HECES", "Frasco tapa rosca estéril"),
    # ── Serología / Infecciosas ─────────────────────────────────
    ("VIH001", "Prueba VIH (Elisa/Western blot)", "Serología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER001", "Hepatitis B (HBsAg)", "Serología", "28000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER002", "Hepatitis B (anti-HBs)", "Serología", "28000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER003", "Hepatitis B (anti-HBc total)", "Serología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER004", "Hepatitis B (anti-HBc IgM)", "Serología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER005", "Hepatitis B (HBeAg)", "Serología", "32000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER006", "Hepatitis C (anti-VHC)", "Serología", "32000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER007", "Dengue NS1 + IgM/IgG", "Serología", "55000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER008", "VDRL (sífilis)", "Serología", "15000", "SANGRE", "Tubo tapa roja (sin aditivo)"),
    ("SER009", "FTA-ABS (confirmación sífilis)", "Serología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER010", "Chagas (anti-T. cruzi)", "Serología", "28000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER011", "Toxoplasmosis (IgG + IgM)", "Serología", "40000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER012", "Rubéola (IgG + IgM)", "Serología", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER013", "CMV (IgG + IgM)", "Serología", "40000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER014", "Herpes simple 1 y 2 (IgG)", "Serología", "38000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("SER015", "Mononucleosis (EBV)", "Serología", "30000", "SANGRE", "Tubo tapa amarilla (gel)"),
    # ── Coagulación ─────────────────────────────────────────────
    ("COA001", "Coagulograma completo (TP + TTP + Fibrinógeno + INR)", "Coagulación", "35000", "SANGRE", "Tubo tapa azul (citrato Na)"),
    ("COA002", "INR (International Normalized Ratio)", "Coagulación", "18000", "SANGRE", "Tubo tapa azul (citrato Na)"),
    # ── Microbiología ───────────────────────────────────────────
    ("MIC001", "Cultivo general (muestra selecta)", "Microbiología", "25000", "OTRO", "Recipiente estéril según muestra"),
    ("MIC002", "Cultivo de uropatógenos", "Microbiología", "22000", "ORINA", "Frasco estéril"),
    ("MIC003", "Cultivo de hemocultivo", "Microbiología", "35000", "SANGRE", "Frascos hemocultivo"),
    ("MIC004", "Cultivo de herida / absceso", "Microbiología", "22000", "OTRO", "Recipiente estéril"),
    ("MIC005", "Cultivo respiratorio (esputo)", "Microbiología", "28000", "HISOPADO", "Recipiente estéril"),
    ("MIC006", "Cultivo de garganta (toma exudado)", "Microbiología", "22000", "HISOPADO", "Hisopado estéril"),
    ("MIC007", "KOH (hongos directo)", "Microbiología", "18000", "OTRO", "Recipiente estéril"),
    ("MIC008", "Tinción de Gram", "Microbiología", "12000", "OTRO", "Recipiente estéril"),
    ("MIC009", "Tinción de Ziehl-Neelsen (BK)", "Microbiología", "15000", "OTRO", "Recipiente estéril"),
    # ── Marcadores tumorales ────────────────────────────────────
    ("MAR001", "PSA total (Antígeno prostático)", "Marcadores tumorales", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("MAR002", "PSA libre", "Marcadores tumorales", "35000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("MAR003", "CEA (Antígeno carcinoembrionario)", "Marcadores tumorales", "40000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("MAR004", "AFP (Alfa-fetoproteína)", "Marcadores tumorales", "38000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("MAR005", "CA 125", "Marcadores tumorales", "42000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("MAR006", "CA 15-3", "Marcadores tumorales", "42000", "SANGRE", "Tubo tapa amarilla (gel)"),
    ("MAR007", "CA 19-9", "Marcadores tumorales", "42000", "SANGRE", "Tubo tapa amarilla (gel)"),
    # ── Toxicología ─────────────────────────────────────────────
    ("TOX001", "Alcohol etílico (nivel en sangre)", "Toxicología", "25000", "SANGRE", "Tubo tapa gris (fluoruro Na)"),
    ("TOX002", "Screening de drogas en orina (panel de 10)", "Toxicología", "65000", "ORINA", "Frasco estéril"),
    ("TOX003", "Plomo en sangre", "Toxicología", "45000", "SANGRE", "Tubo tapa lila (EDTA)"),
]

PARAMETROS_EXAMEN = {
    # ── Hematología ──────────────────────────────────────────
    "HEM001": [
        ("Hematocrito", "%", "36-46", 36, 46, "NUMERICO", None, 1),
        ("Hemoglobina", "g/dL", "12-16", 12, 16, "NUMERICO", None, 2),
        ("Leucocitos totales", "x10³/μL", "4-11", 4, 11, "NUMERICO", None, 3),
        ("Plaquetas", "x10³/μL", "150-400", 150, 400, "NUMERICO", None, 4),
        ("VCM", "fL", "80-100", 80, 100, "NUMERICO", None, 5),
        ("HCM", "pg", "27-33", 27, 33, "NUMERICO", None, 6),
        ("CHCM", "g/dL", "32-36", 32, 36, "NUMERICO", None, 7),
        ("Neutrófilos", "%", "40-70", 40, 70, "NUMERICO", None, 8),
        ("Linfocitos", "%", "20-40", 20, 40, "NUMERICO", None, 9),
        ("Monocitos", "%", "2-10", 2, 10, "NUMERICO", None, 10),
        ("Eosinófilos", "%", "1-6", 1, 6, "NUMERICO", None, 11),
        ("Basófilos", "%", "0-2", 0, 2, "NUMERICO", None, 12),
        ("Reticulocitos", "%", "0.5-1.5", 0.5, 1.5, "NUMERICO", None, 13),
    ],
    "HEM002": [
        ("Hemoglobina glicosilada (HbA1c)", "%", "<5.7", None, 5.7, "NUMERICO", None, 1),
    ],
    "HEM003": [
        ("Velocidad de sedimentación (VSG)", "mm/h", "0-20", 0, 20, "NUMERICO", None, 1),
    ],
    "HEM004": [
        ("Reticulocitos", "%", "0.5-1.5", 0.5, 1.5, "NUMERICO", None, 1),
    ],
    "HEM005": [
        ("Grupo ABO", None, "", None, None, "SELECT", "A,B,AB,O", 1),
        ("Factor Rh", None, "Positivo", None, None, "SELECT", "Positivo,Negativo", 2),
    ],
    "HEM006": [
        ("Coombs directa", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
    ],
    "HEM007": [
        ("Coombs indirecta", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
    ],
    "HEM008": [
        ("Descripción del frotis", None, "Normal", None, None, "TEXT", None, 1),
    ],
    "HEM009": [
        ("Tiempo de protrombina (TP)", "seg", "11-13.5", 11, 13.5, "NUMERICO", None, 1),
        ("INR", "", "0.8-1.2", 0.8, 1.2, "NUMERICO", None, 2),
    ],
    "HEM010": [
        ("Tiempo de tromboplastina parcial (TTP)", "seg", "25-35", 25, 35, "NUMERICO", None, 1),
    ],
    "HEM011": [
        ("Fibrinógeno", "mg/dL", "200-400", 200, 400, "NUMERICO", None, 1),
    ],
    "HEM012": [
        ("Dímero D", "μg/mL", "<0.5", None, 0.5, "NUMERICO", None, 1),
    ],

    # ── Química sanguínea ────────────────────────────────────
    "GLU001": [
        ("Glucosa en ayunas", "mg/dL", "70-100", 70, 100, "NUMERICO", None, 1),
    ],
    "QUI001": [
        ("Colesterol total", "mg/dL", "<200", None, 200, "NUMERICO", None, 1),
        ("Triglicéridos", "mg/dL", "<150", None, 150, "NUMERICO", None, 2),
        ("HDL", "mg/dL", ">40", 40, None, "NUMERICO", None, 3),
        ("LDL", "mg/dL", "<130", None, 130, "NUMERICO", None, 4),
        ("VLDL", "mg/dL", "<30", None, 30, "NUMERICO", None, 5),
        ("Relación CT/HDL", "", "<5", None, 5, "NUMERICO", None, 6),
    ],
    "CRE001": [
        ("Creatinina", "mg/dL", "0.6-1.2", 0.6, 1.2, "NUMERICO", None, 1),
    ],
    "URE001": [
        ("Nitrógeno ureico (BUN)", "mg/dL", "7-20", 7, 20, "NUMERICO", None, 1),
    ],
    "QUI002": [
        ("Ácido úrico", "mg/dL", "3.5-7.2", 3.5, 7.2, "NUMERICO", None, 1),
    ],
    "QUI003": [
        ("Bilirrubina total", "mg/dL", "0.1-1.2", 0.1, 1.2, "NUMERICO", None, 1),
    ],
    "QUI004": [
        ("Bilirrubina directa", "mg/dL", "0-0.3", 0, 0.3, "NUMERICO", None, 1),
    ],
    "QUI005": [
        ("Bilirrubina indirecta", "mg/dL", "0-0.8", 0, 0.8, "NUMERICO", None, 1),
    ],
    "QUI006": [
        ("TGO (AST)", "U/L", "5-40", 5, 40, "NUMERICO", None, 1),
    ],
    "QUI007": [
        ("TGP (ALT)", "U/L", "5-35", 5, 35, "NUMERICO", None, 1),
    ],
    "QUI008": [
        ("Fosfatasa alcalina", "U/L", "40-130", 40, 130, "NUMERICO", None, 1),
    ],
    "QUI009": [
        ("GGT", "U/L", "5-55", 5, 55, "NUMERICO", None, 1),
    ],
    "QUI010": [
        ("Proteínas totales", "g/dL", "6-8.3", 6, 8.3, "NUMERICO", None, 1),
    ],
    "QUI011": [
        ("Albúmina", "g/dL", "3.5-5.5", 3.5, 5.5, "NUMERICO", None, 1),
    ],
    "QUI012": [
        ("Calcio sérico", "mg/dL", "8.5-10.5", 8.5, 10.5, "NUMERICO", None, 1),
    ],
    "QUI013": [
        ("Fósforo sérico", "mg/dL", "2.5-4.5", 2.5, 4.5, "NUMERICO", None, 1),
    ],
    "QUI014": [
        ("Magnesio sérico", "mg/dL", "1.7-2.2", 1.7, 2.2, "NUMERICO", None, 1),
    ],
    "QUI015": [
        ("Hierro sérico", "μg/dL", "60-170", 60, 170, "NUMERICO", None, 1),
    ],
    "QUI016": [
        ("Ferritina", "ng/mL", "12-150", 12, 150, "NUMERICO", None, 1),
    ],
    "QUI017": [
        ("Transferrina", "mg/dL", "200-360", 200, 360, "NUMERICO", None, 1),
    ],
    "QUI018": [
        ("LDH", "U/L", "120-246", 120, 246, "NUMERICO", None, 1),
    ],
    "QUI019": [
        ("Amilasa sérica", "U/L", "28-100", 28, 100, "NUMERICO", None, 1),
    ],
    "QUI020": [
        ("Lipasa sérica", "U/L", "0-160", 0, 160, "NUMERICO", None, 1),
    ],
    "QUI021": [
        ("CK total", "U/L", "26-192", 26, 192, "NUMERICO", None, 1),
    ],
    "QUI022": [
        ("CK-MB", "U/L", "0-25", 0, 25, "NUMERICO", None, 1),
    ],
    "QUI023": [
        ("Troponina I", "ng/mL", "<0.04", None, 0.04, "NUMERICO", None, 1),
    ],
    "QUI024": [
        ("pH arterial", "", "7.35-7.45", 7.35, 7.45, "NUMERICO", None, 1),
        ("pO2 arterial", "mmHg", "80-100", 80, 100, "NUMERICO", None, 2),
        ("pCO2 arterial", "mmHg", "35-45", 35, 45, "NUMERICO", None, 3),
        ("HCO3 arterial", "mEq/L", "22-26", 22, 26, "NUMERICO", None, 4),
        ("SatO2", "%", "95-100", 95, 100, "NUMERICO", None, 5),
        ("Exceso de base (BE)", "mEq/L", "-2 a +2", -2, 2, "NUMERICO", None, 6),
    ],

    # ── Perfiles ──────────────────────────────────────────────
    "PER001": [
        ("TGO (AST)", "U/L", "5-40", 5, 40, "NUMERICO", None, 1),
        ("TGP (ALT)", "U/L", "5-35", 5, 35, "NUMERICO", None, 2),
        ("Bilirrubina total", "mg/dL", "0.1-1.2", 0.1, 1.2, "NUMERICO", None, 3),
        ("Bilirrubina directa", "mg/dL", "0-0.3", 0, 0.3, "NUMERICO", None, 4),
        ("Fosfatasa alcalina", "U/L", "40-130", 40, 130, "NUMERICO", None, 5),
        ("GGT", "U/L", "5-55", 5, 55, "NUMERICO", None, 6),
        ("Proteínas totales", "g/dL", "6-8.3", 6, 8.3, "NUMERICO", None, 7),
        ("Albúmina", "g/dL", "3.5-5.5", 3.5, 5.5, "NUMERICO", None, 8),
    ],
    "PER002": [
        ("Creatinina", "mg/dL", "0.6-1.2", 0.6, 1.2, "NUMERICO", None, 1),
        ("BUN", "mg/dL", "7-20", 7, 20, "NUMERICO", None, 2),
        ("Ácido úrico", "mg/dL", "3.5-7.2", 3.5, 7.2, "NUMERICO", None, 3),
        ("Calcio", "mg/dL", "8.5-10.5", 8.5, 10.5, "NUMERICO", None, 4),
        ("Fósforo", "mg/dL", "2.5-4.5", 2.5, 4.5, "NUMERICO", None, 5),
    ],
    "PER003": [
        ("TSH", "mUI/L", "0.4-4.0", 0.4, 4.0, "NUMERICO", None, 1),
        ("T3 libre", "pg/mL", "2.0-4.4", 2.0, 4.4, "NUMERICO", None, 2),
        ("T4 libre", "ng/dL", "0.8-1.8", 0.8, 1.8, "NUMERICO", None, 3),
    ],
    "PER004": [
        ("Hemograma completo", None, "Ver HEM001", None, None, "TEXT", None, 1),
        ("Glucosa", "mg/dL", "70-100", 70, 100, "NUMERICO", None, 2),
        ("Creatinina", "mg/dL", "0.6-1.2", 0.6, 1.2, "NUMERICO", None, 3),
        ("Tiempo de protrombina", "seg", "11-13.5", 11, 13.5, "NUMERICO", None, 4),
        ("INR", "", "0.8-1.2", 0.8, 1.2, "NUMERICO", None, 5),
        ("BUN", "mg/dL", "7-20", 7, 20, "NUMERICO", None, 6),
        ("VSG", "mm/h", "0-20", 0, 20, "NUMERICO", None, 7),
    ],
    "PER005": [
        ("Hemograma", None, "Ver HEM001", None, None, "TEXT", None, 1),
        ("VDRL", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 2),
        ("Grupo y Rh", None, "", None, None, "TEXT", None, 3),
        ("Glucosa", "mg/dL", "70-100", 70, 100, "NUMERICO", None, 4),
        ("Creatinina", "mg/dL", "0.6-1.2", 0.6, 1.2, "NUMERICO", None, 5),
        ("Urocultivo", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 6),
        ("Toxoplasmosis IgG", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 7),
        ("Rubéola IgG", None, "Positivo (protección)", None, None, "SELECT", "Negativo,Positivo", 8),
        ("VIH", None, "Negativo", None, None, "SELECT", "Negativo,Positivo,Indeterminado", 9),
        ("Hepatitis B (HBsAg)", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 10),
        ("Hemocultivo", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 11),
    ],
    "PER006": [
        ("Glucosa en ayunas", "mg/dL", "70-100", 70, 100, "NUMERICO", None, 1),
        ("Colesterol total", "mg/dL", "<200", None, 200, "NUMERICO", None, 2),
        ("Triglicéridos", "mg/dL", "<150", None, 150, "NUMERICO", None, 3),
        ("HDL", "mg/dL", ">40", 40, None, "NUMERICO", None, 4),
        ("LDL", "mg/dL", "<130", None, 130, "NUMERICO", None, 5),
        ("Creatinina", "mg/dL", "0.6-1.2", 0.6, 1.2, "NUMERICO", None, 6),
        ("BUN", "mg/dL", "7-20", 7, 20, "NUMERICO", None, 7),
        ("Ácido úrico", "mg/dL", "3.5-7.2", 3.5, 7.2, "NUMERICO", None, 8),
        ("TGO", "U/L", "5-40", 5, 40, "NUMERICO", None, 9),
        ("TGP", "U/L", "5-35", 5, 35, "NUMERICO", None, 10),
        ("HbA1c", "%", "<5.7", None, 5.7, "NUMERICO", None, 11),
    ],

    # ── Inmunología ──────────────────────────────────────────
    "PCR001": [
        ("Proteína C reactiva (PCR)", "mg/L", "<5", None, 5, "NUMERICO", None, 1),
    ],
    "INM001": [
        ("Complemento C3", "mg/dL", "90-180", 90, 180, "NUMERICO", None, 1),
    ],
    "INM002": [
        ("Complemento C4", "mg/dL", "10-40", 10, 40, "NUMERICO", None, 1),
    ],
    "INM003": [
        ("Factor reumatoide", "UI/mL", "<20", None, 20, "NUMERICO", None, 1),
    ],
    "INM004": [
        ("ANA (Anti-nucleares)", None, "Negativo", None, None, "SELECT", "Negativo,Positivo (1:80),Positivo (1:160),Positivo (1:320),Positivo (1:640)", 1),
        ("Patrón", None, "", None, None, "SELECT", "Homogéneo,Punteado,Membranoso,Nuclear,Nucleolar,Centromérico", 2),
    ],
    "INM005": [
        ("Anti-DNA de doble cadena", "UI/mL", "<20", None, 20, "NUMERICO", None, 1),
    ],
    "INM006": [
        ("Anti-streptolisina O (ASLO)", "UI/mL", "<200", None, 200, "NUMERICO", None, 1),
    ],
    "INM007": [
        ("IgA", "mg/dL", "70-400", 70, 400, "NUMERICO", None, 1),
    ],
    "INM008": [
        ("IgE total", "UI/mL", "<100", None, 100, "NUMERICO", None, 1),
    ],
    "INM009": [
        ("IgG", "mg/dL", "700-1600", 700, 1600, "NUMERICO", None, 1),
    ],
    "INM010": [
        ("IgM", "mg/dL", "40-230", 40, 230, "NUMERICO", None, 1),
    ],
    "INM011": [
        ("Anti-tiroglobulina", "UI/mL", "<115", None, 115, "NUMERICO", None, 1),
    ],
    "INM012": [
        ("Anti-TPO", "UI/mL", "<35", None, 35, "NUMERICO", None, 1),
    ],
    "INM013": [
        ("FAN (Factor anti-nuclear)", None, "Negativo", None, None, "SELECT", "Negativo,Positivo (1:80),Positivo (1:160),Positivo (1:320)", 1),
    ],
    "INM014": [
        ("VSG", "mm/h", "0-20", 0, 20, "NUMERICO", None, 1),
    ],

    # ── Endocrinología ───────────────────────────────────────
    "TSH001": [
        ("TSH", "mUI/L", "0.4-4.0", 0.4, 4.0, "NUMERICO", None, 1),
    ],
    "END001": [
        ("T3 libre", "pg/mL", "2.0-4.4", 2.0, 4.4, "NUMERICO", None, 1),
    ],
    "END002": [
        ("T4 libre", "ng/dL", "0.8-1.8", 0.8, 1.8, "NUMERICO", None, 1),
    ],
    "END003": [
        ("T3 total", "ng/dL", "80-200", 80, 200, "NUMERICO", None, 1),
    ],
    "END004": [
        ("T4 total", "μg/dL", "5-12", 5, 12, "NUMERICO", None, 1),
    ],
    "END005": [
        ("Insulina", "μU/mL", "2-25", 2, 25, "NUMERICO", None, 1),
    ],
    "END006": [
        ("Cortisol (8 AM)", "μg/dL", "5-25", 5, 25, "NUMERICO", None, 1),
    ],
    "END007": [
        ("PTH (Parathormona)", "pg/mL", "10-65", 10, 65, "NUMERICO", None, 1),
    ],
    "END008": [
        ("Testosterona", "ng/dL", "300-1000 (H) / 15-70 (M)", None, None, "NUMERICO", None, 1),
    ],
    "END009": [
        ("Estradiol", "pg/mL", "20-75 (H) / <40 (M)", None, None, "NUMERICO", None, 1),
    ],
    "END010": [
        ("Progesterona", "ng/mL", "0.2-1.5 (H) / 1.2-15.9 (F lútea)", None, None, "NUMERICO", None, 1),
    ],
    "END011": [
        ("FSH", "mUI/mL", "1.5-12.4 (H) / 3.5-12.5 (F)", None, None, "NUMERICO", None, 1),
    ],
    "END012": [
        ("LH", "mUI/mL", "1.7-8.6 (H) / 2.4-12.6 (F)", None, None, "NUMERICO", None, 1),
    ],
    "END013": [
        ("Prolactina", "ng/mL", "2-18 (H) / 2-29 (M)", None, None, "NUMERICO", None, 1),
    ],
    "END014": [
        ("Vitamina D (25-OH)", "ng/mL", "30-100", 30, 100, "NUMERICO", None, 1),
    ],
    "END015": [
        ("Vitamina B12", "pg/mL", "200-900", 200, 900, "NUMERICO", None, 1),
    ],
    "END016": [
        ("Ácido fólico", "ng/mL", "2.7-17", 2.7, 17, "NUMERICO", None, 1),
    ],

    # ── Uroanálisis ──────────────────────────────────────────
    "ORI001": [
        ("Color", None, "Amarillo claro", None, None, "SELECT", "Amarillo claro,Amarillo oscuro,Naranja,Rojo,Verde,Castroso", 1),
        ("Aspecto", None, "Claro", None, None, "SELECT", "Claro,Turbio,Espumoso,Hemático", 2),
        ("Densidad", "", "1.005-1.030", 1.005, 1.030, "NUMERICO", None, 3),
        ("pH", "", "4.5-8.0", 4.5, 8, "NUMERICO", None, 4),
        ("Proteínas", None, "Negativo", None, None, "SELECT", "Negativo,Positivo trace,Positivo 1+,Positivo 2+,Positivo 3+", 5),
        ("Glucosa", None, "Negativo", None, None, "SELECT", "Negativo,Positivo trace,Positivo 1+,Positivo 2+", 6),
        ("Cetonas", None, "Negativo", None, None, "SELECT", "Negativo,Positivo trace,Positivo 1+,Positivo 2+", 7),
        ("Bilirrubina", None, "Negativo", None, None, "SELECT", "Negativo,Positivo 1+,Positivo 2+", 8),
        ("Sangre oculta", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 9),
        ("Nitritos", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 10),
        ("Esterasa leucocitaria", None, "Negativo", None, None, "SELECT", "Negativo,Positivo trace,Positivo 1+,Positivo 2+", 11),
        ("Células epiteliales", "/campo", "0-5", 0, 5, "NUMERICO", None, 12),
        ("Leucocitos", "/campo", "0-5", 0, 5, "NUMERICO", None, 13),
        ("Hematíes", "/campo", "0-2", 0, 2, "NUMERICO", None, 14),
        ("Cilindros", "/campo", "0-2", 0, 2, "NUMERICO", None, 15),
        ("Bacterias", None, "Ninguna", None, None, "SELECT", "Ninguna,Pocas,Moderadas,Abundantes", 16),
        ("Cristales", None, "Ninguno", None, None, "SELECT", "Ninguno,Ácido úrico,Calcio oxálico,Calcio fosfático,Estruvita", 17),
    ],
    "URO001": [
        ("Crecimiento bacteriano", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Uropatógeno identificado", None, "", None, None, "TEXT", None, 2),
        ("Antibiograma", None, "Ver informe", None, None, "TEXT", None, 3),
    ],
    "URO002": [
        ("Clearance de creatinina", "mL/min", "80-120", 80, 120, "NUMERICO", None, 1),
    ],
    "URO003": [
        ("Proteinuria en 24h", "mg/24h", "<150", None, 150, "NUMERICO", None, 1),
    ],
    "URO004": [
        ("Microalbuminuria", "mg/L", "<30", None, 30, "NUMERICO", None, 1),
    ],

    # ── Coproparasitoscópico ─────────────────────────────────
    "COP001": [
        ("Aspecto", None, "", None, None, "SELECT", "Formado,Blando,Líquido,Con sangre,Con moco", 1),
        ("Sangre oculta", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 2),
        ("Leucocitos", "/campo", "0-2", 0, 2, "NUMERICO", None, 3),
        ("Parásitos observados", None, "Ninguno", None, None, "SELECT", "Ninguno,Ascaris lumbricoides,Trichuris trichiura,Enterobius vermicularis,Hymenolepis nana,Strongyloides stercoralis,Entamoeba histolytica,Giardia lamblia", 4),
        ("Quistes / Trofozoitos", "/campo", "0", 0, 0, "NUMERICO", None, 5),
        ("Larvas", "/campo", "0", 0, 0, "NUMERICO", None, 6),
        ("Huevos", "/campo", "0", 0, 0, "NUMERICO", None, 7),
    ],
    "COP002": [
        ("Parásito encontrado", None, "Ninguno", None, None, "SELECT", "Ninguno,Ascaris,Trichiuris,Enterobius,Hymenolepis,Strongyloides,Entamoeba,Giardia", 1),
        ("Muestra 1", None, "", None, None, "TEXT", None, 2),
        ("Muestra 2", None, "", None, None, "TEXT", None, 3),
        ("Muestra 3", None, "", None, None, "TEXT", None, 4),
    ],

    # ── Serología ────────────────────────────────────────────
    "VIH001": [
        ("Resultado VIH (Elisa)", None, "No reactivo", None, None, "SELECT", "Reactivo,No reactivo,Indeterminado", 1),
        ("Confirmatorio (Western blot)", None, "No reactivo", None, None, "SELECT", "Reactivo,No reactivo,Pendiente", 2),
    ],
    "SER001": [
        ("HBsAg", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
    ],
    "SER002": [
        ("Anti-HBs", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Título", "mUI/mL", "<10", None, 10, "NUMERICO", None, 2),
    ],
    "SER003": [
        ("Anti-HBc total", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
    ],
    "SER004": [
        ("Anti-HBc IgM", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
    ],
    "SER005": [
        ("HBeAg", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
    ],
    "SER006": [
        ("Anti-VHC", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
    ],
    "SER007": [
        ("NS1 Antígeno dengue", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
        ("IgM dengue", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 2),
        ("IgG dengue", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 3),
    ],
    "SER008": [
        ("VDRL", None, "Negativo", None, None, "SELECT", "Negativo,Positivo 1:2,Positivo 1:4,Positivo 1:8,Positivo 1:16", 1),
    ],
    "SER009": [
        ("FTA-ABS", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
    ],
    "SER010": [
        ("Anti-T. cruzi (Chagas)", None, "Negativo", None, None, "SELECT", "Negativo,Positivo,Indeterminado", 1),
    ],
    "SER011": [
        ("Toxoplasmosis IgG", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Toxoplasmosis IgM", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 2),
    ],
    "SER012": [
        ("Rubéola IgG", None, "", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Rubéola IgM", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 2),
    ],
    "SER013": [
        ("CMV IgG", None, "", None, None, "SELECT", "Negativo,Positivo", 1),
        ("CMV IgM", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 2),
    ],
    "SER014": [
        ("Herpes 1 IgG", None, "", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Herpes 2 IgG", None, "", None, None, "SELECT", "Negativo,Positivo", 2),
    ],
    "SER015": [
        ("Mononucleosis (EBV VCA IgM)", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Mononucleosis (EBV VCA IgG)", None, "", None, None, "SELECT", "Negativo,Positivo", 2),
    ],

    # ── Coagulación ──────────────────────────────────────────
    "COA001": [
        ("Tiempo de protrombina (TP)", "seg", "11-13.5", 11, 13.5, "NUMERICO", None, 1),
        ("INR", "", "0.8-1.2", 0.8, 1.2, "NUMERICO", None, 2),
        ("TTP", "seg", "25-35", 25, 35, "NUMERICO", None, 3),
        ("Fibrinógeno", "mg/dL", "200-400", 200, 400, "NUMERICO", None, 4),
    ],
    "COA002": [
        ("INR", "", "0.8-1.2", 0.8, 1.2, "NUMERICO", None, 1),
    ],

    # ── Microbiología ────────────────────────────────────────
    "MIC001": [
        ("Crecimiento bacteriano", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Agente identificado", None, "", None, None, "TEXT", None, 2),
        ("Antibiograma", None, "Ver informe", None, None, "TEXT", None, 3),
    ],
    "MIC002": [
        ("Crecimiento", None, "Negativo", None, None, "SELECT", "Negativo,Positivo (>100,000 UFC/mL),Positivo (10,000-100,000)", 1),
        ("Uropatógeno", None, "", None, None, "TEXT", None, 2),
        ("Antibiograma", None, "Ver informe", None, None, "TEXT", None, 3),
    ],
    "MIC003": [
        ("Hemocultivo", None, "Negativo (48h)", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Agente", None, "", None, None, "TEXT", None, 2),
    ],
    "MIC004": [
        ("Crecimiento", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Agente", None, "", None, None, "TEXT", None, 2),
    ],
    "MIC005": [
        ("Crecimiento", None, "Flora normal", None, None, "SELECT", "Flora normal,Crecimiento patológico", 1),
        ("Agente", None, "", None, None, "TEXT", None, 2),
    ],
    "MIC006": [
        ("Crecimiento", None, "Negativo", None, None, "SELECT", "Negativo,Positivo (Strep. pyogenes),Positivo (Staf. aureus),Positivo (otro)", 1),
    ],
    "MIC007": [
        ("KOH directo", None, "Negativo", None, None, "SELECT", "Negativo,Positivo (hifas),Positivo (levaduras)", 1),
    ],
    "MIC008": [
        ("Tinción de Gram", None, "", None, None, "TEXT", None, 1),
    ],
    "MIC009": [
        ("BAAR (Bacilos Ácido Alcohol Resistentes)", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Número de bacilos", "/100 campos", "0", 0, 0, "NUMERICO", None, 2),
    ],

    # ── Marcadores tumorales ─────────────────────────────────
    "MAR001": [
        ("PSA total", "ng/mL", "<4.0", None, 4, "NUMERICO", None, 1),
    ],
    "MAR002": [
        ("PSA libre", "ng/mL", "<0.9", None, 0.9, "NUMERICO", None, 1),
        ("Relación PSA libre/total", "%", ">25", 25, None, "NUMERICO", None, 2),
    ],
    "MAR003": [
        ("CEA", "ng/mL", "<3.0 (no fumador) / <5.0 (fumador)", None, 5, "NUMERICO", None, 1),
    ],
    "MAR004": [
        ("AFP (Alfa-fetoproteína)", "ng/mL", "<10", None, 10, "NUMERICO", None, 1),
    ],
    "MAR005": [
        ("CA 125", "U/mL", "<35", None, 35, "NUMERICO", None, 1),
    ],
    "MAR006": [
        ("CA 15-3", "U/mL", "<30", None, 30, "NUMERICO", None, 1),
    ],
    "MAR007": [
        ("CA 19-9", "U/mL", "<37", None, 37, "NUMERICO", None, 1),
    ],

    # ── Toxicología ──────────────────────────────────────────
    "TOX001": [
        ("Alcohol etílico", "mg/dL", "<10", None, 10, "NUMERICO", None, 1),
    ],
    "TOX002": [
        ("Anfetaminas", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 1),
        ("Cocaína/metabolitos", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 2),
        ("Cannabis (THC)", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 3),
        ("Opiáceos", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 4),
        ("Benzodiazepinas", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 5),
        ("Barbitúricos", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 6),
        ("Metadona", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 7),
        ("Fenciclidina (PCP)", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 8),
        ("Metanfetaminas", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 9),
        ("Nicotina", None, "Negativo", None, None, "SELECT", "Negativo,Positivo", 10),
    ],
    "TOX003": [
        ("Plomo en sangre", "μg/dL", "<10", None, 10, "NUMERICO", None, 1),
    ],
}

DEPARTAMENTOS_CIUDADES = {
    "Amazonas": ["Leticia", "Puerto Nariño"],
    "Antioquia": ["Medellín", "Bello", "Itagüí", "Envigado", "Rionegro", "Apartadó", "Turbo", "Sabaneta"],
    "Arauca": ["Arauca", "Saravena", "Tame"],
    "Atlántico": ["Barranquilla", "Soledad", "Malambo", "Sabanalarga"],
    "Bogotá D.C.": ["Bogotá D.C."],
    "Bolívar": ["Cartagena", "Magangué", "Turbaco", "Arjona"],
    "Boyacá": ["Tunja", "Duitama", "Sogamoso", "Chiquinquirá"],
    "Caldas": ["Manizales", "La Dorada", "Chinchiná", "Villamaría"],
    "Caquetá": ["Florencia"],
    "Casanare": ["Yopal"],
    "Cauca": ["Popayán", "Santander de Quilichao"],
    "Cesar": ["Valledupar", "Aguachica"],
    "Chocó": ["Quibdó"],
    "Córdoba": ["Montería", "Lorica", "Cereté"],
    "Cundinamarca": ["Soacha", "Chía", "Zipaquirá", "Facatativá", "Fusagasugá", "Girardot", "Mosquera", "Madrid"],
    "Guainía": ["Inírida"],
    "Guaviare": ["San José del Guaviare"],
    "Huila": ["Neiva", "Pitalito", "Garzón"],
    "La Guajira": ["Riohacha", "Maicao"],
    "Magdalena": ["Santa Marta", "Ciénaga"],
    "Meta": ["Villavicencio", "Acacías", "Granada"],
    "Nariño": ["Pasto", "Ipiales", "Tumaco"],
    "Norte de Santander": ["Cúcuta", "Ocaña", "Pamplona"],
    "Putumayo": ["Mocoa"],
    "Quindío": ["Armenia", "Calarcá", "Montenegro", "Circasia", "La Tebaida"],
    "Risaralda": ["Pereira", "Dosquebradas", "Santa Rosa de Cabal"],
    "San Andrés y Providencia": ["San Andrés", "Providencia"],
    "Santander": ["Bucaramanga", "Floridablanca", "Girón", "Piedecuesta", "Barrancabermeja"],
    "Sucre": ["Sincelejo", "Corozal"],
    "Tolima": ["Ibagué", "Espinal", "Melgar"],
    "Valle del Cauca": ["Cali", "Palmira", "Buenaventura", "Tuluá", "Buga", "Cartago", "Yumbo"],
    "Vaupés": ["Mitú"],
    "Vichada": ["Puerto Carreño"],
}

# Modulo = misma etiqueta que aparece en el menu lateral (ver
# app/security/sesion.py -> TODOS_LOS_MODULOS). "Administrador" no
# aparece aqui porque se le da acceso a todo automaticamente.
ROLES_MODULOS = {
    "Médico": [
        "Dashboard", "Ordenes", "ProcesarValidar", "Examenes",
    ],
    "Enfermero": [
        "ProcesarValidar",
    ],
    "Bacteriólogo": [
        "Dashboard", "ProcesarValidar",
    ],
    "Recepción": [
        "Dashboard", "Pacientes", "Profesionales", "Ordenes", "EPS",
        "Convenios", "Agenda", "Facturacion", "Inventario",
    ],
}


def seed_datos_particular() -> None:
    db = SessionLocal()
    try:
        eps = db.query(EPS).filter(EPS.codigo == CODIGO_EPS_PARTICULAR).first()
        if eps is None:
            eps = EPS(
                codigo=CODIGO_EPS_PARTICULAR,
                nombre="PARTICULAR (paciente sin EPS)",
                activo=True,
            )
            db.add(eps)
            db.commit()
            db.refresh(eps)

        convenio = db.query(Convenio).filter(
            Convenio.codigo == CODIGO_CONVENIO_PARTICULAR
        ).first()
        if convenio is None:
            convenio = Convenio(
                eps_id=eps.id,
                codigo=CODIGO_CONVENIO_PARTICULAR,
                nombre="Convenio Particular - Pago directo del paciente",
                fecha_inicio=date.today(),
                tipo_copago="PORCENTAJE",
                valor_copago=Decimal("100"),
                observaciones=(
                    "Convenio de uso interno: el paciente paga el 100% del "
                    "valor de la factura. Se usa para exámenes particulares "
                    "solicitados desde la Agenda sin orden médica ni EPS."
                ),
                activo=True,
            )
            db.add(convenio)
            db.commit()

        medico = db.query(Medico).filter(
            Medico.registro_medico == REGISTRO_MEDICO_PARTICULAR
        ).first()
        if medico is None:
            medico = Medico(
                registro_medico=REGISTRO_MEDICO_PARTICULAR,
                nombres="Paciente",
                apellidos="Particular (sin médico remitente)",
                activo=True,
            )
            db.add(medico)
            db.commit()

    finally:
        db.close()


def seed_usuario_admin() -> None:
    db = SessionLocal()
    try:
        existente = db.query(Usuario).filter(Usuario.usuario == USUARIO_ADMIN).first()
        if existente is not None:
            print(f"[seed] El usuario '{USUARIO_ADMIN}' ya existía (id={existente.id}). No se modificó.")
            return

        admin = Usuario(
            tipo_documento="CC",
            documento="0000000000",
            nombres="Administrador",
            apellidos="del Sistema",
            correo="admin@labsys.local",
            cargo="Administrador del sistema",
            usuario=USUARIO_ADMIN,
            password_hash=generar_hash(PASSWORD_ADMIN_INICIAL),
            cambiar_password=True,
            activo=True,
        )
        db.add(admin)
        db.commit()
        print(f"[seed] Usuario '{USUARIO_ADMIN}' creado correctamente.")
    finally:
        db.close()


def seed_examenes_base() -> None:
    db = SessionLocal()
    try:
        creados = 0
        actualizados = 0
        for codigo, nombre, categoria, precio, tipo_muestra, recipiente in EXAMENES_BASE:
            existente = db.query(Examen).filter(Examen.codigo == codigo).first()
            if existente is not None:
                if not existente.tipo_muestra and tipo_muestra:
                    existente.tipo_muestra = tipo_muestra
                    existente.recipiente = recipiente
                    actualizados += 1
                continue

            db.add(Examen(
                codigo=codigo,
                nombre=nombre,
                categoria=categoria,
                precio=Decimal(precio),
                tipo_muestra=tipo_muestra,
                recipiente=recipiente,
                activo=True,
            ))
            creados += 1

        if creados or actualizados:
            db.commit()
            if creados:
                print(f"[seed] {creados} examen(es) del catálogo base creado(s).")
            if actualizados:
                print(f"[seed] {actualizados} examen(es) actualizado(s) con tipo_muestra/recipiente.")
        else:
            print("[seed] El catálogo de exámenes base ya existía.")
    finally:
        db.close()


def seed_geografia_colombia() -> None:
    from app.models.ciudad import Ciudad
    from app.models.departamento import Departamento

    db = SessionLocal()
    try:
        if db.query(Departamento).count() > 0:
            print("[seed] El catálogo de departamentos/ciudades ya existía.")
            return

        total_ciudades = 0
        for nombre_departamento, ciudades in DEPARTAMENTOS_CIUDADES.items():
            dep = Departamento(nombre=nombre_departamento)
            db.add(dep)
            db.flush()

            for nombre_ciudad in ciudades:
                db.add(Ciudad(nombre=nombre_ciudad, departamento_id=dep.id))
                total_ciudades += 1

        db.commit()
        print(f"[seed] Cargados {len(DEPARTAMENTOS_CIUDADES)} departamentos y {total_ciudades} ciudades de Colombia.")
    finally:
        db.close()


def seed_roles_y_permisos() -> None:
    from app.models.permiso import Permiso
    from app.models.rol import Rol
    from app.models.rol_permiso import RolPermiso
    from app.models.usuario_rol import UsuarioRol
    from app.security.sesion import TODOS_LOS_MODULOS

    db = SessionLocal()
    try:
        if db.query(Rol).count() > 0:
            print("[seed] Los roles ya existían.")
            return

        # Un permiso por modulo (acceso a esa pantalla completa).
        permiso_por_modulo = {}
        for modulo in TODOS_LOS_MODULOS:
            permiso = Permiso(
                codigo=f"ACCESO_{modulo.upper()}",
                nombre=f"Acceso a {modulo}",
                modulo=modulo,
                activo=True,
            )
            db.add(permiso)
            db.flush()
            permiso_por_modulo[modulo] = permiso

        # Administrador: todos los modulos.
        rol_admin = Rol(nombre="Administrador", descripcion="Acceso completo al sistema.", activo=True)
        db.add(rol_admin)
        db.flush()
        for modulo in TODOS_LOS_MODULOS:
            db.add(RolPermiso(rol_id=rol_admin.id, permiso_id=permiso_por_modulo[modulo].id))

        # Los demas roles, segun ROLES_MODULOS.
        for nombre_rol, modulos in ROLES_MODULOS.items():
            rol = Rol(nombre=nombre_rol, descripcion=f"Rol de {nombre_rol}.", activo=True)
            db.add(rol)
            db.flush()
            for modulo in modulos:
                if modulo in permiso_por_modulo:
                    db.add(RolPermiso(rol_id=rol.id, permiso_id=permiso_por_modulo[modulo].id))

        db.commit()
        print(f"[seed] Creados {1 + len(ROLES_MODULOS)} roles con sus permisos por módulo.")

        # El usuario admin queda con el rol Administrador.
        admin = db.query(Usuario).filter(Usuario.usuario == USUARIO_ADMIN).first()
        if admin:
            ya_tiene = db.query(UsuarioRol).filter(
                UsuarioRol.usuario_id == admin.id, UsuarioRol.rol_id == rol_admin.id
            ).first()
            if not ya_tiene:
                db.add(UsuarioRol(usuario_id=admin.id, rol_id=rol_admin.id))
                db.commit()
                print("[seed] Usuario 'admin' asignado al rol 'Administrador'.")
    finally:
        db.close()


def seed_parametros_examen() -> None:
    from app.models.examen import Examen
    from app.models.parametro_examen import ParametroExamen

    db = SessionLocal()
    try:
        if db.query(ParametroExamen).count() > 0:
            print("[seed] Los parámetros de exámenes ya existían.")
            return

        creados = 0
        for codigo_examen, parametros in PARAMETROS_EXAMEN.items():
            examen = db.query(Examen).filter(Examen.codigo == codigo_examen).first()
            if examen is None:
                continue

            for (
                nombre,
                unidad,
                valor_ref,
                val_min,
                val_max,
                tipo,
                opciones,
                orden,
            ) in parametros:
                db.add(ParametroExamen(
                    examen_id=examen.id,
                    nombre=nombre,
                    unidad=unidad,
                    valor_referencia=valor_ref,
                    valor_minimo=val_min,
                    valor_maximo=val_max,
                    tipo=tipo,
                    opciones=opciones,
                    orden=orden,
                ))
                creados += 1

        if creados:
            db.commit()
            print(f"[seed] {creados} parámetro(s) de exámenes creado(s).")
        else:
            print("[seed] No se encontraron exámenes base para crear parámetros.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_datos_particular()
    seed_usuario_admin()
    seed_examenes_base()
    seed_geografia_colombia()
    seed_roles_y_permisos()
    seed_parametros_examen()
