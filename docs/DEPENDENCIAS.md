# 📦 Dependencias del Proyecto - Aplicación GNV

## Resumen

Este documento lista todas las dependencias del proyecto y su propósito.

## Dependencias Externas

Estas dependencias deben instalarse mediante `pip install -r requirements.txt`:

### 1. streamlit >= 1.28.0
**Propósito:** Framework web para crear la interfaz de usuario de la aplicación.

**Uso en el proyecto:**
- Interfaz principal de la aplicación (`calculos_combustible_vehicular.py`)
- Componentes UI (botones, formularios, gráficos)
- Gestión de sesión y estado
- Integración con draw.io (`drawio_integration.py`)

**Documentación:** https://docs.streamlit.io/

### 2. pandas >= 2.0.0
**Propósito:** Manipulación y análisis de datos estructurados.

**Uso en el proyecto:**
- Manejo de datos tabulares en la aplicación
- Procesamiento de resultados de cálculos
- Visualización de datos en tablas

**Documentación:** https://pandas.pydata.org/

### 3. openpyxl >= 3.0.0
**Propósito:** Lectura y escritura de archivos Excel (.xlsx).

**Uso en el proyecto:**
- Soporte para archivos Excel en pandas
- Referencias a archivos BOM (Bill of Materials) en formato Excel
- Compatibilidad con entregables en formato .xlsx

**Documentación:** https://openpyxl.readthedocs.io/

## Bibliotecas Estándar de Python

Estas bibliotecas vienen incluidas con Python y **NO** necesitan instalación:

### Módulos Utilizados

1. **math** - Funciones matemáticas
   - Uso: Cálculos del sistema GNV (`calculation_engine.py`)

2. **json** - Manejo de archivos JSON
   - Uso: 
     - Base de datos de usuarios (`users_db.json`)
     - Manifest del proyecto (`manifest_v1.json`)
     - Datos del cliente (`datos_cliente_*.json`)

3. **base64** - Codificación Base64
   - Uso: Generación de enlaces de descarga para archivos

4. **os** - Operaciones del sistema operativo
   - Uso: Manejo de rutas de archivos, verificación de existencia

5. **sys** - Funciones del sistema
   - Uso: Gestión de paths para imports

6. **datetime** - Manejo de fechas y tiempos
   - Uso: Timestamps, fechas de creación/modificación

7. **xml.etree.ElementTree** - Procesamiento XML
   - Uso: Generación de diagramas draw.io (`drawio_agent.py`)

8. **xml.dom.minidom** - Procesamiento XML (DOM)
   - Uso: Formateo de XML para draw.io (`drawio_agent.py`)

9. **typing** - Anotaciones de tipo
   - Uso: Type hints en funciones (`drawio_agent.py`)

10. **hashlib** - Funciones hash
    - Uso: Hash SHA-256 para contraseñas (`auth_system.py`)

## Dependencias Indirectas

Estas dependencias se instalan automáticamente como dependencias de las librerías principales:

- **numpy** - Instalado automáticamente con pandas
- **altair** - Instalado automáticamente con streamlit (para gráficos)
- **toml** - Instalado automáticamente con streamlit
- **pyarrow** - Instalado automáticamente con pandas (opcional, para mejor rendimiento)

## Instalación

### Opción 1: Script Automático (Windows)
```bash
instalar_dependencias.bat
```

### Opción 2: Manual
```bash
pip install -r requirements.txt
```

### Opción 3: Con entorno virtual (Recomendado)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# o
source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

## Verificación de Instalación

Para verificar que todas las dependencias están instaladas:

```bash
python verificar_dependencias.py
```

O manualmente:
```bash
python -c "import streamlit; import pandas; import openpyxl; print('OK')"
```

## Versiones Mínimas

Las versiones mínimas especificadas en `requirements.txt` son:

- **streamlit >= 1.28.0**: Versión mínima que soporta todas las características usadas
- **pandas >= 2.0.0**: Versión 2.x con mejoras de rendimiento y nuevas características
- **openpyxl >= 3.0.0**: Versión estable con soporte completo para Excel moderno

## Actualización de Dependencias

Para actualizar todas las dependencias a sus últimas versiones compatibles:

```bash
pip install --upgrade streamlit pandas openpyxl
```

Luego actualizar `requirements.txt` con las versiones instaladas:

```bash
pip freeze > requirements.txt
```

**Nota:** Se recomienda probar la aplicación después de actualizar dependencias.

## Solución de Problemas

### Error: "No module named 'streamlit'"
```bash
pip install streamlit
```

### Error: "No module named 'pandas'"
```bash
pip install pandas
```

### Error: "No module named 'openpyxl'"
```bash
pip install openpyxl
```

### Error al leer archivos Excel
Asegúrese de tener `openpyxl` instalado:
```bash
pip install openpyxl
```

## Compatibilidad

- **Python:** 3.8 o superior
- **Sistema Operativo:** Windows, Linux, macOS
- **Streamlit:** Compatible con versiones 1.28.0 y superiores

---

*Última actualización: 2024-12-19*

