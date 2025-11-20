"""
Utilidades para manejo del manifest
"""
import json
import os
import sys
from datetime import datetime

# Importar configuración
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MANIFEST_FILE

def load_manifest():
    """Carga el manifest JSON del proyecto"""
    manifest_path = MANIFEST_FILE
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return None
    return None

def save_manifest(manifest_data):
    """Guarda el manifest JSON"""
    manifest_path = MANIFEST_FILE
    try:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        return False

def generate_manifest_html(manifest_data):
    """Genera un archivo HTML formateado del manifest"""
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Obtener información del proyecto
    project = manifest_data.get('project', {})
    cliente_nombre = project.get('client', 'N/A')
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manifest del Proyecto - {cliente_nombre}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 4px solid #FF7A00;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #0F1216;
            margin: 0;
            font-size: 28pt;
        }}
        h2 {{
            color: #124272;
            border-bottom: 2px solid #2AA1FF;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        h3 {{
            color: #173e62;
            margin-top: 25px;
        }}
        .info-box {{
            background-color: #f4f4f4;
            border-left: 4px solid #FF7A00;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #173e62;
            color: #fff;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .status-completo {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-pendiente {{
            color: #ffc107;
            font-weight: bold;
        }}
        .priority-high {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
        }}
        .priority-medium {{
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 10px;
            margin: 10px 0;
        }}
        .metric {{
            display: inline-block;
            background: #f8f9fa;
            padding: 15px;
            margin: 10px;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            min-width: 200px;
        }}
        .metric-value {{
            font-size: 24pt;
            font-weight: bold;
            color: #0F1216;
        }}
        .metric-label {{
            color: #6c757d;
            font-size: 12pt;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
            color: #6B7280;
            text-align: center;
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
    <div class="container">
        <div class="header">
            <h1>📋 Manifest del Proyecto</h1>
            <p><strong>Cliente:</strong> {project.get('client', 'N/A')}<br>
            <strong>Proyecto:</strong> {project.get('name', 'N/A')}<br>
            <strong>Versión:</strong> {project.get('version', 'N/A')}<br>
            <strong>Fecha de Creación:</strong> {project.get('date_created', 'N/A')}<br>
            <strong>Estado:</strong> {project.get('status', 'N/A')}<br>
            <strong>Generado:</strong> {fecha_actual}</p>
        </div>
"""
    
    # Entregables
    if 'deliverables' in manifest_data:
        html += "<h2>📦 Entregables</h2>"
        deliverables = manifest_data['deliverables']
        for key, value in deliverables.items():
            if isinstance(value, dict):
                status_class = "status-completo" if value.get('status') == 'Completo' else "status-pendiente"
                html += f"""
        <div class="info-box">
            <h3>📄 {value.get('filename', key)}</h3>
            <p><strong>Formato:</strong> {value.get('format', 'N/A')}</p>
            <p><strong>Estado:</strong> <span class="{status_class}">{value.get('status', 'N/A')}</span></p>
            <p><strong>Descripción:</strong> {value.get('description', 'N/A')}</p>
"""
                if 'sections' in value:
                    html += "<p><strong>Secciones incluidas:</strong></p><ul>"
                    for section in value['sections']:
                        html += f"<li>{section}</li>"
                    html += "</ul>"
                html += "</div>"
    
    # Parámetros Técnicos
    if 'technical_parameters' in manifest_data:
        html += "<h2>⚙️ Parámetros Técnicos</h2>"
        tech_params = manifest_data['technical_parameters']
        
        if 'configurations_analyzed' in tech_params:
            html += "<h3>Configuraciones Analizadas</h3><table><thead><tr>"
            configs = tech_params['configurations_analyzed']
            if configs:
                for key in configs[0].keys():
                    html += f"<th>{key.replace('_', ' ').title()}</th>"
                html += "</tr></thead><tbody>"
                for config in configs:
                    html += "<tr>"
                    for value in config.values():
                        html += f"<td>{value}</td>"
                    html += "</tr>"
                html += "</tbody></table>"
    
    # Riesgos
    if 'risks_identified' in manifest_data:
        html += "<h2>⚠️ Riesgos Identificados</h2><table><thead><tr>"
        risks = manifest_data['risks_identified']
        if risks:
            for key in risks[0].keys():
                html += f"<th>{key.replace('_', ' ').title()}</th>"
            html += "</tr></thead><tbody>"
            for risk in risks:
                html += "<tr>"
                for value in risk.values():
                    html += f"<td>{value}</td>"
                html += "</tr>"
            html += "</tbody></table>"
    
    # Decisiones Pendientes
    if 'pending_decisions' in manifest_data:
        html += "<h2>❓ Decisiones Pendientes</h2>"
        decisions = manifest_data['pending_decisions']
        
        if 'high_priority' in decisions:
            html += "<h3>🔴 Alta Prioridad</h3>"
            for decision in decisions['high_priority']:
                html += f"""
        <div class="priority-high">
            <p><strong>{decision.get('question', 'N/A')}</strong></p>
            <p><strong>Impacto:</strong> {decision.get('impact', 'N/A')}</p>
            <p><strong>Estado:</strong> {decision.get('status', 'N/A')}</p>
        </div>
"""
        
        if 'medium_priority' in decisions:
            html += "<h3>🟡 Prioridad Media</h3>"
            for decision in decisions['medium_priority']:
                html += f"""
        <div class="priority-medium">
            <p><strong>{decision.get('question', 'N/A')}</strong></p>
            <p><strong>Impacto:</strong> {decision.get('impact', 'N/A')}</p>
            <p><strong>Estado:</strong> {decision.get('status', 'N/A')}</p>
        </div>
"""
    
    # Costos
    if 'cost_estimates' in manifest_data:
        html += "<h2>💰 Estimaciones de Costo</h2>"
        costs = manifest_data['cost_estimates']
        if 'breakdown' in costs:
            breakdown = costs['breakdown']
            html += '<div style="display: flex; flex-wrap: wrap;">'
            if 'subtotal_components' in breakdown:
                html += f'<div class="metric"><div class="metric-label">Subtotal Componentes</div><div class="metric-value">${breakdown["subtotal_components"].get("usd", 0):,.0f} USD</div></div>'
            if 'total_estimated' in breakdown:
                total = breakdown['total_estimated']
                html += f'<div class="metric"><div class="metric-label">Total Estimado</div><div class="metric-value">${total.get("usd", 0):,.0f} USD</div></div>'
                html += f'<div class="metric"><div class="metric-label">Total Estimado (COP)</div><div class="metric-value">${total.get("cop", 0):,.0f}</div></div>'
            html += '</div>'
    
    # Datos del Cliente
    if 'cliente_data' in manifest_data:
        html += "<h2>👤 Datos del Cliente</h2>"
        cliente = manifest_data['cliente_data']
        html += f"""
        <div class="info-box">
            <p><strong>Nombre:</strong> {cliente.get('nombre', 'N/A')}</p>
            <p><strong>Rol:</strong> {cliente.get('rol', 'N/A')}</p>
            <p><strong>Capacidad de la Flota:</strong> {cliente.get('capacidad_de_la_flota', 'N/A')}</p>
        </div>
"""
    
    html += f"""
        <div class="footer">
            <p><strong>CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL</strong></p>
            <p>Manifest generado automáticamente el {fecha_actual}</p>
            <p><em>Confidencial - Uso exclusivo del cliente {cliente_nombre}</em></p>
        </div>
    </div>
</body>
</html>
"""
    return html

