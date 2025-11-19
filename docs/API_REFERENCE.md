# 📚 Referencia de API - Aplicación GNV

## Módulos Principales

### `auth_system.py`

Sistema de autenticación y gestión de usuarios.

#### Funciones

**`hash_password(password: str) -> str`**
- Genera hash SHA-256 de la contraseña
- **Parámetros:**
  - `password`: Contraseña en texto plano
- **Retorna:** Hash hexadecimal de la contraseña

**`verify_user(username: str, password: str) -> Optional[Dict]`**
- Verifica credenciales de usuario
- **Parámetros:**
  - `username`: Nombre de usuario
  - `password`: Contraseña en texto plano
- **Retorna:** Diccionario con datos del usuario o `None` si inválido
- **Formato retorno:**
  ```python
  {
      'username': str,
      'role': str,
      'created_at': str
  }
  ```

**`create_user(username: str, password: str, role: str) -> bool`**
- Crea un nuevo usuario
- **Parámetros:**
  - `username`: Nombre de usuario
  - `password`: Contraseña en texto plano
  - `role`: Rol del usuario ('Administrador' o 'Cliente')
- **Retorna:** `True` si se creó, `False` si el usuario ya existe

**`get_user_role(username: str) -> Optional[str]`**
- Obtiene el rol de un usuario
- **Parámetros:**
  - `username`: Nombre de usuario
- **Retorna:** Rol del usuario o `None` si no existe

**`init_default_users() -> Dict`**
- Inicializa usuarios por defecto si no existen
- **Retorna:** Diccionario de usuarios

---

### `utils/calculation_engine.py`

Motor de cálculos para sistemas GNV/CNG.

#### Funciones

**`calcular_sistema_gnv(...) -> Dict`**
- Calcula todos los parámetros del sistema GNV

**Parámetros:**
```python
calcular_sistema_gnv(
    consumo_diesel: float,              # L/100 km
    autonomia_deseada: float,           # km
    poder_calorifico_diesel: float,     # MJ/L
    lhv_ch4: float,                     # MJ/kg
    eficiencia_conversion: float,       # 0.0-1.0
    presion_llenado: float,            # bar
    temperatura_operacion: float,      # °C
    factor_compresibilidad: float,     # 0.0-1.0
    volumen_unitario_tanque: float,    # m³
    peso_tanque_vacio: float,          # kg
    peso_soportes: float,              # kg
    peso_accesorios: float,            # kg
    constante_gases: float = 8.314,    # J/(mol·K)
    masa_molar_ch4: float = 0.01604    # kg/mol
)
```

**Retorna:**
```python
{
    'volumen_diesel_equivalente': float,  # L
    'energia_requerida': float,           # MJ
    'masa_ch4_requerida': float,          # kg
    'volumen_gas': float,                 # m³
    'numero_tanques': int,                # unidades
    'peso_adicional_total': float,        # kg
    'presion_llenado': float,             # bar
    'temperatura_operacion': float,       # °C
    'consumo_base': float,                # L/100 km
    'autonomia_objetivo': float           # km
}
```

**Ejemplo:**
```python
from utils.calculation_engine import calcular_sistema_gnv

resultado = calcular_sistema_gnv(
    consumo_diesel=35.0,
    autonomia_deseada=800.0,
    poder_calorifico_diesel=35.8,
    lhv_ch4=50.0,
    eficiencia_conversion=0.95,
    presion_llenado=200.0,
    temperatura_operacion=25.0,
    factor_compresibilidad=0.85,
    volumen_unitario_tanque=0.080,
    peso_tanque_vacio=65.0,
    peso_soportes=10.0,
    peso_accesorios=5.0
)

print(f"Tanques requeridos: {resultado['numero_tanques']}")
print(f"Peso adicional: {resultado['peso_adicional_total']} kg")
```

**`calcular_sensibilidad(consumo_base, autonomia_base, variacion, otros_parametros) -> Dict`**
- Calcula análisis de sensibilidad

**Parámetros:**
- `consumo_base`: Consumo base en L/100km
- `autonomia_base`: Autonomía base en km
- `variacion`: Porcentaje de variación (5-30)
- `otros_parametros`: Dict con parámetros para `calcular_sistema_gnv()`

**Retorna:**
```python
{
    'variaciones_consumo': [
        {
            'variacion': int,      # %
            'consumo': float,      # L/100km
            'resultado': Dict      # Resultado de calcular_sistema_gnv
        },
        ...
    ],
    'variaciones_autonomia': [
        {
            'variacion': int,      # %
            'autonomia': float,    # km
            'resultado': Dict      # Resultado de calcular_sistema_gnv
        },
        ...
    ]
}
```

---

### `utils/manifest_utils.py`

Utilidades para manejo del manifest.

#### Funciones

**`load_manifest() -> Optional[Dict]`**
- Carga el manifest JSON del proyecto
- **Retorna:** Diccionario con datos del manifest o `None` si hay error
- **Archivo:** `data/PETROLIQUIDOS_GNV_manifest_v1.json`

**`save_manifest(manifest_data: Dict) -> bool`**
- Guarda el manifest JSON
- **Parámetros:**
  - `manifest_data`: Diccionario con datos del manifest
- **Retorna:** `True` si se guardó correctamente, `False` si hay error

**`generate_manifest_html(manifest_data: Dict) -> str`**
- Genera un archivo HTML formateado del manifest
- **Parámetros:**
  - `manifest_data`: Diccionario con datos del manifest
- **Retorna:** String con HTML completo

---

### `utils/auth_utils.py`

Utilidades de autenticación.

#### Funciones

**`load_remembered_user() -> Tuple[str, str]`**
- Carga el último usuario recordado
- **Retorna:** Tupla (username, role) o ('', 'Cliente') si no existe

**`save_remembered_user(username: str, role: str) -> None`**
- Guarda el usuario para recordarlo
- **Parámetros:**
  - `username`: Nombre de usuario
  - `role`: Rol del usuario

**`clear_remembered_user() -> None`**
- Elimina el usuario recordado

---

### `utils/drawio_agent.py`

Agente generador de diagramas P&ID en formato draw.io.

#### Clase Principal

**`DrawIOAgent`**

Clase principal para generar diagramas draw.io con variables dinámicas.

**Inicialización:**
```python
agent = DrawIOAgent(output_path: str = None)
```

**Parámetros:**
- `output_path`: Ruta donde guardar el diagrama generado (opcional)

#### Métodos Principales

**`load_calculation_variables(calculation_results: Dict) -> None`**
- Carga variables de los cálculos del sistema
- **Parámetros:**
  - `calculation_results`: Diccionario con resultados de `calcular_sistema_gnv()`

**`generate_diagram_from_engineering(calculation_results: Dict, client_name: str = "PETROLIQUIDOS", doc_path: str = None) -> str`**
- Genera un diagrama draw.io completo basado en las instrucciones de ingeniería
- **Parámetros:**
  - `calculation_results`: Resultados del cálculo del sistema
  - `client_name`: Nombre del cliente
  - `doc_path`: Ruta al documento de ingeniería (opcional)
- **Retorna:** String con el XML del diagrama generado

**`save_diagram(xml_content: str, filepath: str = None) -> str`**
- Guarda el diagrama en un archivo
- **Retorna:** Ruta del archivo guardado

---

### `utils/drawio_integration.py`

Integración del agente draw.io con Streamlit.

#### Funciones

**`show_diagram_generator(calculation_results: dict, client_name: str = "PETROLIQUIDOS") -> None`**
- Muestra la interfaz Streamlit para generar/actualizar diagramas draw.io
- **Parámetros:**
  - `calculation_results`: Resultados del cálculo del sistema
  - `client_name`: Nombre del cliente
- **Funcionalidades:**
  - Generación automática de diagramas
  - Visualización de variables
  - Descarga del diagrama en formato .drawio.xml

---

### `utils/file_handler.py`

Manejo de archivos y descargas.

#### Funciones

**`get_file_mime_type(filename: str) -> str`**
- Obtiene el MIME type según la extensión
- **Parámetros:**
  - `filename`: Nombre del archivo
- **Retorna:** MIME type (ej: 'application/json', 'text/html')

**`create_download_link(file_path: str, display_text: str, button_style: str = "default") -> Optional[str]`**
- Crea un enlace de descarga para un archivo
- **Parámetros:**
  - `file_path`: Ruta completa del archivo
  - `display_text`: Texto a mostrar en el botón
  - `button_style`: Estilo ('default' o 'primary')
- **Retorna:** HTML del enlace o `None` si el archivo no existe

**`file_exists(file_path: str) -> bool`**
- Verifica si un archivo existe
- **Parámetros:**
  - `file_path`: Ruta del archivo
- **Retorna:** `True` si existe, `False` si no

---

### `config.py`

Configuración centralizada.

#### Constantes

**Configuración de la Aplicación:**
```python
APP_TITLE = "Cálculos Combustible Vehicular GNC/GNL"
APP_ICON = "⛽"
APP_LAYOUT = "wide"
```

**Valores por Defecto del Proyecto:**
```python
DEFAULT_CLIENT = 'PETROLIQUIDOS'
DEFAULT_VERSION = '1.0'
DEFAULT_DATE = '2024-12-19'
```

**Parámetros por Defecto de Cálculo:**
```python
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
```

**Constantes Físicas:**
```python
CONSTANTE_GASES = 8.314
MASA_MOLAR_CH4 = 0.01604
```

**Rutas de Archivos:**
```python
MANIFEST_FILE = os.path.join(DATA_DIR, 'PETROLIQUIDOS_GNV_manifest_v1.json')
REMEMBERED_USER_FILE = os.path.join(DATA_DIR, 'remembered_user.json')
USERS_DB_FILE = os.path.join(DATA_DIR, 'users_db.json')
DELIVERABLE_MD = os.path.join(DOCS_DIR, 'PETROLIQUIDOS_GNV_Informe_v1.md')
DELIVERABLE_XLSX = os.path.join(OUTPUTS_DIR, 'PETROLIQUIDOS_GNV_BOM_v1.xlsx')
DELIVERABLE_XML = os.path.join(ASSETS_DIR, 'PETROLIQUIDOS_GNV_PID_v1.drawio.xml')
```

---

## Ejemplos de Uso

### Ejemplo 1: Calcular Sistema GNV

```python
from utils.calculation_engine import calcular_sistema_gnv
from config import (
    DEFAULT_PODER_CALORIFICO, DEFAULT_LHV_CH4, DEFAULT_EFICIENCIA,
    DEFAULT_PRESION, DEFAULT_TEMPERATURA, DEFAULT_FACTOR_Z,
    DEFAULT_VOLUMEN_TANQUE, DEFAULT_PESO_TANQUE,
    DEFAULT_PESO_SOPORTES, DEFAULT_PESO_ACCESORIOS,
    CONSTANTE_GASES, MASA_MOLAR_CH4
)

resultado = calcular_sistema_gnv(
    consumo_diesel=35.0,
    autonomia_deseada=800.0,
    poder_calorifico_diesel=DEFAULT_PODER_CALORIFICO,
    lhv_ch4=DEFAULT_LHV_CH4,
    eficiencia_conversion=DEFAULT_EFICIENCIA,
    presion_llenado=DEFAULT_PRESION,
    temperatura_operacion=DEFAULT_TEMPERATURA,
    factor_compresibilidad=DEFAULT_FACTOR_Z,
    volumen_unitario_tanque=DEFAULT_VOLUMEN_TANQUE,
    peso_tanque_vacio=DEFAULT_PESO_TANQUE,
    peso_soportes=DEFAULT_PESO_SOPORTES,
    peso_accesorios=DEFAULT_PESO_ACCESORIOS,
    constante_gases=CONSTANTE_GASES,
    masa_molar_ch4=MASA_MOLAR_CH4
)

print(f"Tanques: {resultado['numero_tanques']}")
print(f"Peso: {resultado['peso_adicional_total']} kg")
```

### Ejemplo 2: Cargar y Modificar Manifest

```python
from utils.manifest_utils import load_manifest, save_manifest

# Cargar manifest
manifest = load_manifest()

if manifest:
    # Modificar datos
    manifest['project']['status'] = 'En Progreso'
    
    # Guardar cambios
    if save_manifest(manifest):
        print("Manifest actualizado correctamente")
```

### Ejemplo 3: Verificar Usuario

```python
from auth_system import verify_user

user = verify_user('admin', 'admin123')
if user:
    print(f"Usuario: {user['username']}")
    print(f"Rol: {user['role']}")
else:
    print("Credenciales inválidas")
```

---

### `api_endpoint.py`

API REST para obtener todos los datos de salida del proyecto con timestamp.

#### Endpoints Disponibles

**`GET /`**
- Retorna información de la API y endpoints disponibles
- **Respuesta:** JSON con mensaje, versión y lista de endpoints

**`GET /datos-salida`**
- Obtiene todos los datos de salida del proyecto con timestamp
- **Respuesta:** JSON con todos los archivos organizados por categoría (outputs, data, docs, assets)
- **Incluye:** Archivos codificados en base64, metadatos, manifest parseado

**`GET /datos-salida/resumen`**
- Obtiene resumen ligero sin contenido de archivos
- **Respuesta:** JSON con metadatos de archivos (nombre, tamaño, fecha, tipo MIME)

**`POST /datos-salida/crear-carpeta`**
- Crea carpeta "cliente 1 - petroliquidos" con timestamp y copia todos los archivos
- **Respuesta:** JSON con información de la carpeta creada y estructura

#### Ejemplo de Uso

```python
import requests

# Obtener todos los datos
response = requests.get("http://localhost:8000/datos-salida")
datos = response.json()

# Obtener resumen
response = requests.get("http://localhost:8000/datos-salida/resumen")
resumen = response.json()

# Crear carpeta organizada
response = requests.post("http://localhost:8000/datos-salida/crear-carpeta")
resultado = response.json()
print(f"Carpeta creada: {resultado['ruta_completa']}")
```

#### Documentación Completa

Ver [API_ENDPOINT_DATOS_SALIDA.md](API_ENDPOINT_DATOS_SALIDA.md) para documentación detallada.

---

*Referencia actualizada: 2024-12-19*

