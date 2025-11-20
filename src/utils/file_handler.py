"""
Manejo de archivos y descargas
"""
import os
import base64
import json
from pathlib import Path
from typing import Optional

# Importar funciones de conversión
try:
    from .documentos_utils import (
        convertir_md_a_html,
        convertir_json_a_html,
        procesar_archivo_md
    )
    CONVERSION_AVAILABLE = True
except ImportError:
    CONVERSION_AVAILABLE = False

def get_file_mime_type(filename):
    """Obtiene el MIME type según la extensión del archivo"""
    mime_types = {
        '.md': 'text/html',  # Cambiado a HTML porque ahora convertimos MD a HTML
        '.json': 'text/html',  # Cambiado a HTML porque ahora convertimos JSON a HTML
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xml': 'application/xml',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.html': 'text/html'
    }
    file_ext = os.path.splitext(filename)[1].lower()
    return mime_types.get(file_ext, 'application/octet-stream')

def create_download_link(file_path, display_text, button_style="default", 
                         titulo: Optional[str] = None,
                         header: Optional[str] = None,
                         footer: Optional[str] = None):
    """
    Crea un enlace de descarga para un archivo.
    Si es un archivo .md o .json, lo convierte a HTML primero.
    
    Args:
        file_path: Ruta del archivo
        display_text: Texto a mostrar en el botón
        button_style: Estilo del botón (default, primary, etc.)
        titulo: Título personalizado para HTML (opcional)
        header: Header personalizado para HTML (opcional)
        footer: Footer personalizado para HTML (opcional)
    
    Returns:
        str: HTML del enlace de descarga o None si el archivo no existe
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path)
        nombre_sin_ext = os.path.splitext(filename)[0]
        
        # Si es un archivo .md, convertirlo a HTML
        if file_ext == '.md' and CONVERSION_AVAILABLE:
            try:
                ruta_archivo = Path(file_path)
                html_content, nombre_archivo = procesar_archivo_md(
                    ruta_archivo,
                    titulo=titulo,
                    header=header,
                    footer=footer
                )
                file_data = html_content.encode('utf-8')
                mime_type = 'text/html'
                download_filename = f"{nombre_sin_ext}.html"
            except Exception as e:
                # Si falla la conversión, usar el archivo original
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                mime_type = get_file_mime_type(file_path)
                download_filename = filename
        
        # Si es un archivo .json, convertirlo a HTML
        elif file_ext == '.json' and CONVERSION_AVAILABLE:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                html_content = convertir_json_a_html(
                    json_data,
                    titulo=titulo or nombre_sin_ext.replace('_', ' ').title(),
                    header=header,
                    footer=footer,
                    nombre_archivo=nombre_sin_ext
                )
                file_data = html_content.encode('utf-8')
                mime_type = 'text/html'
                download_filename = f"{nombre_sin_ext}.html"
            except Exception as e:
                # Si falla la conversión, usar el archivo original
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                mime_type = get_file_mime_type(file_path)
                download_filename = filename
        
        # Para otros tipos de archivo, usar el archivo original
        else:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            mime_type = get_file_mime_type(file_path)
            download_filename = filename
        
        b64_file = base64.b64encode(file_data).decode()
        
        styles = {
            "default": "background-color: #2AA1FF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;",
            "primary": "background-color: #FF7A00; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;"
        }
        style = styles.get(button_style, styles["default"])
        
        # Actualizar el texto del botón si es HTML
        if file_ext in ['.md', '.json'] and CONVERSION_AVAILABLE:
            display_text = display_text.replace('.md', '.html').replace('.json', '.html')
        
        href = f'<a href="data:{mime_type};base64,{b64_file}" download="{download_filename}" style="{style}">{display_text}</a>'
        return href
    except Exception as e:
        return None

def file_exists(file_path):
    """Verifica si un archivo existe"""
    return os.path.exists(file_path)

