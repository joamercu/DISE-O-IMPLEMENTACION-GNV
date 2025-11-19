"""
Manejo de archivos y descargas
"""
import os
import base64

def get_file_mime_type(filename):
    """Obtiene el MIME type según la extensión del archivo"""
    mime_types = {
        '.md': 'text/markdown',
        '.json': 'application/json',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xml': 'application/xml',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.html': 'text/html'
    }
    file_ext = os.path.splitext(filename)[1].lower()
    return mime_types.get(file_ext, 'application/octet-stream')

def create_download_link(file_path, display_text, button_style="default"):
    """
    Crea un enlace de descarga para un archivo
    
    Args:
        file_path: Ruta del archivo
        display_text: Texto a mostrar en el botón
        button_style: Estilo del botón (default, primary, etc.)
    
    Returns:
        str: HTML del enlace de descarga o None si el archivo no existe
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        mime_type = get_file_mime_type(file_path)
        b64_file = base64.b64encode(file_data).decode()
        filename = os.path.basename(file_path)
        
        styles = {
            "default": "background-color: #2AA1FF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;",
            "primary": "background-color: #FF7A00; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;"
        }
        style = styles.get(button_style, styles["default"])
        
        href = f'<a href="data:{mime_type};base64,{b64_file}" download="{filename}" style="{style}">{display_text}</a>'
        return href
    except Exception as e:
        return None

def file_exists(file_path):
    """Verifica si un archivo existe"""
    return os.path.exists(file_path)

