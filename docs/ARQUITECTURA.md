# 🏗️ Arquitectura del Sistema - Aplicación GNV

## Visión General

La aplicación está diseñada con una arquitectura modular que separa responsabilidades y facilita el mantenimiento.

## Estructura del Proyecto

```
proyecto/
├── src/                              # Código fuente
│   ├── calculos_combustible_vehicular.py  # Aplicación principal (2012 líneas)
│   ├── api_endpoint.py                    # API REST de datos de salida
│   ├── auth_system.py                # Sistema de autenticación
│   ├── config.py                     # Configuración centralizada
│   └── utils/                        # Módulos utilitarios
│       ├── __init__.py
│       ├── auth_utils.py             # Utilidades de autenticación
│       ├── manifest_utils.py         # Manejo de manifest
│       ├── calculation_engine.py     # Motor de cálculos
│       ├── file_handler.py           # Manejo de archivos
│       ├── drawio_agent.py           # Agente generador de diagramas P&ID
│       └── drawio_integration.py     # Integración draw.io con Streamlit
├── data/                             # Archivos de datos
│   ├── PETROLIQUIDOS_GNV_manifest_v1.json
│   ├── users_db.json
│   ├── remembered_user.json
│   └── datos_cliente_*.json
├── docs/                             # Documentación
│   ├── README.md
│   ├── GUIA_USUARIO.md
│   ├── PARAMETROS.md
│   ├── ARQUITECTURA.md
│   └── VERIFICACION_VINCULOS.md
├── scripts/                          # Scripts de ejecución
│   ├── iniciar_app.bat               # Script de inicio
│   └── instalar_dependencias.bat     # Instalación
├── outputs/                          # Archivos generados
├── assets/                           # Recursos estáticos
├── requirements.txt                   # Dependencias
└── README.md                          # Documentación principal
```

## Arquitectura Modular

### Capa de Presentación
**Archivo:** `calculos_combustible_vehicular.py`

**Responsabilidades:**
- Interfaz de usuario Streamlit
- Gestión de sesión
- Navegación entre pestañas
- Renderizado de resultados

**Componentes:**
- Sistema de autenticación (UI)
- 6 pestañas principales
- Formularios interactivos
- Visualización de datos

### Capa de Lógica de Negocio

#### Módulo de Autenticación
**Archivo:** `auth_system.py`

**Funciones:**
- `hash_password()` - Hash SHA-256
- `verify_user()` - Verificación de credenciales
- `create_user()` - Creación de usuarios
- `get_user_role()` - Obtención de rol
- `init_default_users()` - Inicialización

**Almacenamiento:**
- `data/users_db.json` - Base de datos de usuarios

#### Motor de Cálculos
**Archivo:** `utils/calculation_engine.py`

**Funciones:**
- `calcular_sistema_gnv()` - Cálculo completo del sistema
- `calcular_sensibilidad()` - Análisis de sensibilidad

**Entradas:**
- Parámetros de operación
- Parámetros técnicos
- Parámetros de almacenamiento
- Constantes físicas

**Salidas:**
- Diccionario con todos los resultados calculados

#### Manejo de Manifest
**Archivo:** `utils/manifest_utils.py`

**Funciones:**
- `load_manifest()` - Carga desde JSON
- `save_manifest()` - Guarda en JSON
- `generate_manifest_html()` - Genera HTML formateado

**Almacenamiento:**
- `data/PETROLIQUIDOS_GNV_manifest_v1.json`

### Capa de Utilidades

#### Utilidades de Autenticación
**Archivo:** `utils/auth_utils.py`

**Funciones:**
- `load_remembered_user()` - Carga usuario recordado
- `save_remembered_user()` - Guarda usuario
- `clear_remembered_user()` - Elimina usuario guardado

**Almacenamiento:**
- `data/remembered_user.json`

#### API REST de Datos de Salida
**Archivo:** `src/api_endpoint.py`

**Framework:** FastAPI con uvicorn

**Responsabilidades:**
- Servidor API REST para obtener datos de salida del proyecto
- Recopilación de archivos de todas las carpetas (outputs, data, docs, assets)
- Organización automática en carpeta "cliente 1 - petroliquidos" con timestamp
- Codificación de archivos en base64 para transferencia
- Generación de metadatos y estructura de carpetas

**Endpoints:**
- `GET /` - Información de la API
- `GET /datos-salida` - Obtiene todos los datos con timestamp
- `GET /datos-salida/resumen` - Resumen ligero sin contenido
- `POST /datos-salida/crear-carpeta` - Crea carpeta organizada

**Funciones Principales:**
- `recopilar_datos_salida()` - Recopila todos los archivos del proyecto
- `crear_estructura_carpeta_cliente()` - Crea carpeta organizada
- `leer_archivo_como_base64()` - Codifica archivos para transferencia
- `leer_archivo_json()` - Lee y parsea archivos JSON

**Documentación:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### Manejo de Archivos
**Archivo:** `utils/file_handler.py`

**Funciones:**
- `get_file_mime_type()` - Obtiene MIME type
- `create_download_link()` - Crea enlace de descarga
- `file_exists()` - Verifica existencia

#### Agente Generador de Diagramas P&ID
**Archivo:** `utils/drawio_agent.py`

**Clase Principal:** `DrawIOAgent`

**Responsabilidades:**
- Generación automática de diagramas draw.io (XML)
- Carga de variables desde resultados de cálculo
- Creación de componentes del sistema (tanques, reguladores, válvulas, sensores, ECU, etc.)
- Generación de conexiones entre componentes
- Exportación a formato draw.io compatible

**Funciones Principales:**
- `load_calculation_variables()` - Carga variables de cálculo
- `load_engineering_instructions()` - Lee instrucciones de ingeniería
- `create_component()` - Crea un componente del diagrama
- `create_connection()` - Crea conexiones entre componentes
- `generate_diagram_from_engineering()` - Genera diagrama completo
- `save_diagram()` - Guarda el diagrama en archivo XML

**Componentes Generados:**
- Tanques CNG (con número y capacidad dinámicos)
- Manifold de distribución
- Válvulas (shut-off, alivio, llenado)
- Reguladores (1ra y 2da etapa con rangos de presión)
- Filtro de gas
- ECU (Engine Control Unit)
- Sensores (presión, temperatura, lambda)
- Inyectores de gas
- Motor diésel convertido

**Almacenamiento:**
- `PETROLIQUIDOS_GNV_PID_v1.drawio.xml` - Diagrama generado

#### Integración Draw.io con Streamlit
**Archivo:** `utils/drawio_integration.py`

**Funciones:**
- `show_diagram_generator()` - Interfaz Streamlit para generación de diagramas

**Características:**
- Botones para generar, ver variables y descargar diagrama
- Visualización de variables del diagrama
- Integración con resultados de cálculo
- Descarga del diagrama en formato .drawio.xml

### Capa de Configuración
**Archivo:** `config.py`

**Contenido:**
- Parámetros por defecto
- Rutas de archivos
- Constantes físicas
- Configuración de la aplicación

## Flujo de Datos

### Flujo de Autenticación
```
Usuario → Login UI → auth_system.verify_user() → users_db.json
                ↓
         Session State (authenticated, username, user_role)
```

### Flujo de Cálculo
```
Parámetros UI → calcular_sistema_gnv() → Resultados → Session State
                                              ↓
                                    Visualización en UI
```

### Flujo de Datos del Cliente
```
Formulario → Session State → Guardar → cliente_data
                                      ↓
                              Exportar JSON (Admin)
```

### Flujo de Manifest
```
load_manifest() → data/manifest.json → Visualización
                    ↓
            generate_manifest_html() → Exportar HTML
```

### Flujo de Generación de Diagrama P&ID
```
Resultados Cálculo → DrawIOAgent.load_calculation_variables()
                        ↓
            DrawIOAgent.generate_diagram_from_engineering()
                        ↓
            Creación de componentes y conexiones
                        ↓
            Generación XML draw.io
                        ↓
            Guardado en PETROLIQUIDOS_GNV_PID_v1.drawio.xml
                        ↓
            Visualización y descarga en Streamlit
```

## Sistema de Roles

### Administrador
**Permisos:**
- ✅ Editar información del proyecto
- ✅ Ver fórmulas y procedimientos
- ✅ Exportar datos del cliente
- ✅ Descargar entregables
- ✅ Exportar manifest completo
- ✅ Ver todas las respuestas

### Cliente
**Permisos:**
- ✅ Realizar cálculos
- ✅ Ver resultados
- ✅ Completar datos del cliente
- ✅ Ver análisis de sensibilidad
- ✅ Ver manifest del proyecto
- ✅ Responder decisiones pendientes
- ❌ NO puede ver fórmulas
- ❌ NO puede exportar datos
- ❌ NO puede descargar entregables

## Gestión de Estado

### Session State (Streamlit)
**Variables principales:**
- `authenticated` - Estado de autenticación
- `username` - Usuario actual
- `user_role` - Rol del usuario
- `proyecto_cliente` - Cliente del proyecto
- `proyecto_version` - Versión del proyecto
- `proyecto_fecha` - Fecha del proyecto
- `cliente_data` - Datos del cliente
- `calculo_resultado` - Resultados del cálculo
- `decisiones_respuestas` - Respuestas a decisiones
- `diagram_xml` - Contenido XML del diagrama generado
- `diagram_generated` - Flag de diagrama generado

## Persistencia de Datos

### Archivos JSON
- `data/users_db.json` - Usuarios y contraseñas (hash)
- `data/remembered_user.json` - Usuario recordado
- `data/PETROLIQUIDOS_GNV_manifest_v1.json` - Manifest del proyecto
- `data/datos_cliente_*.json` - Exportaciones de datos del cliente

### Archivos de Entregables
- `docs/PETROLIQUIDOS_GNV_Informe_v1.md` - Informe en Markdown
- `outputs/PETROLIQUIDOS_GNV_BOM_v1.xlsx` - Bill of Materials
- `assets/PETROLIQUIDOS_GNV_PID_v1.drawio.xml` - Diagrama P&ID

## Comunicación entre Módulos

### Imports
```python
# Archivo principal
from auth_system import verify_user, create_user, get_user_role
from utils.auth_utils import load_remembered_user, save_remembered_user
from utils.manifest_utils import load_manifest, save_manifest
from utils.calculation_engine import calcular_sistema_gnv
from utils.file_handler import create_download_link, file_exists
from config import MANIFEST_FILE, DEFAULT_CLIENT, ...
```

### Rutas Centralizadas
Todas las rutas están en `config.py`:
- `MANIFEST_FILE` → `data/PETROLIQUIDOS_GNV_manifest_v1.json`
- `USERS_DB_FILE` → `data/users_db.json`
- `REMEMBERED_USER_FILE` → `data/remembered_user.json`

## Seguridad

### Autenticación
- Hash SHA-256 para contraseñas
- Verificación de credenciales
- Gestión de sesión

### Autorización
- Sistema de roles
- Verificación de permisos en cada función
- Acceso condicional a funciones

### Validación
- Validación de entrada de datos
- Verificación de tipos
- Manejo de errores

## Optimizaciones Implementadas

### Eliminación de Duplicación
- ✅ Funciones movidas a módulos utils
- ✅ Motor de cálculos centralizado
- ✅ Rutas centralizadas en config

### Rendimiento
- ✅ Carga lazy de módulos
- ✅ Validación de datos antes de cálculos
- ✅ Manejo eficiente de archivos

### Mantenibilidad
- ✅ Código modular
- ✅ Separación de responsabilidades
- ✅ Documentación completa

## Extensibilidad

### Agregar Nuevas Funcionalidades
1. Crear nuevo módulo en `utils/`
2. Agregar función en el módulo
3. Importar en `calculos_combustible_vehicular.py`
4. Agregar UI en la pestaña correspondiente

### Modificar Parámetros
1. Editar `config.py`
2. Los cambios se reflejan automáticamente

### Agregar Nuevos Roles
1. Modificar `auth_system.py`
2. Agregar verificaciones de permisos
3. Actualizar UI condicional

## Dependencias

### Principales
- **streamlit** >= 1.28.0 - Framework web
- **pandas** >= 2.0.0 - Manipulación de datos

### Estándar de Python
- `json` - Manejo de JSON
- `os` - Operaciones del sistema
- `base64` - Codificación
- `datetime` - Fechas y tiempos
- `hashlib` - Hash de contraseñas
- `math` - Funciones matemáticas
- `sys` - Funciones del sistema

## Patrones de Diseño Utilizados

1. **Módulo Singleton:** `config.py` - Configuración única
2. **Factory Pattern:** Funciones de creación en utils
3. **Strategy Pattern:** Diferentes estrategias según rol
4. **Observer Pattern:** Session State observa cambios

## API REST

### Servidor FastAPI
- **Archivo:** `src/api_endpoint.py`
- **Framework:** FastAPI con uvicorn
- **Puerto:** 8000 (por defecto)

### Endpoints Disponibles

1. **GET /** - Información de la API
2. **GET /datos-salida** - Obtiene todos los datos de salida con timestamp
3. **GET /datos-salida/resumen** - Resumen ligero sin contenido de archivos
4. **POST /datos-salida/crear-carpeta** - Crea carpeta "cliente 1 - petroliquidos" organizada

### Características
- Recopila archivos de `outputs/`, `data/`, `docs/`, `assets/`
- Organiza datos por categorías
- Codifica archivos en base64 para transferencia
- Genera metadatos con timestamp
- Crea estructura de carpetas organizada
- Documentación interactiva (Swagger UI y ReDoc)

### Documentación
Ver [API_ENDPOINT_DATOS_SALIDA.md](API_ENDPOINT_DATOS_SALIDA.md) para documentación completa.

## Próximas Mejoras Sugeridas

1. **Base de Datos:** Migrar de JSON a SQLite o PostgreSQL
2. **Caché:** Implementar caché para cálculos repetidos
3. **Tests:** Agregar tests unitarios
4. **Logging:** Sistema de logging estructurado
5. **Autenticación API:** Agregar autenticación a endpoints REST

---

*Documentación actualizada: 2024-12-19*

