# ⛽ CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL

Aplicación Streamlit para el cálculo de sistemas GNV/CNG (Gas Natural Vehicular / Compressed Natural Gas) para vehículos pesados.

## 📋 Descripción

Esta herramienta permite calcular los parámetros técnicos necesarios para la conversión de vehículos pesados a Gas Natural Vehicular, incluyendo:

- ✅ Dimensionamiento de tanques
- ✅ Cálculo de energía requerida
- ✅ Estimación de peso adicional
- ✅ Análisis de sensibilidad
- ✅ Visualización de fórmulas y procedimientos numéricos
- ✅ Gestión de datos del cliente
- ✅ Manifest del proyecto
- ✅ Sistema de autenticación con roles
- ✅ **Generador automático de diagramas P&ID (draw.io)**
- ✅ **API REST para datos de salida con timestamp**
- ✅ **Sistema de notificaciones y seguimiento** - Nuevo
  - Registro automático de envíos de clientes
  - Notificaciones por email y en la aplicación
  - Panel de administración con seguimiento de estados
  - Base de datos PostgreSQL para persistencia

## 🚀 Inicio Rápido

### Aplicación Streamlit

#### Opción 1: Script Automático (Windows)
Doble clic en: **`scripts/iniciar_app.bat`**

#### Opción 2: Manual
```bash
cd src
streamlit run calculos_combustible_vehicular.py
```

### API REST

#### Iniciar Servidor API
```bash
# Opción 1: Script batch (Windows)
scripts\iniciar_api.bat

# Opción 2: Manual
python -m uvicorn src.api_endpoint:app --reload --host 0.0.0.0 --port 8000
```

El servidor API estará disponible en:
- **http://localhost:8000** - API base
- **http://localhost:8000/docs** - Documentación interactiva (Swagger UI)
- **http://localhost:8000/redoc** - Documentación alternativa (ReDoc)

### Primera Instalación
Si es la primera vez, ejecute:
```bash
scripts\instalar_dependencias.bat
```
O manualmente:
```bash
pip install -r requirements.txt
```

### Configuración del Sistema de Notificaciones (Opcional)

El sistema incluye un módulo de notificaciones y seguimiento que requiere PostgreSQL:

1. **Instalar PostgreSQL** (si no está instalado)
   - Descargar desde: https://www.postgresql.org/download/

2. **Configurar variables de entorno:**
   ```bash
   # Copiar plantilla
   copy .env.example .env
   
   # Editar .env con sus credenciales
   # - Configuración de PostgreSQL
   # - Configuración de SMTP para emails
   ```

3. **Inicializar base de datos:**
   ```bash
   python scripts/init_database.py
   ```

4. **O usar el script de configuración:**
   ```bash
   scripts\setup_env.bat
   ```

La aplicación se abrirá automáticamente en `http://localhost:8501`

## 🔐 Credenciales por Defecto

- **Administrador:** 
  - Usuario: `admin`
  - Contraseña: `admin123`
  
- **Cliente:** 
  - Usuario: `cliente`
  - Contraseña: `cliente123`

## 📖 Estructura del Proyecto

```
proyecto/
├── src/                          # Código fuente
│   ├── calculos_combustible_vehicular.py  # Aplicación principal
│   ├── auth_system.py           # Sistema de autenticación
│   ├── config.py                 # Configuración centralizada
│   ├── database.py               # Módulo de base de datos PostgreSQL
│   ├── notifications.py          # Sistema de notificaciones
│   ├── admin_panel.py            # Panel de administración
│   └── utils/                    # Módulos utilitarios
│       ├── auth_utils.py         # Utilidades de autenticación
│       ├── manifest_utils.py     # Manejo de manifest
│       ├── calculation_engine.py # Motor de cálculos
│       └── file_handler.py       # Manejo de archivos
├── data/                         # Archivos de datos
│   ├── PETROLIQUIDOS_GNV_manifest_v1.json
│   ├── users_db.json
│   └── remembered_user.json
├── docs/                         # Documentación
├── outputs/                      # Archivos generados
├── assets/                       # Recursos estáticos
├── scripts/                      # Scripts de ejecución
│   ├── iniciar_app.bat          # Script de inicio
│   ├── iniciar_api.bat          # Script de inicio API REST
│   ├── instalar_dependencias.bat # Instalación de dependencias
│   ├── init_database.py         # Inicialización de base de datos
│   └── setup_env.bat            # Configuración de variables de entorno
├── .env.example                  # Plantilla de configuración
└── .env                          # Variables de entorno (crear desde .env.example)
└── requirements.txt             # Dependencias Python
```

## 🔔 Sistema de Notificaciones y Seguimiento

El sistema incluye un módulo completo de notificaciones y seguimiento que permite:

### Funcionalidades

- **Registro Automático**: Cuando un cliente envía sus datos, se crea automáticamente un registro en la base de datos
- **Notificaciones Duales**: 
  - Email al administrador con detalles del envío
  - Notificación en la aplicación (panel de administración)
- **Seguimiento de Estados**: 
  - Pendiente
  - En Revisión
  - Aprobado
  - Rechazado
- **Panel de Administración**: 
  - Dashboard con estadísticas
  - Lista de envíos con filtros
  - Vista detallada de cada envío (datos, cálculos, diagramas)
  - Gestión de estados y notas

### Flujo de Trabajo

1. **Cliente envía datos** → Se crea submission con estado "pendiente"
2. **Sistema envía notificaciones** → Email + notificación en app
3. **Administrador revisa** → Ve notificaciones en panel
4. **Administrador gestiona** → Cambia estado, agrega notas
5. **Seguimiento completo** → Historial de cambios y notificaciones

### Requisitos

- PostgreSQL instalado y ejecutándose
- Configuración de SMTP para emails (opcional, pero recomendado)
- Variables de entorno configuradas en `.env`

## 📚 Documentación

La documentación completa está disponible en la carpeta `docs/`:

- **[README.md](docs/README.md)** - Documentación técnica completa
- **[GUIA_USUARIO.md](docs/GUIA_USUARIO.md)** - Guía de usuario detallada
- **[PARAMETROS.md](docs/PARAMETROS.md)** - Documentación de parámetros
- **[ARQUITECTURA.md](docs/ARQUITECTURA.md)** - Arquitectura del sistema
- **[API_ENDPOINT_DATOS_SALIDA.md](docs/API_ENDPOINT_DATOS_SALIDA.md)** - Documentación API REST
- **[VERIFICACION_VINCULOS.md](docs/VERIFICACION_VINCULOS.md)** - Verificación técnica

## 🎯 Funcionalidades Principales

### 1. 🔢 Cálculos Principales
- Cálculo completo del sistema GNV/CNG
- Parámetros configurables
- Resultados detallados paso a paso
- Alertas y recomendaciones

### 2. 👤 Datos del Cliente
- Formulario de información del cliente
- Supuestos operativos y de componentes
- Exportación a JSON (solo administradores)
- Registro de auditoría con timestamps

### 3. 📐 Fórmulas y Procedimientos
- Fórmulas matemáticas completas (solo administradores)
- Procedimientos numéricos paso a paso
- Ejemplos de cálculo

### 4. 📊 Análisis de Sensibilidad
- Variación de consumo de combustible
- Variación de autonomía
- Gráficos interactivos
- Tablas comparativas

### 5. 📋 Manifest del Proyecto
- Visualización completa del manifest
- Formularios interactivos para decisiones pendientes
- Descarga de entregables (solo administradores)
- Exportación a HTML y JSON

### 6. ℹ️ Información Técnica
- Información del proyecto
- Normativas y certificaciones
- Recomendaciones y limitaciones
- Generación de informes HTML

### 7. 🌐 API REST de Datos de Salida
- Endpoint para obtener todos los datos de salida del proyecto
- Organización automática en carpeta "cliente 1 - petroliquidos" con timestamp
- Documentación interactiva (Swagger UI)
- Endpoints disponibles:
  - `GET /datos-salida` - Obtener todos los datos
  - `GET /datos-salida/resumen` - Obtener resumen ligero
  - `POST /datos-salida/crear-carpeta` - Crear carpeta organizada
- Ver [docs/API_ENDPOINT_DATOS_SALIDA.md](docs/API_ENDPOINT_DATOS_SALIDA.md) para documentación completa

## ⚙️ Parámetros Configurables

Todos los parámetros pueden ser modificados desde la interfaz:

### Parámetros de Operación
- Consumo de diésel: **35.0 L/100 km** (rango: 1.0 - 200.0)
- Autonomía deseada: **800.0 km** (rango: 100.0 - 2000.0)

### Parámetros Técnicos
- Poder calorífico diésel: **35.8 MJ/L** (rango: 30.0 - 40.0)
- LHV CH₄: **50.0 MJ/kg** (rango: 45.0 - 55.0)
- Eficiencia de conversión: **0.95** (rango: 0.80 - 1.0)

### Parámetros de Almacenamiento
- Presión de llenado: **200.0 bar** (rango: 150.0 - 300.0)
- Temperatura de operación: **25.0 °C** (rango: 0.0 - 50.0)
- Factor de compresibilidad Z: **0.85** (rango: 0.70 - 1.0)
- Volumen unitario tanque: **0.080 m³** (rango: 0.01 - 0.20)
- Peso tanque vacío: **65.0 kg** (rango: 20.0 - 150.0)
- Peso soportes: **10.0 kg** (rango: 5.0 - 30.0)
- Peso accesorios: **5.0 kg** (rango: 1.0 - 20.0)

### Constantes Físicas
- Constante universal de gases R: **8.314 J/(mol·K)**
- Masa molar CH₄: **0.01604 kg/mol**

*Ver [docs/PARAMETROS.md](docs/PARAMETROS.md) para documentación completa de parámetros*

## 📊 Resultados Calculados

La aplicación calcula y muestra:

1. **Volumen diésel equivalente** (L)
2. **Energía requerida** (MJ)
3. **Masa de CH₄ requerida** (kg)
4. **Volumen de gas a presión de llenado** (m³)
5. **Número de tanques requeridos** (unidades)
6. **Peso adicional total** (kg)

Incluye alertas y recomendaciones cuando los valores calculados pueden ser problemáticos.

## 🔧 Requisitos del Sistema

- **Python:** 3.8 o superior
- **Streamlit:** 1.28.0 o superior
- **Pandas:** 2.0.0 o superior
- **Sistema Operativo:** Windows, Linux, macOS

## 🛠️ Desarrollo

### Estructura Modular
La aplicación está organizada en módulos:

- `auth_system.py` - Autenticación y gestión de usuarios
- `config.py` - Configuración centralizada
- `utils/` - Módulos utilitarios reutilizables
- `calculos_combustible_vehicular.py` - Aplicación principal Streamlit

### Extensibilidad
- Fácil agregar nuevos módulos en `utils/`
- Configuración centralizada en `config.py`
- Motor de cálculos reutilizable

## 📝 Notas Importantes

- Los valores por defecto están basados en el informe técnico PETROLIQUIDOS_GNV_Informe_v1
- Todos los valores deben validarse con datos reales del vehículo
- La aplicación asume CH₄ puro; en realidad el GNV contiene ~90-95% CH₄
- El factor de compresibilidad Z puede variar según la composición del gas
- Los archivos de datos se guardan en `data/`
- Los entregables deben estar en la raíz del proyecto

## 🔒 Seguridad

- Contraseñas almacenadas con hash SHA-256
- Sistema de roles (Administrador/Cliente)
- Acceso restringido a funciones administrativas
- Datos de auditoría con timestamps

## 📄 Licencia

Confidencial - Uso exclusivo del cliente PETROLIQUIDOS

## 👥 Soporte

Para consultas técnicas o actualizaciones, contactar al equipo de ingeniería.

---

**Versión:** 1.0  
**Fecha:** 2024-12-19  
**Cliente:** PETROLIQUIDOS  
**Última actualización:** 2024-12-19

