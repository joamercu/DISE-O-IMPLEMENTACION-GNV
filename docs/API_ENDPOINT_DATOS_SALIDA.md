# API Endpoint - Datos de Salida del Proyecto

## Descripción

Este endpoint API permite obtener todos los datos de salida del proyecto organizados en una carpeta con timestamp enfocada en "cliente 1 - petroliquidos".

## Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Iniciar el servidor API:
```bash
# Opción 1: Usando el script batch (Windows)
scripts\iniciar_api.bat

# Opción 2: Usando uvicorn directamente
python -m uvicorn src.api_endpoint:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints Disponibles

### 1. GET `/`
Endpoint raíz con información de la API.

**Respuesta:**
```json
{
  "mensaje": "API de Datos de Salida - Proyecto GNV",
  "version": "1.0.0",
  "endpoints": {
    "/datos-salida": "GET - Obtiene todos los datos de salida del proyecto con timestamp",
    "/datos-salida/crear-carpeta": "POST - Crea la carpeta 'cliente 1 - petroliquidos' con los archivos"
  }
}
```

### 2. GET `/datos-salida`
Obtiene todos los datos de salida del proyecto con timestamp.

**Respuesta:**
```json
{
  "timestamp": "2024-12-19T10:30:45.123456",
  "cliente": "PETROLIQUIDOS",
  "carpeta_destino": "cliente 1 - petroliquidos_20241219_103045",
  "archivos_procesados": 25,
  "datos": {
    "metadata": {
      "timestamp": "2024-12-19T10:30:45.123456",
      "timestamp_formateado": "20241219_103045",
      "cliente": "PETROLIQUIDOS",
      "carpeta_destino": "cliente 1 - petroliquidos_20241219_103045",
      "ruta_carpeta_destino": "D:\\...\\cliente 1 - petroliquidos_20241219_103045"
    },
    "outputs": {
      "directorio": ".../outputs",
      "archivos": [...],
      "total": 10
    },
    "data": {
      "directorio": ".../data",
      "archivos": [...],
      "total": 7
    },
    "docs": {
      "directorio": ".../docs",
      "archivos": [...],
      "total": 6
    },
    "assets": {
      "directorio": ".../assets",
      "archivos": [...],
      "total": 2
    },
    "manifest": {
      "ruta": ".../PETROLIQUIDOS_GNV_manifest_v1.json",
      "contenido": {...}
    },
    "resumen": {
      "total_archivos": 25,
      "archivos_por_categoria": {
        "outputs": 10,
        "data": 7,
        "docs": 6,
        "assets": 2
      }
    }
  }
}
```

**Nota:** Los archivos se incluyen codificados en base64 en el campo `contenido_base64` de cada archivo.

### 3. GET `/datos-salida/resumen`
Obtiene un resumen de los datos de salida sin incluir el contenido de los archivos (más ligero).

**Respuesta:**
```json
{
  "timestamp": "2024-12-19T10:30:45.123456",
  "cliente": "PETROLIQUIDOS",
  "carpeta_destino": "cliente 1 - petroliquidos_20241219_103045",
  "resumen": {
    "total_archivos": 25,
    "archivos_por_categoria": {
      "outputs": 10,
      "data": 7,
      "docs": 6,
      "assets": 2
    }
  },
  "archivos": {
    "outputs": [
      {
        "nombre": "PETROLIQUIDOS_GNV_BOM_v1.xlsx",
        "tamaño_bytes": 45678,
        "fecha_modificacion": "2024-12-19T08:15:30",
        "tipo_mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      },
      ...
    ],
    ...
  }
}
```

### 4. POST `/datos-salida/crear-carpeta`
Crea la carpeta "cliente 1 - petroliquidos" con timestamp y copia todos los archivos organizados.

**Respuesta:**
```json
{
  "mensaje": "Carpeta creada exitosamente",
  "carpeta": "cliente 1 - petroliquidos_20241219_103045",
  "ruta_completa": "D:\\...\\cliente 1 - petroliquidos_20241219_103045",
  "timestamp": "2024-12-19T10:30:45.123456",
  "archivos_copiados": 25,
  "estructura": {
    "outputs": 10,
    "data": 7,
    "docs": 6,
    "assets": 2
  }
}
```

**Estructura de carpetas creada:**
```
cliente 1 - petroliquidos_20241219_103045/
├── outputs/
│   ├── PETROLIQUIDOS_GNV_BOM_v1.xlsx
│   ├── informe_gnv_*.html
│   └── ...
├── data/
│   ├── PETROLIQUIDOS_GNV_manifest_v1.json
│   ├── datos_cliente_*.json
│   └── ...
├── docs/
│   ├── PETROLIQUIDOS_GNV_Informe_v1.md
│   ├── README.md
│   └── ...
├── assets/
│   └── PETROLIQUIDOS_GNV_PID_v1.drawio.xml
└── metadata.json
```

## Uso con cURL

### Obtener todos los datos:
```bash
curl http://localhost:8000/datos-salida
```

### Obtener resumen:
```bash
curl http://localhost:8000/datos-salida/resumen
```

### Crear carpeta:
```bash
curl -X POST http://localhost:8000/datos-salida/crear-carpeta
```

## Uso con Python

```python
import requests

# Obtener todos los datos
response = requests.get("http://localhost:8000/datos-salida")
datos = response.json()

# Obtener resumen
response = requests.get("http://localhost:8000/datos-salida/resumen")
resumen = response.json()

# Crear carpeta
response = requests.post("http://localhost:8000/datos-salida/crear-carpeta")
resultado = response.json()
print(f"Carpeta creada: {resultado['ruta_completa']}")
```

## Documentación Interactiva

Una vez iniciado el servidor, puedes acceder a la documentación interactiva de Swagger UI en:
- http://localhost:8000/docs

O la documentación alternativa en ReDoc:
- http://localhost:8000/redoc

## Características

- ✅ Recopila todos los archivos de salida del proyecto
- ✅ Incluye timestamp en formato ISO y formateado
- ✅ Organiza datos por categorías (outputs, data, docs, assets)
- ✅ Codifica archivos en base64 para transferencia
- ✅ Incluye metadatos de cada archivo (tamaño, fecha, tipo MIME)
- ✅ Crea estructura de carpetas organizada
- ✅ Genera archivo de metadatos en la carpeta destino
- ✅ Soporta archivos JSON, Excel, HTML, Markdown, XML, PDF

## Notas

- Los archivos JSON en la carpeta `data/` se incluyen tanto en base64 como parseados en el campo `contenido_parseado`
- La carpeta `outputs/archivos_antiguos/` se excluye automáticamente
- Solo se incluyen archivos de documentación principales en la carpeta `docs/`
- El timestamp se genera al momento de la solicitud

