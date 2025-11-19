"""
API Endpoint para obtener todos los datos de salida del proyecto
Organizados en carpeta "cliente 1 - petroliquidos" con timestamp
"""

import os
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import shutil

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Importar configuración
import sys
import os
# Asegurar que src esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    BASE_DIR, DATA_DIR, OUTPUTS_DIR, DOCS_DIR, ASSETS_DIR,
    MANIFEST_FILE, DELIVERABLE_MD, DELIVERABLE_XLSX, DELIVERABLE_XML
)

app = FastAPI(
    title="API Datos de Salida - Proyecto GNV",
    description="Endpoint para obtener todos los datos de salida del proyecto con timestamp",
    version="1.0.0"
)


class OutputDataResponse(BaseModel):
    """Modelo de respuesta para los datos de salida"""
    timestamp: str
    cliente: str
    carpeta_destino: str
    archivos_procesados: int
    datos: Dict[str, Any]


def leer_archivo_como_base64(ruta_archivo: str) -> Dict[str, Any]:
    """
    Lee un archivo y lo convierte a base64
    
    Args:
        ruta_archivo: Ruta al archivo
        
    Returns:
        Dict con contenido en base64 y metadatos
    """
    try:
        if not os.path.exists(ruta_archivo):
            return None
        
        with open(ruta_archivo, 'rb') as f:
            contenido = f.read()
            contenido_base64 = base64.b64encode(contenido).decode('utf-8')
        
        # Obtener información del archivo
        stat_info = os.stat(ruta_archivo)
        nombre_archivo = os.path.basename(ruta_archivo)
        extension = os.path.splitext(nombre_archivo)[1].lower()
        
        # Determinar tipo MIME
        tipos_mime = {
            '.json': 'application/json',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.html': 'text/html',
            '.md': 'text/markdown',
            '.xml': 'application/xml',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain'
        }
        mime_type = tipos_mime.get(extension, 'application/octet-stream')
        
        return {
            'nombre': nombre_archivo,
            'ruta_original': ruta_archivo,
            'tamaño_bytes': stat_info.st_size,
            'fecha_modificacion': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            'tipo_mime': mime_type,
            'extension': extension,
            'contenido_base64': contenido_base64
        }
    except Exception as e:
        return {
            'error': f"Error al leer archivo: {str(e)}",
            'ruta': ruta_archivo
        }


def leer_archivo_json(ruta_archivo: str) -> Dict[str, Any]:
    """
    Lee un archivo JSON y retorna su contenido parseado
    
    Args:
        ruta_archivo: Ruta al archivo JSON
        
    Returns:
        Contenido del JSON parseado o None si hay error
    """
    try:
        if not os.path.exists(ruta_archivo):
            return None
        
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {'error': f"Error al leer JSON: {str(e)}"}


def recopilar_datos_salida() -> Dict[str, Any]:
    """
    Recopila todos los datos de salida del proyecto
    
    Returns:
        Dict con todos los datos organizados por categoría
    """
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    timestamp_iso = timestamp.isoformat()
    
    # Crear nombre de carpeta destino
    carpeta_destino = f"cliente 1 - petroliquidos_{timestamp_str}"
    ruta_carpeta_destino = os.path.join(BASE_DIR, carpeta_destino)
    
    datos_salida = {
        'metadata': {
            'timestamp': timestamp_iso,
            'timestamp_formateado': timestamp_str,
            'cliente': 'PETROLIQUIDOS',
            'carpeta_destino': carpeta_destino,
            'ruta_carpeta_destino': ruta_carpeta_destino
        },
        'outputs': {},
        'data': {},
        'docs': {},
        'assets': {},
        'manifest': None,
        'resumen': {
            'total_archivos': 0,
            'archivos_por_categoria': {}
        }
    }
    
    # 1. Recopilar archivos de OUTPUTS
    if os.path.exists(OUTPUTS_DIR):
        archivos_outputs = []
        for root, dirs, files in os.walk(OUTPUTS_DIR):
            # Excluir carpeta archivos_antiguos si existe
            if 'archivos_antiguos' in dirs:
                dirs.remove('archivos_antiguos')
            
            for archivo in files:
                ruta_completa = os.path.join(root, archivo)
                archivo_data = leer_archivo_como_base64(ruta_completa)
                if archivo_data:
                    archivos_outputs.append(archivo_data)
        
        datos_salida['outputs'] = {
            'directorio': OUTPUTS_DIR,
            'archivos': archivos_outputs,
            'total': len(archivos_outputs)
        }
        datos_salida['resumen']['archivos_por_categoria']['outputs'] = len(archivos_outputs)
        datos_salida['resumen']['total_archivos'] += len(archivos_outputs)
    
    # 2. Recopilar archivos de DATA (JSON)
    if os.path.exists(DATA_DIR):
        archivos_data = []
        for archivo in os.listdir(DATA_DIR):
            ruta_completa = os.path.join(DATA_DIR, archivo)
            if os.path.isfile(ruta_completa):
                # Para JSON, leer también el contenido parseado
                if archivo.endswith('.json'):
                    contenido_json = leer_archivo_json(ruta_completa)
                    archivo_data = leer_archivo_como_base64(ruta_completa)
                    if archivo_data:
                        archivo_data['contenido_parseado'] = contenido_json
                        archivos_data.append(archivo_data)
                else:
                    archivo_data = leer_archivo_como_base64(ruta_completa)
                    if archivo_data:
                        archivos_data.append(archivo_data)
        
        datos_salida['data'] = {
            'directorio': DATA_DIR,
            'archivos': archivos_data,
            'total': len(archivos_data)
        }
        datos_salida['resumen']['archivos_por_categoria']['data'] = len(archivos_data)
        datos_salida['resumen']['total_archivos'] += len(archivos_data)
    
    # 3. Recopilar archivos de DOCS (documentación)
    if os.path.exists(DOCS_DIR):
        archivos_docs = []
        # Solo incluir archivos principales, no todos los PDFs
        archivos_importantes = [
            'PETROLIQUIDOS_GNV_Informe_v1.md',
            'README.md',
            'GUIA_USUARIO.md',
            'ARQUITECTURA.md',
            'API_REFERENCE.md',
            'RESUMEN_PROYECTO.md'
        ]
        
        for archivo in archivos_importantes:
            ruta_completa = os.path.join(DOCS_DIR, archivo)
            if os.path.exists(ruta_completa):
                archivo_data = leer_archivo_como_base64(ruta_completa)
                if archivo_data:
                    archivos_docs.append(archivo_data)
        
        datos_salida['docs'] = {
            'directorio': DOCS_DIR,
            'archivos': archivos_docs,
            'total': len(archivos_docs)
        }
        datos_salida['resumen']['archivos_por_categoria']['docs'] = len(archivos_docs)
        datos_salida['resumen']['total_archivos'] += len(archivos_docs)
    
    # 4. Recopilar archivos de ASSETS
    if os.path.exists(ASSETS_DIR):
        archivos_assets = []
        for archivo in os.listdir(ASSETS_DIR):
            ruta_completa = os.path.join(ASSETS_DIR, archivo)
            if os.path.isfile(ruta_completa):
                archivo_data = leer_archivo_como_base64(ruta_completa)
                if archivo_data:
                    archivos_assets.append(archivo_data)
        
        datos_salida['assets'] = {
            'directorio': ASSETS_DIR,
            'archivos': archivos_assets,
            'total': len(archivos_assets)
        }
        datos_salida['resumen']['archivos_por_categoria']['assets'] = len(archivos_assets)
        datos_salida['resumen']['total_archivos'] += len(archivos_assets)
    
    # 5. Cargar manifest principal
    if os.path.exists(MANIFEST_FILE):
        manifest_data = leer_archivo_json(MANIFEST_FILE)
        datos_salida['manifest'] = {
            'ruta': MANIFEST_FILE,
            'contenido': manifest_data
        }
    
    return datos_salida


def crear_estructura_carpeta_cliente(datos_salida: Dict[str, Any]) -> str:
    """
    Crea la estructura de carpetas "cliente 1 - petroliquidos" y copia los archivos
    
    Args:
        datos_salida: Diccionario con todos los datos de salida
        
    Returns:
        Ruta de la carpeta creada
    """
    carpeta_destino = datos_salida['metadata']['carpeta_destino']
    ruta_carpeta_destino = datos_salida['metadata']['ruta_carpeta_destino']
    
    # Crear estructura de carpetas
    subcarpetas = {
        'outputs': os.path.join(ruta_carpeta_destino, 'outputs'),
        'data': os.path.join(ruta_carpeta_destino, 'data'),
        'docs': os.path.join(ruta_carpeta_destino, 'docs'),
        'assets': os.path.join(ruta_carpeta_destino, 'assets')
    }
    
    # Crear carpeta principal y subcarpetas
    os.makedirs(ruta_carpeta_destino, exist_ok=True)
    for subcarpeta in subcarpetas.values():
        os.makedirs(subcarpeta, exist_ok=True)
    
    # Copiar archivos de outputs
    if os.path.exists(OUTPUTS_DIR):
        for archivo_info in datos_salida['outputs'].get('archivos', []):
            ruta_original = archivo_info.get('ruta_original')
            if ruta_original and os.path.exists(ruta_original):
                nombre_archivo = archivo_info['nombre']
                ruta_destino = os.path.join(subcarpetas['outputs'], nombre_archivo)
                try:
                    shutil.copy2(ruta_original, ruta_destino)
                except Exception as e:
                    print(f"Error al copiar {ruta_original}: {e}")
    
    # Copiar archivos de data
    if os.path.exists(DATA_DIR):
        for archivo_info in datos_salida['data'].get('archivos', []):
            ruta_original = archivo_info.get('ruta_original')
            if ruta_original and os.path.exists(ruta_original):
                nombre_archivo = archivo_info['nombre']
                ruta_destino = os.path.join(subcarpetas['data'], nombre_archivo)
                try:
                    shutil.copy2(ruta_original, ruta_destino)
                except Exception as e:
                    print(f"Error al copiar {ruta_original}: {e}")
    
    # Copiar archivos de docs
    if os.path.exists(DOCS_DIR):
        for archivo_info in datos_salida['docs'].get('archivos', []):
            ruta_original = archivo_info.get('ruta_original')
            if ruta_original and os.path.exists(ruta_original):
                nombre_archivo = archivo_info['nombre']
                ruta_destino = os.path.join(subcarpetas['docs'], nombre_archivo)
                try:
                    shutil.copy2(ruta_original, ruta_destino)
                except Exception as e:
                    print(f"Error al copiar {ruta_original}: {e}")
    
    # Copiar archivos de assets
    if os.path.exists(ASSETS_DIR):
        for archivo_info in datos_salida['assets'].get('archivos', []):
            ruta_original = archivo_info.get('ruta_original')
            if ruta_original and os.path.exists(ruta_original):
                nombre_archivo = archivo_info['nombre']
                ruta_destino = os.path.join(subcarpetas['assets'], nombre_archivo)
                try:
                    shutil.copy2(ruta_original, ruta_destino)
                except Exception as e:
                    print(f"Error al copiar {ruta_original}: {e}")
    
    # Crear archivo de metadatos en la carpeta
    metadata_file = os.path.join(ruta_carpeta_destino, 'metadata.json')
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datos_salida['metadata']['timestamp'],
            'cliente': datos_salida['metadata']['cliente'],
            'resumen': datos_salida['resumen']
        }, f, indent=2, ensure_ascii=False)
    
    return ruta_carpeta_destino


@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "mensaje": "API de Datos de Salida - Proyecto GNV",
        "version": "1.0.0",
        "endpoints": {
            "/datos-salida": "GET - Obtiene todos los datos de salida del proyecto con timestamp",
            "/datos-salida/crear-carpeta": "POST - Crea la carpeta 'cliente 1 - petroliquidos' con los archivos"
        }
    }


@app.get("/datos-salida", response_model=OutputDataResponse)
async def obtener_datos_salida():
    """
    Endpoint principal que retorna todos los datos de salida del proyecto
    
    Returns:
        JSON con todos los datos de salida organizados por categoría
    """
    try:
        datos_salida = recopilar_datos_salida()
        
        return JSONResponse(
            content={
                "timestamp": datos_salida['metadata']['timestamp'],
                "cliente": datos_salida['metadata']['cliente'],
                "carpeta_destino": datos_salida['metadata']['carpeta_destino'],
                "archivos_procesados": datos_salida['resumen']['total_archivos'],
                "datos": datos_salida
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al recopilar datos de salida: {str(e)}"
        )


@app.post("/datos-salida/crear-carpeta")
async def crear_carpeta_cliente():
    """
    Crea la carpeta "cliente 1 - petroliquidos" con timestamp y copia todos los archivos
    
    Returns:
        Información sobre la carpeta creada
    """
    try:
        datos_salida = recopilar_datos_salida()
        ruta_carpeta = crear_estructura_carpeta_cliente(datos_salida)
        
        return {
            "mensaje": "Carpeta creada exitosamente",
            "carpeta": datos_salida['metadata']['carpeta_destino'],
            "ruta_completa": ruta_carpeta,
            "timestamp": datos_salida['metadata']['timestamp'],
            "archivos_copiados": datos_salida['resumen']['total_archivos'],
            "estructura": {
                "outputs": len(datos_salida['outputs'].get('archivos', [])),
                "data": len(datos_salida['data'].get('archivos', [])),
                "docs": len(datos_salida['docs'].get('archivos', [])),
                "assets": len(datos_salida['assets'].get('archivos', []))
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear carpeta: {str(e)}"
        )


@app.get("/datos-salida/resumen")
async def obtener_resumen():
    """
    Retorna un resumen de los datos de salida sin incluir el contenido de los archivos
    (más ligero para consultas rápidas)
    """
    try:
        datos_salida = recopilar_datos_salida()
        
        # Crear resumen sin contenido base64
        resumen = {
            "timestamp": datos_salida['metadata']['timestamp'],
            "cliente": datos_salida['metadata']['cliente'],
            "carpeta_destino": datos_salida['metadata']['carpeta_destino'],
            "resumen": datos_salida['resumen'],
            "archivos": {
                "outputs": [
                    {
                        "nombre": a['nombre'],
                        "tamaño_bytes": a['tamaño_bytes'],
                        "fecha_modificacion": a['fecha_modificacion'],
                        "tipo_mime": a['tipo_mime']
                    }
                    for a in datos_salida['outputs'].get('archivos', [])
                ],
                "data": [
                    {
                        "nombre": a['nombre'],
                        "tamaño_bytes": a['tamaño_bytes'],
                        "fecha_modificacion": a['fecha_modificacion'],
                        "tipo_mime": a['tipo_mime']
                    }
                    for a in datos_salida['data'].get('archivos', [])
                ],
                "docs": [
                    {
                        "nombre": a['nombre'],
                        "tamaño_bytes": a['tamaño_bytes'],
                        "fecha_modificacion": a['fecha_modificacion'],
                        "tipo_mime": a['tipo_mime']
                    }
                    for a in datos_salida['docs'].get('archivos', [])
                ],
                "assets": [
                    {
                        "nombre": a['nombre'],
                        "tamaño_bytes": a['tamaño_bytes'],
                        "fecha_modificacion": a['fecha_modificacion'],
                        "tipo_mime": a['tipo_mime']
                    }
                    for a in datos_salida['assets'].get('archivos', [])
                ]
            }
        }
        
        return resumen
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener resumen: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

