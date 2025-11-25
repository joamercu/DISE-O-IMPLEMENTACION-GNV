"""
Página Streamlit: Calculadora de Capacidad y Espesor de Tanques GNV

Permite calcular la capacidad y el espesor requerido de cilindros GNV
según las normas ISO 11439 y ASME Section VIII.

Autor: Sistema de Diseño GNV
Fecha: 2025-01-27
"""

import streamlit as st
import sys
import os
from pathlib import Path
from typing import Dict, Optional

# Agregar src al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tank_calculator import (
    calcular_capacidad_cilindro,
    calcular_espesor_iso11439,
    calcular_espesor_asme,
    validar_espesor,
    calcular_presion_prueba,
    obtener_propiedades_material,
    listar_materiales,
    MATERIALES
)
from datetime import datetime

def generar_informe_html_tanques(capacidad_result, espesor_result, validacion, norma_usada, parametros, material_props, incluye_tapas):
    """
    Genera un informe HTML profesional para los resultados de la calculadora de tanques GNV
    """
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Formatear fecha en español
    meses_es = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    fecha_obj = datetime.now()
    fecha_es = f"{fecha_obj.day} de {meses_es[fecha_obj.month]} de {fecha_obj.year}"
    
    # Determinar estado con color
    estado_color = "#28a745" if validacion['es_valido'] else "#dc3545"
    if validacion['es_valido'] and "Marginal" in validacion['estado']:
        estado_color = "#ffc107"
    
    # Generar contenido de capacidad según si incluye tapas
    if incluye_tapas:
        capacidad_content = f"""
        <div class="metric-grid">
            <div class="metric">
                <div class="metric-value">{capacidad_result['volumen_total_litros']:.2f} L</div>
                <div class="metric-label">Volumen Total</div>
            </div>
            <div class="metric">
                <div class="metric-value">{capacidad_result['volumen_total_m3']:.4f} m³</div>
                <div class="metric-label">Volumen Total</div>
            </div>
            <div class="metric">
                <div class="metric-value">{capacidad_result['volumen_cuerpo_litros']:.2f} L</div>
                <div class="metric-label">Volumen Cuerpo</div>
            </div>
            <div class="metric">
                <div class="metric-value">{capacidad_result['volumen_tapas_litros']:.2f} L</div>
                <div class="metric-label">Volumen Tapas</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Diámetro Interno</td>
                    <td>{capacidad_result['diametro_interno_mm']:.2f}</td>
                    <td>mm</td>
                </tr>
                <tr>
                    <td>Radio Interno</td>
                    <td>{capacidad_result['radio_interno_mm']:.2f}</td>
                    <td>mm</td>
                </tr>
                <tr>
                    <td>Longitud del Cuerpo</td>
                    <td>{capacidad_result['longitud_cuerpo_mm']:.2f}</td>
                    <td>mm</td>
                </tr>
            </tbody>
        </table>
        """
    else:
        capacidad_content = f"""
        <div class="metric-grid">
            <div class="metric">
                <div class="metric-value">{capacidad_result['volumen_cuerpo_litros']:.2f} L</div>
                <div class="metric-label">Volumen Interno</div>
            </div>
            <div class="metric">
                <div class="metric-value">{capacidad_result['volumen_total_m3']:.4f} m³</div>
                <div class="metric-label">Volumen Interno</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Diámetro Interno</td>
                    <td>{capacidad_result['diametro_interno_mm']:.2f}</td>
                    <td>mm</td>
                </tr>
                <tr>
                    <td>Radio Interno</td>
                    <td>{capacidad_result['radio_interno_mm']:.2f}</td>
                    <td>mm</td>
                </tr>
            </tbody>
        </table>
        """
    
    # Generar advertencias
    advertencias_html = ""
    advertencias = []
    
    if validacion['factor_seguridad'] < 2.25:
        advertencias.append("❌ **Factor de seguridad insuficiente**: El factor de seguridad calculado es menor al mínimo requerido (2.25 según NTC 3847)")
    
    if validacion['porcentaje_margen'] < 10:
        advertencias.append("⚠️ **Margen bajo**: Se recomienda un margen mínimo del 10% sobre el espesor requerido")
    
    if parametros['espesor_actual'] < espesor_result['espesor_con_tolerancia_mm']:
        advertencias.append("⚠️ **Tolerancia de fabricación**: El espesor actual es menor que el espesor requerido con tolerancia de fabricación (15%)")
    
    if parametros['espesor_actual'] < 5.0 or parametros['espesor_actual'] > 10.0:
        advertencias.append("ℹ️ **Rango atípico**: El espesor está fuera del rango típico para cilindros GNV (5-8 mm para Tipo 1)")
    
    if advertencias:
        advertencias_html = "<div class='advertencias'>"
        for advertencia in advertencias:
            advertencias_html += f"<div class='advertencia'>{advertencia}</div>"
        advertencias_html += "</div>"
    else:
        advertencias_html = "<div class='success-message'>✅ No se detectaron problemas. El diseño cumple con todos los requisitos.</div>"
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Cálculo - Tanque GNV</title>
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
            text-align: center;
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
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24pt;
            font-weight: bold;
            color: #0F1216;
        }}
        .metric-label {{
            color: #6c757d;
            font-size: 12pt;
            margin-top: 5px;
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
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            background-color: {estado_color};
        }}
        .advertencias {{
            margin: 20px 0;
        }}
        .advertencia {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .success-message {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 4px;
            color: #155724;
        }}
        .formula-box {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
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
            body {{
                background-color: white;
            }}
            .container {{
                box-shadow: none;
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
            <h1>🔧 Informe de Cálculo - Tanque GNV</h1>
            <p><strong>Fecha de Generación:</strong> {fecha_es}<br>
            <strong>Norma Aplicada:</strong> {norma_usada}<br>
            <strong>Estado de Validación:</strong> <span class="status-badge">{validacion['estado']}</span></p>
        </div>

        <h2>📥 Parámetros de Entrada</h2>
        <table>
            <thead>
                <tr>
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Diámetro Exterior</td>
                    <td>{parametros['diametro_exterior']:.2f}</td>
                    <td>mm</td>
                </tr>
                <tr>
                    <td>Longitud Total</td>
                    <td>{parametros['longitud']:.2f}</td>
                    <td>mm</td>
                </tr>
                <tr>
                    <td>Espesor Actual de Pared</td>
                    <td>{parametros['espesor_actual']:.2f}</td>
                    <td>mm</td>
                </tr>
                <tr>
                    <td>Presión de Trabajo</td>
                    <td>{parametros['presion_trabajo']:.0f}</td>
                    <td>bar</td>
                </tr>
                <tr>
                    <td>Presión de Prueba</td>
                    <td>{parametros['presion_prueba']:.0f}</td>
                    <td>bar</td>
                </tr>
                <tr>
                    <td>Material</td>
                    <td>{material_props['nombre']}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>Incluir Tapas Semiesféricas</td>
                    <td>{'Sí' if incluye_tapas else 'No'}</td>
                    <td>-</td>
                </tr>
            </tbody>
        </table>

        <h2>📏 Resultados de Capacidad</h2>
        {capacidad_content}

        <h2>🛡️ Resultados de Espesor</h2>
        <div class="metric-grid">
            <div class="metric">
                <div class="metric-value">{espesor_result['espesor_minimo_mm']:.2f} mm</div>
                <div class="metric-label">Espesor Mínimo Requerido</div>
            </div>
            <div class="metric">
                <div class="metric-value">{espesor_result['espesor_con_tolerancia_mm']:.2f} mm</div>
                <div class="metric-label">Espesor con Tolerancia (15%)</div>
            </div>
            <div class="metric">
                <div class="metric-value">{parametros['espesor_actual']:.2f} mm</div>
                <div class="metric-label">Espesor Actual</div>
            </div>
        </div>

        <h2>✅ Validación del Espesor</h2>
        <div class="metric-grid">
            <div class="metric">
                <div class="metric-value">{validacion['factor_seguridad']:.2f}</div>
                <div class="metric-label">Factor de Seguridad</div>
            </div>
            <div class="metric">
                <div class="metric-value">{validacion['diferencia_mm']:.2f} mm</div>
                <div class="metric-label">Diferencia (Actual - Requerido)</div>
            </div>
            <div class="metric">
                <div class="metric-value">{validacion['porcentaje_margen']:.1f}%</div>
                <div class="metric-label">Margen de Seguridad</div>
            </div>
        </div>

        <div class="info-box">
            <h3>Conclusión</h3>
            <p>{validacion['mensaje']}</p>
        </div>

        <h2>⚠️ Advertencias y Recomendaciones</h2>
        {advertencias_html}

        <h2>🔬 Propiedades del Material</h2>
        <table>
            <thead>
                <tr>
                    <th>Propiedad</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Límite Elástico (Re)</td>
                    <td>{material_props['limite_elastico_mpa']:.0f}</td>
                    <td>MPa</td>
                </tr>
                <tr>
                    <td>Resistencia a Tracción (Mín)</td>
                    <td>{material_props['resistencia_traccion_min_mpa']:.0f}</td>
                    <td>MPa</td>
                </tr>
                <tr>
                    <td>Resistencia a Tracción (Máx)</td>
                    <td>{material_props['resistencia_traccion_max_mpa']:.0f}</td>
                    <td>MPa</td>
                </tr>
            </tbody>
        </table>

        <div class="info-box">
            <h3>Descripción del Material</h3>
            <p>{material_props['descripcion']}</p>
        </div>

        <h2>📚 Referencias Normativas</h2>
        <div class="info-box">
            <h3>ISO 11439 / NTC 3847</h3>
            <p>• <strong>ISO 11439:2013</strong>: Gas cylinders — High pressure cylinders for the on-board storage of natural gas as a fuel for automotive vehicles</p>
            <p>• <strong>NTC 3847:2002</strong>: Cilindros de alta presión para almacenamiento de GNC para vehículos (equivalente a ISO 11439:2000)</p>
            <p>• <strong>Factor de seguridad mínimo</strong>: 2.25</p>
            <p>• <strong>Presión de prueba</strong>: 1.5 × Presión de trabajo</p>
        </div>

        <div class="info-box">
            <h3>ASME Section VIII, Division 1</h3>
            <p>• <strong>ASME Boiler and Pressure Vessel Code, Section VIII, Division 1</strong>: Rules for Construction of Pressure Vessels</p>
            <p>• <strong>Condición de validez</strong>: P ≤ 0.385 × S × E</p>
            <p>• <strong>Eficiencia de junta</strong>: E = 1.0 para cilindros sin costura</p>
        </div>

        <div class="footer">
            <p><strong>WELDTECH SOLUTIONS - CALCULADORA DE TANQUES GNV</strong></p>
            <p>Informe generado automáticamente el {fecha_actual}</p>
            <p><em>Este documento es confidencial y de uso exclusivo del solicitante</em></p>
        </div>
    </div>
</body>
</html>"""
    
    return html

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Tanques GNV",
    page_icon="🔧",
    layout="wide"
)

# Verificar autenticación y rol de administrador
if 'authenticated' not in st.session_state or not st.session_state.get('authenticated', False):
    st.error("🔒 Acceso Restringido")
    st.warning("Debe iniciar sesión para acceder a esta página.")
    st.info("Por favor, regrese a la página principal e inicie sesión.")
    st.stop()

user_role = st.session_state.get('user_role', '')
if user_role != 'Administrador':
    st.error("🚫 Acceso Denegado")
    st.warning("Esta página es exclusiva para administradores.")
    st.info(f"Su rol actual es: **{user_role}**. Solo los usuarios con rol de **Administrador** pueden acceder a esta herramienta.")
    st.stop()

# Título principal
st.title("🔧 Calculadora de Capacidad y Espesor de Tanques GNV")
st.markdown("---")

# Información inicial
with st.expander("ℹ️ Información sobre esta herramienta", expanded=False):
    st.markdown("""
    Esta calculadora permite determinar:
    
    1. **Capacidad del tanque**: Volumen interno basado en dimensiones físicas
    2. **Espesor requerido**: Según normas ISO 11439 / NTC 3847 o ASME Section VIII
    3. **Validación**: Comparación del espesor actual vs requerido
    
    ### Normas Aplicables:
    - **ISO 11439 / NTC 3847**: Norma específica para cilindros GNV vehiculares
    - **ASME Section VIII, Division 1**: Código para recipientes a presión
    
    ### Factor de Seguridad:
    - Mínimo requerido: **2.25** (según NTC 3847)
    - Presión de prueba: **1.5 × Presión de trabajo**
    """)

# Sidebar para entrada de datos
with st.sidebar:
    st.header("📥 Parámetros de Entrada")
    
    st.subheader("Dimensiones del Cilindro")
    
    diametro_exterior = st.number_input(
        "Diámetro Exterior (mm)",
        min_value=200.0,
        max_value=600.0,
        value=356.0,
        step=1.0,
        help="Diámetro exterior del cilindro en milímetros"
    )
    
    longitud = st.number_input(
        "Longitud (mm)",
        min_value=500.0,
        max_value=2500.0,
        value=1000.0,
        step=10.0,
        help="Longitud del cilindro en milímetros"
    )
    
    espesor_actual = st.number_input(
        "Espesor Actual de Pared (mm)",
        min_value=1.0,
        max_value=50.0,
        value=7.2,
        step=0.1,
        help="Espesor actual de la pared (opcional, para validación)"
    )
    
    incluir_tapas = st.checkbox(
        "Incluir tapas semiesféricas en volumen",
        value=True,
        help="Si está marcado, incluye el volumen de las tapas semiesféricas en el cálculo de capacidad"
    )
    
    st.markdown("---")
    
    st.subheader("Condiciones de Operación")
    
    presion_trabajo = st.selectbox(
        "Presión de Trabajo (bar)",
        options=[200, 250, 300],
        index=0,
        help="Presión de operación del cilindro"
    )
    
    # Calcular presión de prueba automáticamente
    presion_prueba = calcular_presion_prueba(presion_trabajo, factor_seguridad=1.5)
    
    st.info(f"**Presión de Prueba:** {presion_prueba:.0f} bar (calculada automáticamente)")
    
    st.markdown("---")
    
    st.subheader("Material")
    
    materiales_disponibles = list(MATERIALES.keys())
    material_seleccionado = st.selectbox(
        "Material del Cilindro",
        options=materiales_disponibles,
        index=0,
        help="Seleccione el material del cilindro"
    )
    
    # Mostrar propiedades del material seleccionado
    material_props = obtener_propiedades_material(material_seleccionado)
    
    with st.expander("📋 Propiedades del Material"):
        st.write(f"**Nombre:** {material_props['nombre']}")
        st.write(f"**Límite Elástico (R_e):** {material_props['limite_elastico_mpa']:.0f} MPa")
        st.write(f"**Resistencia a Tracción:** {material_props['resistencia_traccion_min_mpa']:.0f} - {material_props['resistencia_traccion_max_mpa']:.0f} MPa")
        st.write(f"**Descripción:** {material_props['descripcion']}")
    
    st.markdown("---")
    
    st.subheader("Norma de Cálculo")
    
    norma_seleccionada = st.radio(
        "Seleccione la norma para cálculo de espesor:",
        options=["ISO 11439 / NTC 3847", "ASME Section VIII"],
        help="ISO 11439 es específica para GNV, ASME es más general"
    )

# Contenido principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Resultados del Cálculo")
    
    # Botón para calcular
    if st.button("🔄 Calcular", type="primary", use_container_width=True):
        try:
            # Calcular capacidad
            capacidad_result = calcular_capacidad_cilindro(
                diametro_exterior_mm=diametro_exterior,
                longitud_mm=longitud,
                espesor_pared_mm=espesor_actual,
                incluir_tapas_semiesfericas=incluir_tapas
            )
            
            # Calcular espesor según norma seleccionada
            if norma_seleccionada == "ISO 11439 / NTC 3847":
                espesor_result = calcular_espesor_iso11439(
                    diametro_exterior_mm=diametro_exterior,
                    presion_prueba_bar=presion_prueba,
                    limite_elastico_mpa=material_props['limite_elastico_mpa']
                )
                norma_usada = "ISO 11439 / NTC 3847"
            else:  # ASME
                espesor_result = calcular_espesor_asme(
                    radio_interior_mm=capacidad_result['radio_interno_mm'],
                    presion_diseno_bar=presion_trabajo,
                    esfuerzo_admisible_mpa=material_props['esfuerzo_admisible_asme_mpa'],
                    eficiencia_junta=1.0
                )
                norma_usada = "ASME Section VIII, Division 1"
            
            # Guardar si incluye tapas
            st.session_state['incluye_tapas'] = incluir_tapas
            
            # Validar espesor
            validacion = validar_espesor(
                espesor_actual_mm=espesor_actual,
                espesor_requerido_mm=espesor_result['espesor_minimo_mm'],
                factor_seguridad_minimo=2.25
            )
            
            # Guardar resultados en session state
            st.session_state['capacidad_result'] = capacidad_result
            st.session_state['espesor_result'] = espesor_result
            st.session_state['validacion'] = validacion
            st.session_state['norma_usada'] = norma_usada
            st.session_state['parametros'] = {
                'diametro_exterior': diametro_exterior,
                'longitud': longitud,
                'espesor_actual': espesor_actual,
                'presion_trabajo': presion_trabajo,
                'presion_prueba': presion_prueba,
                'material': material_seleccionado,
                'norma': norma_seleccionada
            }
            
            st.success("✅ Cálculo completado exitosamente!")
            
        except ValueError as e:
            st.error(f"❌ Error en el cálculo: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            st.exception(e)

with col2:
    st.header("ℹ️ Información")
    
    if 'capacidad_result' in st.session_state:
        capacidad = st.session_state['capacidad_result']
        volumen_display = capacidad.get('volumen_total_litros', capacidad.get('volumen_litros', 0))
        st.metric(
            "Capacidad",
            f"{volumen_display:.1f} L"
        )
        
        if 'espesor_result' in st.session_state:
            st.metric(
                "Espesor Requerido",
                f"{st.session_state['espesor_result']['espesor_minimo_mm']:.2f} mm"
            )
        
        if 'validacion' in st.session_state:
            validacion = st.session_state['validacion']
            st.markdown(f"**Estado:** {validacion['estado']}")

# Mostrar resultados si existen
if 'capacidad_result' in st.session_state:
    st.markdown("---")
    
    # Sección de capacidad
    st.header("📏 Capacidad del Cilindro")
    
    capacidad_result = st.session_state['capacidad_result']
    parametros = st.session_state['parametros']
    
    # Mostrar métricas según si incluye tapas o no
    if capacidad_result.get('incluye_tapas', True):
        col_cap1, col_cap2, col_cap3, col_cap4 = st.columns(4)
        
        with col_cap1:
            st.metric("Volumen Total", f"{capacidad_result['volumen_total_litros']:.2f} L")
        
        with col_cap2:
            st.metric("Volumen Total", f"{capacidad_result['volumen_total_m3']:.4f} m³")
        
        with col_cap3:
            st.metric("Volumen Cuerpo", f"{capacidad_result['volumen_cuerpo_litros']:.2f} L")
        
        with col_cap4:
            st.metric("Volumen Tapas", f"{capacidad_result['volumen_tapas_litros']:.2f} L")
        
        # Métricas adicionales
        col_cap5, col_cap6, col_cap7 = st.columns(3)
        
        with col_cap5:
            st.metric("Diámetro Interno", f"{capacidad_result['diametro_interno_mm']:.2f} mm")
        
        with col_cap6:
            st.metric("Radio Interno", f"{capacidad_result['radio_interno_mm']:.2f} mm")
        
        with col_cap7:
            st.metric("Longitud Cuerpo", f"{capacidad_result['longitud_cuerpo_mm']:.2f} mm")
    else:
        col_cap1, col_cap2, col_cap3, col_cap4 = st.columns(4)
        
        with col_cap1:
            st.metric("Volumen Interno", f"{capacidad_result['volumen_cuerpo_litros']:.2f} L")
        
        with col_cap2:
            st.metric("Volumen Interno", f"{capacidad_result['volumen_total_m3']:.4f} m³")
        
        with col_cap3:
            st.metric("Diámetro Interno", f"{capacidad_result['diametro_interno_mm']:.2f} mm")
        
        with col_cap4:
            st.metric("Radio Interno", f"{capacidad_result['radio_interno_mm']:.2f} mm")
    
    # Fórmula de capacidad
    with st.expander("📐 Fórmula de Capacidad"):
        if capacidad_result.get('incluye_tapas', True):
            st.latex(r"""
            \begin{align}
            D_i &= D_e - 2 \times t \\
            r_i &= \frac{D_i}{2} \\
            L_{cuerpo} &= L_{total} - 2 \times r_i \\
            V_{cuerpo} &= \pi \times r_i^2 \times L_{cuerpo} \\
            V_{tapas} &= \frac{4}{3} \times \pi \times r_i^3 \\
            V_{total} &= V_{cuerpo} + V_{tapas}
            \end{align}
            """)
            st.markdown("""
            Donde:
            - $D_e$ = Diámetro exterior (mm)
            - $D_i$ = Diámetro interior (mm)
            - $t$ = Espesor de pared (mm)
            - $r_i$ = Radio interior (mm)
            - $L_{total}$ = Longitud total del cilindro (mm)
            - $L_{cuerpo}$ = Longitud del cuerpo cilíndrico (sin tapas) (mm)
            - $V_{cuerpo}$ = Volumen del cuerpo cilíndrico (mm³)
            - $V_{tapas}$ = Volumen de las dos tapas semiesféricas (mm³)
            - $V_{total}$ = Volumen total interno (mm³)
            
            **Nota:** Las tapas semiesféricas tienen cada una una altura igual al radio interno.
            """)
        else:
            st.latex(r"""
            \begin{align}
            D_i &= D_e - 2 \times t \\
            r_i &= \frac{D_i}{2} \\
            V &= \pi \times r_i^2 \times L
            \end{align}
            """)
            st.markdown("""
            Donde:
            - $D_e$ = Diámetro exterior (mm)
            - $D_i$ = Diámetro interior (mm)
            - $t$ = Espesor de pared (mm)
            - $r_i$ = Radio interior (mm)
            - $L$ = Longitud del cilindro (mm)
            - $V$ = Volumen interno (mm³)
            
            **Nota:** Solo se calcula el volumen del cuerpo cilíndrico, sin incluir tapas.
            """)
    
    # Sección de espesor
    st.markdown("---")
    st.header("🛡️ Espesor Requerido")
    
    espesor_result = st.session_state['espesor_result']
    norma_usada = st.session_state['norma_usada']
    
    col_esp1, col_esp2, col_esp3 = st.columns(3)
    
    with col_esp1:
        st.metric(
            "Espesor Mínimo",
            f"{espesor_result['espesor_minimo_mm']:.2f} mm"
        )
    
    with col_esp2:
        st.metric(
            "Espesor con Tolerancia",
            f"{espesor_result['espesor_con_tolerancia_mm']:.2f} mm",
            help="Incluye 15% de tolerancia de fabricación"
        )
    
    with col_esp3:
        st.metric(
            "Espesor Actual",
            f"{parametros['espesor_actual']:.2f} mm"
        )
    
    # Fórmula según norma
    with st.expander(f"📐 Fórmula según {norma_usada}"):
        if norma_usada == "ISO 11439 / NTC 3847":
            st.latex(r"""
            e = \frac{D \times P_h}{2 \times R_e + 0.4 \times P_h}
            """)
            st.markdown("""
            Donde:
            - $e$ = Espesor mínimo de la pared (mm)
            - $D$ = Diámetro exterior del cilindro (mm)
            - $P_h$ = Presión de prueba hidráulica (MPa)
            - $R_e$ = Límite elástico del material (MPa)
            
            **Referencia:** ISO 11439:2013 / NTC 3847:2002
            """)
            
            st.markdown("**Valores utilizados:**")
            st.write(f"- Diámetro exterior (D): {parametros['diametro_exterior']:.2f} mm")
            st.write(f"- Presión de prueba (P_h): {espesor_result['presion_prueba_mpa']:.2f} MPa ({parametros['presion_prueba']:.0f} bar)")
            st.write(f"- Límite elástico (R_e): {material_props['limite_elastico_mpa']:.0f} MPa")
        
        else:  # ASME
            st.latex(r"""
            t = \frac{P \times R}{S \times E - 0.6 \times P}
            """)
            st.markdown("""
            Donde:
            - $t$ = Espesor mínimo requerido (mm)
            - $P$ = Presión de diseño (MPa)
            - $R$ = Radio interior del cilindro (mm)
            - $S$ = Esfuerzo máximo admisible del material (MPa)
            - $E$ = Eficiencia de la junta (1.0 para sin costura)
            
            **Condición de validez:** $P \leq 0.385 \times S \times E$
            
            **Referencia:** ASME Section VIII, Division 1
            """)
            
            st.markdown("**Valores utilizados:**")
            st.write(f"- Radio interior (R): {capacidad_result['radio_interno_mm']:.2f} mm")
            st.write(f"- Presión de diseño (P): {espesor_result['presion_diseno_mpa']:.2f} MPa ({parametros['presion_trabajo']:.0f} bar)")
            st.write(f"- Esfuerzo admisible (S): {material_props['esfuerzo_admisible_asme_mpa']:.0f} MPa")
            st.write(f"- Eficiencia de junta (E): 1.0 (sin costura)")
            
            if 'condicion_validez' in espesor_result:
                if espesor_result['condicion_validez']:
                    st.success(f"✅ Condición de validez cumplida: P ({espesor_result['presion_diseno_mpa']:.2f} MPa) ≤ {espesor_result['limite_presion_mpa']:.2f} MPa")
                else:
                    st.error(f"❌ Condición de validez no cumplida")
    
    # Validación
    st.markdown("---")
    st.header("✅ Validación del Espesor")
    
    validacion = st.session_state['validacion']
    
    # Mostrar estado con color
    if validacion['es_valido']:
        if "Marginal" in validacion['estado']:
            st.warning(validacion['mensaje'])
        else:
            st.success(validacion['mensaje'])
    else:
        st.error(validacion['mensaje'])
    
    col_val1, col_val2, col_val3 = st.columns(3)
    
    with col_val1:
        st.metric(
            "Factor de Seguridad",
            f"{validacion['factor_seguridad']:.2f}",
            help="Factor de seguridad mínimo requerido: 2.25"
        )
    
    with col_val2:
        st.metric(
            "Diferencia",
            f"{validacion['diferencia_mm']:.2f} mm",
            delta=f"{validacion['porcentaje_margen']:.1f}%",
            delta_color="normal" if validacion['es_valido'] else "inverse"
        )
    
    with col_val3:
        margen_texto = f"{validacion['porcentaje_margen']:.1f}%"
        if validacion['porcentaje_margen'] < 0:
            margen_texto = f"-{abs(validacion['porcentaje_margen']):.1f}%"
        st.metric(
            "Margen",
            margen_texto
        )
    
    # Advertencias y recomendaciones
    st.markdown("---")
    st.header("⚠️ Advertencias y Recomendaciones")
    
    advertencias = []
    
    # Verificar factor de seguridad
    if validacion['factor_seguridad'] < 2.25:
        advertencias.append("❌ **Factor de seguridad insuficiente**: El factor de seguridad calculado es menor al mínimo requerido (2.25 según NTC 3847)")
    
    # Verificar margen
    if validacion['porcentaje_margen'] < 10:
        advertencias.append("⚠️ **Margen bajo**: Se recomienda un margen mínimo del 10% sobre el espesor requerido")
    
    # Verificar tolerancia de fabricación
    if parametros['espesor_actual'] < espesor_result['espesor_con_tolerancia_mm']:
        advertencias.append("⚠️ **Tolerancia de fabricación**: El espesor actual es menor que el espesor requerido con tolerancia de fabricación (15%)")
    
    # Verificar rangos típicos
    if parametros['espesor_actual'] < 5.0 or parametros['espesor_actual'] > 10.0:
        advertencias.append("ℹ️ **Rango atípico**: El espesor está fuera del rango típico para cilindros GNV (5-8 mm para Tipo 1)")
    
    if advertencias:
        for advertencia in advertencias:
            st.markdown(advertencia)
    else:
        st.success("✅ No se detectaron problemas. El diseño cumple con todos los requisitos.")
    
    # Referencias normativas
    st.markdown("---")
    st.header("📚 Referencias Normativas")
    
    st.markdown("""
    ### ISO 11439 / NTC 3847
    - **ISO 11439:2013**: Gas cylinders — High pressure cylinders for the on-board storage of natural gas as a fuel for automotive vehicles
    - **NTC 3847:2002**: Cilindros de alta presión para almacenamiento de GNC para vehículos (equivalente a ISO 11439:2000)
    - **Factor de seguridad mínimo**: 2.25
    - **Presión de prueba**: 1.5 × Presión de trabajo
    
    ### ASME Section VIII, Division 1
    - **ASME Boiler and Pressure Vessel Code, Section VIII, Division 1**: Rules for Construction of Pressure Vessels
    - **Condición de validez**: P ≤ 0.385 × S × E
    - **Eficiencia de junta**: E = 1.0 para cilindros sin costura
    
    ### Materiales
    - Los materiales especificados (34CrMo4, 30CrMo, 35CrMo) son aceros aleados de alta resistencia
    - Propiedades basadas en especificaciones estándar de la industria
    - Tratamiento térmico: Temple y revenido
    """)
    
    # Exportación de resultados
    st.markdown("---")
    st.header("💾 Exportar Resultados")
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        if st.button("📄 Generar Informe HTML", type="primary", use_container_width=True):
            try:
                # Generar informe HTML profesional
                html_informe = generar_informe_html_tanques(
                    capacidad_result=capacidad_result,
                    espesor_result=espesor_result,
                    validacion=validacion,
                    norma_usada=norma_usada,
                    parametros=parametros,
                    material_props=material_props,
                    incluye_tapas=st.session_state.get('incluye_tapas', True)
                )
                
                # Nombre del archivo
                nombre_archivo = f"informe_tanque_gnv_{parametros['diametro_exterior']:.0f}mm_{parametros['longitud']:.0f}mm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                
                st.download_button(
                    label="⬇️ Descargar Informe HTML",
                    data=html_informe,
                    file_name=nombre_archivo,
                    mime="text/html",
                    use_container_width=True
                )
                
                st.success("✅ Informe HTML generado exitosamente!")
                st.info("💡 **Tip:** Descargue el HTML y conviértalo a PDF usando su navegador (Archivo > Imprimir > Guardar como PDF)")
                
            except Exception as e:
                st.error(f"❌ Error al generar informe HTML: {str(e)}")
    
    with col_export2:
        if st.button("📝 Generar Reporte Texto", use_container_width=True):
            try:
                reporte = f"""# Reporte de Cálculo - Tanque GNV

## Parámetros de Entrada
- Diámetro Exterior: {parametros['diametro_exterior']:.2f} mm
- Longitud: {parametros['longitud']:.2f} mm
- Espesor Actual: {parametros['espesor_actual']:.2f} mm
- Presión de Trabajo: {parametros['presion_trabajo']:.0f} bar
- Presión de Prueba: {parametros['presion_prueba']:.0f} bar
- Material: {material_props['nombre']}
- Norma: {norma_usada}
- Incluir Tapas Semiesféricas: {'Sí' if st.session_state.get('incluye_tapas', True) else 'No'}

## Resultados

### Capacidad"""
                
                if capacidad_result.get('incluye_tapas', True):
                    reporte += f"""
- Volumen Total: {capacidad_result['volumen_total_litros']:.2f} L ({capacidad_result['volumen_total_m3']:.4f} m³)
- Volumen Cuerpo: {capacidad_result['volumen_cuerpo_litros']:.2f} L
- Volumen Tapas: {capacidad_result['volumen_tapas_litros']:.2f} L
- Diámetro Interno: {capacidad_result['diametro_interno_mm']:.2f} mm
- Radio Interno: {capacidad_result['radio_interno_mm']:.2f} mm
- Longitud Cuerpo: {capacidad_result['longitud_cuerpo_mm']:.2f} mm"""
                else:
                    reporte += f"""
- Volumen Interno: {capacidad_result['volumen_cuerpo_litros']:.2f} L ({capacidad_result['volumen_total_m3']:.4f} m³)
- Diámetro Interno: {capacidad_result['diametro_interno_mm']:.2f} mm
- Radio Interno: {capacidad_result['radio_interno_mm']:.2f} mm"""
                
                reporte += f"""

### Espesor Requerido
- Espesor Mínimo: {espesor_result['espesor_minimo_mm']:.2f} mm
- Espesor con Tolerancia: {espesor_result['espesor_con_tolerancia_mm']:.2f} mm

### Validación
- Estado: {validacion['estado']}
- Factor de Seguridad: {validacion['factor_seguridad']:.2f}
- Diferencia: {validacion['diferencia_mm']:.2f} mm ({validacion['porcentaje_margen']:.1f}%)

## Conclusión
{validacion['mensaje']}

---
Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
WELDTECH SOLUTIONS - Calculadora de Tanques GNV
"""
                
                st.download_button(
                    label="⬇️ Descargar Reporte TXT",
                    data=reporte,
                    file_name=f"reporte_tanque_gnv_{parametros['diametro_exterior']:.0f}mm_{parametros['longitud']:.0f}mm.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error al generar reporte de texto: {str(e)}")

else:
    # Mensaje inicial
    st.info("👈 Configure los parámetros en la barra lateral y haga clic en 'Calcular' para comenzar.")
    
    st.markdown("""
    ### Características de la Calculadora
    
    Esta herramienta permite:
    
    - ✅ **Cálculo de Capacidad**: Determina el volumen interno del cilindro basado en dimensiones físicas
    - ✅ **Cálculo de Espesor**: Calcula el espesor mínimo requerido según normas internacionales
    - ✅ **Validación**: Compara el espesor actual con el requerido
    - ✅ **Múltiples Normas**: Soporta ISO 11439 y ASME Section VIII
    - ✅ **Materiales Predefinidos**: Incluye propiedades de aceros comunes para GNV
    
    ### Parámetros por Defecto
    
    Los valores por defecto están basados en especificaciones típicas de la industria:
    - Diámetro: 356 mm (cilindro de 65L)
    - Longitud: 1000 mm
    - Espesor: 7.2 mm
    - Presión: 200 bar (estándar Colombia)
    - Material: 34CrMo4 (más común)
    """)

