"""
Integración del agente draw.io con la aplicación Streamlit
"""
import streamlit as st
from utils.drawio_agent import DrawIOAgent
from config import DELIVERABLE_XML, DELIVERABLE_MD

def show_diagram_generator(calculation_results: dict, client_name: str = "PETROLIQUIDOS"):
    """
    Muestra la interfaz para generar/actualizar diagramas draw.io
    
    Args:
        calculation_results: Resultados del cálculo del sistema
        client_name: Nombre del cliente
    """
    st.subheader("📊 Generador de Diagrama P&ID")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        generate_btn = st.button("🔄 Generar Diagrama Actualizado", use_container_width=True, type="primary")
    
    with col2:
        view_vars_btn = st.button("📋 Ver Variables", use_container_width=True)
    
    with col3:
        download_btn = st.button("📥 Descargar Diagrama", use_container_width=True)
    
    if generate_btn:
        try:
            with st.spinner("Generando diagrama P&ID..."):
                agent = DrawIOAgent(output_path=DELIVERABLE_XML)
                
                # Intentar cargar instrucciones de ingeniería
                doc_path = DELIVERABLE_MD if hasattr(st, 'session_state') and 'proyecto_cliente' in st.session_state else None
                
                xml_content = agent.generate_diagram_from_engineering(
                    calculation_results,
                    client_name,
                    doc_path=doc_path
                )
                
                agent.save_diagram(xml_content)
                
                st.success(f"✅ Diagrama generado exitosamente!")
                st.info(f"📁 Ubicación: `{DELIVERABLE_XML}`")
                
                # Guardar en session_state para descarga
                st.session_state['diagram_xml'] = xml_content
                st.session_state['diagram_generated'] = True
                
        except Exception as e:
            st.error(f"❌ Error al generar diagrama: {str(e)}")
            st.exception(e)
    
    if view_vars_btn:
        try:
            agent = DrawIOAgent()
            agent.load_calculation_variables(calculation_results)
            
            st.subheader("Variables del Diagrama")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Parámetros del Sistema:**")
                st.json({
                    'Número de tanques': agent.variables.get('numero_tanques'),
                    'Presión de llenado': f"{agent.variables.get('presion_llenado', 0):.0f} bar",
                    'Volumen por tanque': f"{agent.variables.get('volumen_tanque_litros', 0):.0f} L",
                    'Temperatura operación': f"{agent.variables.get('temperatura_operacion', 0):.1f} °C"
                })
            
            with col2:
                st.write("**Rangos de Presión:**")
                st.json({
                    'Alta presión': f"{agent.variables.get('presion_etapa1_in', 0):.0f}-{agent.variables.get('presion_llenado_max', 0):.0f} bar",
                    'Media presión': f"{agent.variables.get('presion_etapa1_out', 0)-10:.0f}-{agent.variables.get('presion_etapa1_out', 0)+10:.0f} bar",
                    'Baja presión': f"{agent.variables.get('presion_etapa2_out', 0)-1.5:.1f}-{agent.variables.get('presion_etapa2_out', 0)+1.5:.1f} bar"
                })
            
            st.write("**Variables de Cálculo:**")
            st.json({
                'Volumen total de gas': f"{agent.variables.get('volumen_gas_total', 0):.2f} m³",
                'Masa CH₄ requerida': f"{agent.variables.get('masa_ch4', 0):.2f} kg",
                'Energía requerida': f"{agent.variables.get('energia_requerida', 0):.2f} MJ",
                'Consumo diésel': f"{agent.variables.get('consumo_diesel', 0):.1f} L/100km",
                'Autonomía objetivo': f"{agent.variables.get('autonomia', 0):.0f} km"
            })
            
        except Exception as e:
            st.error(f"❌ Error al cargar variables: {str(e)}")
    
    if download_btn:
        if 'diagram_xml' in st.session_state and st.session_state.get('diagram_generated'):
            xml_content = st.session_state['diagram_xml']
            filename = f"diagrama_gnv_{client_name}_{st.session_state.get('proyecto_fecha', 'v1')}.drawio.xml"
            
            st.download_button(
                label="📥 Descargar Diagrama (.drawio.xml)",
                data=xml_content,
                file_name=filename,
                mime="application/xml",
                use_container_width=True
            )
        else:
            st.warning("⚠️ Primero debe generar el diagrama antes de descargarlo.")
    
    # Información adicional
    st.markdown("---")
    st.info("""
    💡 **Información del Diagrama:**
    - El diagrama incluye todos los componentes del sistema GNV con las variables calculadas del proyecto
    - Puede abrirse y editarse en [draw.io](https://app.diagrams.net) o [diagrams.net](https://diagrams.net)
    - Las presiones y variables se actualizan automáticamente según los cálculos realizados
    - El diagrama cumple con las especificaciones de la fase de ingeniería
    """)

