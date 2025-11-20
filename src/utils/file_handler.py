"""
Manejo de archivos y descargas
"""
import os
import base64
import json
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO

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

# Verificar disponibilidad de weasyprint
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError, Exception):
    # Captura ImportError, errores de carga de DLLs y otros errores
    WEASYPRINT_AVAILABLE = False
    HTML = None  # Definir HTML como None si no está disponible

def get_file_mime_type(filename):
    """Obtiene el MIME type según la extensión del archivo"""
    mime_types = {
        '.md': 'application/pdf',  # Cambiado a PDF porque ahora convertimos MD a PDF
        '.json': 'application/pdf',  # Cambiado a PDF porque ahora convertimos JSON a PDF
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xml': 'application/xml',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.html': 'text/html'
    }
    file_ext = os.path.splitext(filename)[1].lower()
    return mime_types.get(file_ext, 'application/octet-stream')

def generar_pdf_desde_html(html_content: str) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Genera PDF desde contenido HTML usando weasyprint
    
    Args:
        html_content: Contenido HTML como string
    
    Returns:
        tuple: (pdf_bytes, error_message)
        Si hay error, pdf_bytes será None y error_message contendrá el mensaje
        Si es exitoso, error_message será None
    """
    if not WEASYPRINT_AVAILABLE or HTML is None:
        return None, "weasyprint no está instalado. Instale con: pip install weasyprint"
    
    try:
        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()
        return pdf_data, None
    except Exception as e:
        return None, f"Error al generar PDF: {str(e)}"

def create_download_link(file_path, display_text, button_style="default", 
                         titulo: Optional[str] = None,
                         header: Optional[str] = None,
                         footer: Optional[str] = None):
    """
    Crea un enlace de descarga para un archivo.
    Si es un archivo .md o .json, lo convierte a HTML y luego a PDF.
    
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
        
        # Si es un archivo .md, convertirlo a HTML y luego a PDF
        if file_ext == '.md' and CONVERSION_AVAILABLE:
            try:
                ruta_archivo = Path(file_path)
                html_content, nombre_archivo = procesar_archivo_md(
                    ruta_archivo,
                    titulo=titulo,
                    header=header,
                    footer=footer
                )
                # Generar PDF desde HTML
                pdf_data, error_msg = generar_pdf_desde_html(html_content)
                if pdf_data:
                    file_data = pdf_data
                    mime_type = 'application/pdf'
                    download_filename = f"{nombre_sin_ext}.pdf"
                else:
                    # Si falla la generación de PDF, usar HTML como fallback
                    file_data = html_content.encode('utf-8')
                    mime_type = 'text/html'
                    download_filename = f"{nombre_sin_ext}.html"
            except Exception as e:
                # Si falla la conversión, usar el archivo original
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                mime_type = get_file_mime_type(file_path)
                download_filename = filename
        
        # Si es un archivo .json, convertirlo a HTML y luego a PDF
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
                # Generar PDF desde HTML
                pdf_data, error_msg = generar_pdf_desde_html(html_content)
                if pdf_data:
                    file_data = pdf_data
                    mime_type = 'application/pdf'
                    download_filename = f"{nombre_sin_ext}.pdf"
                else:
                    # Si falla la generación de PDF, usar HTML como fallback
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
        
        # Actualizar el texto del botón si es PDF
        if file_ext in ['.md', '.json'] and CONVERSION_AVAILABLE:
            display_text = display_text.replace('.md', '.pdf').replace('.json', '.pdf')
            display_text = display_text.replace('.html', '.pdf')
        
        href = f'<a href="data:{mime_type};base64,{b64_file}" download="{download_filename}" style="{style}">{display_text}</a>'
        return href
    except Exception as e:
        return None

def file_exists(file_path):
    """Verifica si un archivo existe"""
    return os.path.exists(file_path)

