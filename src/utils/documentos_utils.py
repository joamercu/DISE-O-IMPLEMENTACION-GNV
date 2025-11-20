#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilidades para conversión de documentos Markdown y JSON a HTML para impresión PDF
Basado en: d:\11-11-25-PRESUPUESO - MONTAGAS SA ESP\06_PLAN_BASE_DATOS\utils\documentos.py
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


def convertir_md_a_html(
    contenido_md: str,
    titulo: Optional[str] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    nombre_archivo: Optional[str] = None
) -> str:
    """
    Convierte contenido Markdown a HTML optimizado para impresión PDF
    
    Args:
        contenido_md: Contenido del archivo Markdown
        titulo: Título personalizado del documento
        header: Texto personalizado para el encabezado
        footer: Texto personalizado para el pie de página
        nombre_archivo: Nombre del archivo (para generar títulos automáticos)
    
    Returns:
        HTML completo listo para imprimir
    """
    if not MARKDOWN_AVAILABLE:
        raise ImportError("La librería 'markdown' no está instalada. Instala con: pip install markdown")
    
    # Remover comentarios HTML del markdown
    md_content_clean = re.sub(r'<!--.*?ENCABEZADO.*?-->', '', contenido_md, flags=re.DOTALL)
    md_content_clean = re.sub(r'<!--.*?PIE DE PÁGINA.*?-->', '', md_content_clean, flags=re.DOTALL)
    
    # Convertir markdown a HTML
    html_content = markdown.markdown(
        md_content_clean, 
        extensions=['tables', 'fenced_code', 'codehilite', 'toc']
    )
    
    # Generar títulos dinámicos
    if nombre_archivo:
        nombre_limpio = nombre_archivo.replace('_', ' ').replace('-', ' ').title()
    else:
        nombre_limpio = "Documento"
    
    titulo_documento = titulo if titulo else nombre_limpio
    titulo_html = f"{titulo_documento} - WELDTECH SOLUTIONS" if "WELDTECH" not in titulo_documento.upper() else titulo_documento
    
    # Generar encabezado y pie de página
    texto_header = header if header else titulo_documento
    
    # Formato de fecha en español
    meses_es = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    fecha_obj = datetime.now()
    fecha_actual = f"{fecha_obj.day} de {meses_es[fecha_obj.month]} de {fecha_obj.year}"
    
    texto_footer = footer if footer else f"{nombre_limpio} | Versión 1.0 | {fecha_actual}"
    
    # HTML completo con estilos optimizados para impresión
    html_full = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{titulo_html}</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 2.5cm 2cm;
            }}
            
            .header {{
                position: running(header);
                text-align: center;
                font-size: 9pt;
                color: #6B7280;
                border-bottom: 2px solid #FF7A00;
                padding-bottom: 5px;
                margin-bottom: 10px;
            }}
            
            .footer {{
                position: running(footer);
                text-align: center;
                font-size: 8pt;
                color: #6B7280;
                border-top: 1px solid #E5E7EB;
                padding-top: 5px;
                margin-top: 10px;
            }}
            
            body {{
                margin: 0;
                padding: 0;
            }}
        }}
        
        @page {{
            @top-center {{
                content: element(header);
            }}
            @bottom-center {{
                content: element(footer);
            }}
        }}
        
        .header {{
            text-align: center;
            font-size: 9pt;
            color: #6B7280;
            border-bottom: 2px solid #FF7A00;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }}
        
        .footer {{
            text-align: center;
            font-size: 8pt;
            color: #6B7280;
            border-top: 1px solid #E5E7EB;
            padding-top: 5px;
            margin-top: 20px;
        }}
        
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 10pt;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            color: #0F1216;
            border-bottom: 3px solid #FF7A00;
            padding-bottom: 10px;
            page-break-after: avoid;
            font-size: 20pt;
            margin-top: 0;
        }}
        
        h2 {{
            color: #0F1216;
            border-bottom: 2px solid #2AA1FF;
            padding-bottom: 8px;
            page-break-after: avoid;
            font-size: 14pt;
            margin-top: 20px;
        }}
        
        h3 {{
            color: #6B7280;
            font-size: 12pt;
            margin-top: 15px;
            page-break-after: avoid;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            page-break-inside: auto;
            font-size: 8.5pt;
        }}
        
        thead {{
            display: table-header-group;
        }}
        
        tfoot {{
            display: table-footer-group;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 6px;
            text-align: left;
            vertical-align: top;
        }}
        
        th {{
            background-color: #FF7A00;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 9pt;
        }}
        
        tr:nth-child(even) {{
            background-color: #E5E7EB;
        }}
        
        td:first-child strong {{
            color: #0F1216;
            font-size: 10pt;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 9pt;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            page-break-inside: avoid;
            font-size: 9pt;
        }}
        
        ul, ol {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }}
        
        p {{
            margin: 10px 0;
        }}
        
        strong {{
            color: #0F1216;
        }}
        
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #FF7A00;
            color: #FFFFFF;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14pt;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(255, 122, 0, 0.3);
        }}
        
        .print-button:hover {{
            background-color: #FF9500;
            box-shadow: 0 4px 10px rgba(255, 122, 0, 0.5);
        }}
        
        @media print {{
            .print-button {{
                display: none;
            }}
        }}
    </style>
    <script>
        function imprimirPDF() {{
            window.print();
        }}
    </script>
</head>
<body>
    <button class="print-button" onclick="imprimirPDF()">🖨️ Imprimir a PDF</button>
    
    <div class="header">
        {texto_header}
    </div>
    
    {html_content}
    
    <div class="footer">
        {texto_footer}<br>
        Confidencial - Uso exclusivo del cliente
    </div>
</body>
</html>"""
    
    return html_full


def convertir_json_a_html(
    contenido_json: Dict[str, Any],
    titulo: Optional[str] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    nombre_archivo: Optional[str] = None
) -> str:
    """
    Convierte contenido JSON a HTML optimizado para impresión PDF
    
    Args:
        contenido_json: Diccionario con el contenido JSON
        titulo: Título personalizado del documento
        header: Texto personalizado para el encabezado
        footer: Texto personalizado para el pie de página
        nombre_archivo: Nombre del archivo (para generar títulos automáticos)
    
    Returns:
        HTML completo listo para imprimir
    """
    # Generar títulos dinámicos
    if nombre_archivo:
        nombre_limpio = nombre_archivo.replace('_', ' ').replace('-', ' ').title()
    else:
        nombre_limpio = "Documento JSON"
    
    titulo_documento = titulo if titulo else nombre_limpio
    titulo_html = f"{titulo_documento} - WELDTECH SOLUTIONS" if "WELDTECH" not in titulo_documento.upper() else titulo_documento
    
    # Generar encabezado y pie de página
    texto_header = header if header else titulo_documento
    
    # Formato de fecha en español
    meses_es = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    fecha_obj = datetime.now()
    fecha_actual = f"{fecha_obj.day} de {meses_es[fecha_obj.month]} de {fecha_obj.year}"
    
    texto_footer = footer if footer else f"{nombre_limpio} | Versión 1.0 | {fecha_actual}"
    
    # Convertir JSON a HTML formateado
    def json_to_html(obj, level=0):
        """Convierte recursivamente un objeto JSON a HTML"""
        html = ""
        indent = "  " * level
        
        if isinstance(obj, dict):
            html += f"{indent}<div class='json-object'>\n"
            for key, value in obj.items():
                key_display = key.replace('_', ' ').title()
                html += f"{indent}  <div class='json-item'>\n"
                html += f"{indent}    <strong class='json-key'>{key_display}:</strong>\n"
                html += json_to_html(value, level + 2)
                html += f"{indent}  </div>\n"
            html += f"{indent}</div>\n"
        elif isinstance(obj, list):
            html += f"{indent}<ul class='json-list'>\n"
            for item in obj:
                html += f"{indent}  <li>\n"
                html += json_to_html(item, level + 2)
                html += f"{indent}  </li>\n"
            html += f"{indent}</ul>\n"
        else:
            value_str = str(obj)
            if isinstance(obj, (int, float)):
                html += f"{indent}<span class='json-value json-number'>{value_str}</span>\n"
            elif isinstance(obj, bool):
                html += f"{indent}<span class='json-value json-boolean'>{value_str}</span>\n"
            elif obj is None:
                html += f"{indent}<span class='json-value json-null'>null</span>\n"
            else:
                html += f"{indent}<span class='json-value json-string'>{value_str}</span>\n"
        
        return html
    
    json_html = json_to_html(contenido_json)
    
    # HTML completo con estilos optimizados para impresión
    html_full = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{titulo_html}</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 2.5cm 2cm;
            }}
            
            .header {{
                position: running(header);
                text-align: center;
                font-size: 9pt;
                color: #6B7280;
                border-bottom: 2px solid #FF7A00;
                padding-bottom: 5px;
                margin-bottom: 10px;
            }}
            
            .footer {{
                position: running(footer);
                text-align: center;
                font-size: 8pt;
                color: #6B7280;
                border-top: 1px solid #E5E7EB;
                padding-top: 5px;
                margin-top: 10px;
            }}
            
            body {{
                margin: 0;
                padding: 0;
            }}
        }}
        
        @page {{
            @top-center {{
                content: element(header);
            }}
            @bottom-center {{
                content: element(footer);
            }}
        }}
        
        .header {{
            text-align: center;
            font-size: 9pt;
            color: #6B7280;
            border-bottom: 2px solid #FF7A00;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }}
        
        .footer {{
            text-align: center;
            font-size: 8pt;
            color: #6B7280;
            border-top: 1px solid #E5E7EB;
            padding-top: 5px;
            margin-top: 20px;
        }}
        
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 10pt;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            color: #0F1216;
            border-bottom: 3px solid #FF7A00;
            padding-bottom: 10px;
            page-break-after: avoid;
            font-size: 20pt;
            margin-top: 0;
        }}
        
        .json-object {{
            margin: 10px 0;
            padding-left: 20px;
            border-left: 2px solid #E5E7EB;
        }}
        
        .json-item {{
            margin: 8px 0;
        }}
        
        .json-key {{
            color: #0F1216;
            font-size: 11pt;
        }}
        
        .json-value {{
            margin-left: 10px;
        }}
        
        .json-number {{
            color: #2AA1FF;
            font-weight: bold;
        }}
        
        .json-string {{
            color: #28a745;
        }}
        
        .json-boolean {{
            color: #FF7A00;
            font-weight: bold;
        }}
        
        .json-null {{
            color: #6B7280;
            font-style: italic;
        }}
        
        .json-list {{
            list-style-type: none;
            padding-left: 20px;
        }}
        
        .json-list li {{
            margin: 5px 0;
            padding: 5px;
            background-color: #F9FAFB;
            border-radius: 3px;
        }}
        
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #FF7A00;
            color: #FFFFFF;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14pt;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(255, 122, 0, 0.3);
        }}
        
        .print-button:hover {{
            background-color: #FF9500;
            box-shadow: 0 4px 10px rgba(255, 122, 0, 0.5);
        }}
        
        @media print {{
            .print-button {{
                display: none;
            }}
        }}
    </style>
    <script>
        function imprimirPDF() {{
            window.print();
        }}
    </script>
</head>
<body>
    <button class="print-button" onclick="imprimirPDF()">🖨️ Imprimir a PDF</button>
    
    <div class="header">
        {texto_header}
    </div>
    
    <h1>{titulo_documento}</h1>
    
    <div class="json-content">
        {json_html}
    </div>
    
    <div class="footer">
        {texto_footer}<br>
        Confidencial - Uso exclusivo del cliente
    </div>
</body>
</html>"""
    
    return html_full


def procesar_archivo_md(
    ruta_archivo: Path,
    titulo: Optional[str] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None
) -> Tuple[str, str]:
    """
    Procesa un archivo Markdown y lo convierte a HTML
    
    Args:
        ruta_archivo: Ruta al archivo Markdown
        titulo: Título personalizado
        header: Header personalizado
        footer: Footer personalizado
    
    Returns:
        Tupla (contenido_html, nombre_archivo)
    """
    if not ruta_archivo.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
    
    # Leer el contenido
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido_md = f.read()
    
    # Obtener nombre del archivo sin extensión
    nombre_archivo = ruta_archivo.stem
    
    # Convertir a HTML
    html = convertir_md_a_html(
        contenido_md,
        titulo=titulo,
        header=header,
        footer=footer,
        nombre_archivo=nombre_archivo
    )
    
    return html, nombre_archivo

