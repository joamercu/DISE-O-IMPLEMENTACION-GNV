"""
Configuración global de la aplicación
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la aplicación
APP_TITLE = "Cálculos Combustible Vehicular GNC/GNL"
APP_ICON = "⛽"
APP_LAYOUT = "wide"

# Valores por defecto del proyecto
DEFAULT_CLIENT = 'PETROLIQUIDOS'
DEFAULT_VERSION = '1.0'
DEFAULT_DATE = '2024-12-19'

# Parámetros por defecto de cálculo
DEFAULT_CONSUMO_DIESEL = 35.0
DEFAULT_AUTONOMIA = 600.0
DEFAULT_PODER_CALORIFICO = 35.8
DEFAULT_LHV_CH4 = 50.0
DEFAULT_EFICIENCIA = 0.95
DEFAULT_PRESION = 200.0
DEFAULT_TEMPERATURA = 25.0
DEFAULT_FACTOR_Z = 0.85
DEFAULT_VOLUMEN_TANQUE = 0.080
DEFAULT_PESO_TANQUE = 65.0
DEFAULT_PESO_SOPORTES = 10.0
DEFAULT_PESO_ACCESORIOS = 5.0

# Parámetros por defecto para GNL (Gas Natural Licuado)
DEFAULT_CONSUMO_GNL = 50.0  # L/100 km (estimado, mayor que diesel por menor densidad energética)
DEFAULT_PODER_CALORIFICO_GNL = 22.5  # MJ/L (valor representativo, rango: 20-25 MJ/L)
DEFAULT_DENSIDAD_GNL = 0.45  # kg/L (valor representativo, rango: 0.42-0.50 kg/L)
DEFAULT_EFICIENCIA_GNL_GNV = 0.92  # Eficiencia de conversión GNL a GNV (estimado)

# Constantes físicas
CONSTANTE_GASES = 8.314
MASA_MOLAR_CH4 = 0.01604

# Archivos - Rutas relativas desde src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Archivos de datos
MANIFEST_FILE = os.path.join(DATA_DIR, 'PETROLIQUIDOS_GNV_manifest_v1.json')
REMEMBERED_USER_FILE = os.path.join(DATA_DIR, 'remembered_user.json')
USERS_DB_FILE = os.path.join(DATA_DIR, 'users_db.json')

# Archivos de entregables
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
DELIVERABLE_MD = os.path.join(DOCS_DIR, 'PETROLIQUIDOS_GNV_Informe_v1.md')
DELIVERABLE_XLSX = os.path.join(OUTPUTS_DIR, 'PETROLIQUIDOS_GNV_BOM_v1.xlsx')
DELIVERABLE_XML = os.path.join(ASSETS_DIR, 'PETROLIQUIDOS_GNV_PID_v1.drawio.xml')

# XML de referencia para usar como plantilla base
REFERENCE_XML_ROOT = os.path.join(BASE_DIR, 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.xml')
REFERENCE_XML_ASSETS = os.path.join(ASSETS_DIR, 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.xml')

# Determinar qué XML de referencia usar (prioridad: raíz > assets)
if os.path.exists(REFERENCE_XML_ROOT):
    REFERENCE_XML = REFERENCE_XML_ROOT
elif os.path.exists(REFERENCE_XML_ASSETS):
    REFERENCE_XML = REFERENCE_XML_ASSETS
else:
    # Fallback al XML en assets si existe
    REFERENCE_XML = DELIVERABLE_XML

# PDF de referencia para comparación
REFERENCE_PDF_ROOT = os.path.join(BASE_DIR, 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.pdf')
REFERENCE_PDF_ASSETS = os.path.join(ASSETS_DIR, 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.pdf')

# Determinar qué PDF usar (prioridad: outputs > assets > raíz > referencia)
ELK_FINAL_PDF_OUTPUTS = os.path.join(OUTPUTS_DIR, 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_FINAL.pdf')
ELK_FINAL_PDF_ASSETS = os.path.join(ASSETS_DIR, 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_FINAL.pdf')
ELK_FINAL_PDF_ROOT = os.path.join(BASE_DIR, 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_FINAL.pdf')

if os.path.exists(ELK_FINAL_PDF_OUTPUTS):
    DELIVERABLE_PDF = ELK_FINAL_PDF_OUTPUTS
elif os.path.exists(ELK_FINAL_PDF_ASSETS):
    DELIVERABLE_PDF = ELK_FINAL_PDF_ASSETS
elif os.path.exists(ELK_FINAL_PDF_ROOT):
    DELIVERABLE_PDF = ELK_FINAL_PDF_ROOT
elif os.path.exists(REFERENCE_PDF_ROOT):
    DELIVERABLE_PDF = REFERENCE_PDF_ROOT
elif os.path.exists(REFERENCE_PDF_ASSETS):
    DELIVERABLE_PDF = REFERENCE_PDF_ASSETS
else:
    # Fallback al PDF en assets si existe
    DELIVERABLE_PDF = os.path.join(ASSETS_DIR, 'PETROLIQUIDOS_GNV_PID_v1.pdf')

# ============================================
# CONFIGURACIÓN BASE DE DATOS POSTGRESQL
# ============================================
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'gnv_app')
DB_USER = os.getenv('DB_USER', 'gnv_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# String de conexión PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ============================================
# CONFIGURACIÓN EMAIL SMTP
# ============================================
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@weldtech.com')

