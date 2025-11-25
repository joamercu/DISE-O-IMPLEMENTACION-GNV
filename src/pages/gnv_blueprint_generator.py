"""
Página Streamlit: Generador de Planos Técnicos GNV

Interfaz de usuario para generar planos técnicos de sistemas GNV
con diagramas esquemáticos y vistas 2D.

Autor: Sistema de Diseño GNV
Fecha: 2025-01-19
"""

import streamlit as st
import numpy as np
from typing import Dict, Optional
from datetime import datetime

# Importar módulos del sistema
import sys
import os
from pathlib import Path

# Agregar src al path para imports (consistente con calculos_combustible_vehicular.py)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gnv_layout_generator import (
    GNVLayoutGenerator,
    TruckSpecs,
    CylinderSpecs
)
from utils.gnv_blueprint_renderer import GNVBlueprintRenderer
from utils.gnv_pdf_generator import GNVPDFGenerator
from utils.gnv_layout_model import GNVLayoutModel
import matplotlib.pyplot as plt


# Configuración de la página
st.set_page_config(
    page_title="Generador de Planos GNV",
    page_icon="📐",
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

st.title("📐 Generador de Planos Técnicos GNV")
st.markdown("---")

# Sidebar para parámetros de entrada
with st.sidebar:
    st.header("⚙️ Parámetros de Configuración")
    
    # Número de cilindros
    num_cylinders = st.number_input(
        "Número de Cilindros",
        min_value=1,
        max_value=50,
        value=18,
        help="Número total de cilindros GNV a disponer"
    )
    
    st.subheader("Especificaciones de Cilindros")
    
    cylinder_volume = st.number_input(
        "Volumen Unitario (L)",
        min_value=20.0,
        max_value=200.0,
        value=80.0,
        step=5.0,
        help="Volumen de cada cilindro en litros"
    )
    
    cylinder_diameter = st.number_input(
        "Diámetro (mm)",
        min_value=200.0,
        max_value=500.0,
        value=320.0,
        step=10.0,
        help="Diámetro exterior del cilindro en milímetros"
    )
    
    cylinder_length = st.number_input(
        "Longitud (mm)",
        min_value=500.0,
        max_value=2000.0,
        value=1000.0,
        step=50.0,
        help="Longitud del cilindro en milímetros"
    )
    
    cylinder_pressure = st.number_input(
        "Presión de Operación (bar)",
        min_value=150.0,
        max_value=300.0,
        value=200.0,
        step=10.0,
        help="Presión de operación en bar"
    )
    
    st.subheader("Especificaciones del Camión")
    
    truck_width = st.number_input(
        "Ancho Útil del Chasis (mm)",
        min_value=1500.0,
        max_value=3000.0,
        value=2400.0,
        step=100.0,
        help="Ancho disponible para montaje de cilindros"
    )
    
    truck_length = st.number_input(
        "Largo Disponible (mm)",
        min_value=3000.0,
        max_value=10000.0,
        value=6000.0,
        step=500.0,
        help="Largo disponible para montaje de cilindros"
    )
    
    truck_height = st.number_input(
        "Altura Disponible (mm)",
        min_value=500.0,
        max_value=1500.0,
        value=800.0,
        step=50.0,
        help="Altura disponible para montaje de cilindros"
    )
    
    clearance = st.number_input(
        "Espacio Mínimo entre Cilindros (mm)",
        min_value=20.0,
        max_value=200.0,
        value=50.0,
        step=10.0,
        help="Espacio mínimo requerido entre cilindros para mantenimiento"
    )
    
    st.subheader("Opciones de Disposición")
    
    use_backup = st.checkbox(
        "Usar Módulo de Respaldo",
        value=True,
        help="Genera un módulo principal y un módulo de respaldo"
    )
    
    # Información del proyecto
    st.subheader("Información del Proyecto")
    
    project_name = st.text_input(
        "Nombre del Proyecto",
        value="Sistema GNV",
        help="Nombre identificador del proyecto"
    )
    
    client_name = st.text_input(
        "Nombre del Cliente",
        value="Cliente",
        help="Nombre del cliente"
    )

# Contenido principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Visualización del Plano")
    
    # Botón para generar
    if st.button("🔄 Generar Plano", type="primary", use_container_width=True):
        with st.spinner("Generando disposición y planos..."):
            try:
                # Crear especificaciones
                truck_specs = TruckSpecs(
                    chassis_width_mm=truck_width,
                    chassis_length_mm=truck_length,
                    chassis_height_mm=truck_height,
                    clearance_mm=clearance
                )
                
                cylinder_specs = CylinderSpecs(
                    volume_liters=cylinder_volume,
                    diameter_mm=cylinder_diameter,
                    length_mm=cylinder_length,
                    pressure_bar=cylinder_pressure
                )
                
                # Generar disposición
                generator = GNVLayoutGenerator(
                    num_cylinders=num_cylinders,
                    truck_specs=truck_specs,
                    cylinder_specs=cylinder_specs
                )
                
                layout_data = generator.generate_complete_layout(use_backup=use_backup)
                
                # Guardar en session state
                st.session_state['layout_data'] = layout_data
                st.session_state['truck_specs'] = truck_specs
                st.session_state['cylinder_specs'] = cylinder_specs
                st.session_state['project_name'] = project_name
                st.session_state['client_name'] = client_name
                
                st.success("✅ Plano generado exitosamente!")
                
            except Exception as e:
                st.error(f"❌ Error generando plano: {str(e)}")
                st.exception(e)

with col2:
    st.header("ℹ️ Información")
    
    if 'layout_data' in st.session_state:
        layout_data = st.session_state['layout_data']
        
        st.metric("Cilindros", len(layout_data.get('tanks', [])))
        
        arrangement = layout_data.get('arrangement', {})
        if arrangement:
            st.metric("Filas", arrangement.get('rows', 'N/A'))
            st.metric("Por Fila", arrangement.get('cylinders_per_row', 'N/A'))
        
        is_valid = layout_data.get('is_valid', False)
        if is_valid:
            st.success("✅ Disposición válida")
        else:
            errors = layout_data.get('validation_errors', [])
            st.warning(f"⚠️ {len(errors)} advertencia(s)")
            if errors:
                with st.expander("Ver errores"):
                    for error in errors[:5]:  # Mostrar máximo 5
                        st.text(error)

# Mostrar visualizaciones si hay datos
if 'layout_data' in st.session_state:
    layout_data = st.session_state['layout_data']
    
    st.markdown("---")
    st.header("📐 Vistas del Plano")
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Diagrama Esquemático",
        "👁️ Vista Frontal",
        "👁️ Vista Lateral",
        "📄 Vista Completa"
    ])
    
    try:
        renderer = GNVBlueprintRenderer(layout_data)
        
        with tab1:
            st.subheader("Diagrama Esquemático - Vista Superior")
            fig = renderer.render_schematic_diagram()
            st.pyplot(fig)
            plt.close(fig)
        
        with tab2:
            st.subheader("Vista Frontal")
            fig = renderer.render_front_view()
            st.pyplot(fig)
            plt.close(fig)
        
        with tab3:
            st.subheader("Vista Lateral")
            fig = renderer.render_side_view()
            st.pyplot(fig)
            plt.close(fig)
        
        with tab4:
            st.subheader("Vista Completa")
            fig = renderer.render_all_views()
            st.pyplot(fig)
            plt.close(fig)
    
    except Exception as e:
        st.error(f"Error renderizando vistas: {str(e)}")
        st.exception(e)
    
    # Sección de descarga de PDF
    st.markdown("---")
    st.header("📥 Descargar Plano Técnico")
    
    col_download1, col_download2 = st.columns([3, 1])
    
    with col_download1:
        st.info("Genera un documento PDF técnico completo con todas las vistas, especificaciones y notas técnicas.")
    
    with col_download2:
        if st.button("📄 Generar y Descargar PDF", type="primary", use_container_width=True):
            with st.spinner("Generando PDF..."):
                try:
                    project_name = st.session_state.get('project_name', 'Sistema GNV')
                    client_name = st.session_state.get('client_name', 'Cliente')
                    
                    pdf_generator = GNVPDFGenerator(
                        layout_data=layout_data,
                        project_name=project_name,
                        client_name=client_name,
                        version="1.0"
                    )
                    
                    pdf_bytes, error = pdf_generator.generate_pdf()
                    
                    if error:
                        st.error(f"❌ Error generando PDF: {error}")
                    else:
                        # Nombre del archivo
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"plano_gnv_{client_name}_{timestamp}.pdf"
                        
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        st.success("✅ PDF generado exitosamente!")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)
    
    # Información técnica adicional
    with st.expander("📋 Información Técnica Detallada"):
        if layout_data.get('arrangement'):
            st.subheader("Disposición")
            st.json(layout_data['arrangement'])
        
        if layout_data.get('modules'):
            st.subheader("Módulos")
            st.json(layout_data['modules'])
        
        if layout_data.get('validation_errors'):
            st.subheader("Validación")
            st.write("Errores encontrados:")
            for error in layout_data['validation_errors']:
                st.text(f"• {error}")

else:
    # Mensaje inicial
    st.info("👈 Configure los parámetros en la barra lateral y haga clic en 'Generar Plano' para comenzar.")
    
    st.markdown("""
    ### Características del Generador de Planos
    
    Este módulo permite:
    
    - ✅ **Disposición Optimizada**: Organiza cilindros en módulos y filas optimizando el espacio
    - ✅ **Vistas Técnicas**: Genera diagramas esquemáticos, vistas frontal y lateral
    - ✅ **Validación Automática**: Verifica solapamientos y restricciones físicas
    - ✅ **Exportación PDF**: Genera documentos técnicos completos listos para impresión
    - ✅ **Parámetros Configurables**: Ajusta todas las especificaciones según necesidades
    
    ### Parámetros por Defecto
    
    Los valores por defecto están basados en especificaciones estándar de la industria:
    - Cilindros: 80L, 320mm diámetro, 1000mm longitud, 200 bar
    - Camión: 2400mm ancho, 6000mm largo, 800mm altura
    """)

