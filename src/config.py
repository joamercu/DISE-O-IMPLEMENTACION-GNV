"""
Configuración global de la aplicación
"""
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
DEFAULT_AUTONOMIA = 800.0
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

# Constantes físicas
CONSTANTE_GASES = 8.314
MASA_MOLAR_CH4 = 0.01604

# Archivos - Rutas relativas desde src/
import os
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

