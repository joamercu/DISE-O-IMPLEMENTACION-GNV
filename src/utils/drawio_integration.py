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
    
    # Validar requisitos antes de mostrar botones
    if not calculation_results or not isinstance(calculation_results, dict):
        missing_keys = ['volumen', 'tanques', 'presion_llenado', 'temperatura']
        calculation_results = {}  # Inicializar como diccionario vacío para evitar errores
    else:
        required_keys = ['volumen', 'tanques', 'presion_llenado', 'temperatura']
        missing_keys = [key for key in required_keys if key not in calculation_results or calculation_results.get(key) is None]
    
    if missing_keys:
        st.warning(f"""
        ⚠️ **Datos incompletos para generar el diagrama**
        
        **Faltan los siguientes datos:**
        {', '.join([f'`{key}`' for key in missing_keys])}
        
        **Requisitos para generar el diagrama:**
        - ✅ Realizar un cálculo del sistema GNV primero
        - ✅ Asegurarse de que todos los parámetros estén completos
        - ✅ Verificar que los resultados del cálculo estén disponibles
        
        **Solución:** Vaya a la pestaña "📊 Cálculo del Sistema" y ejecute el cálculo antes de generar el diagrama.
        """)
    else:
        st.success("✅ **Datos completos** - Puede generar el diagrama P&ID con los resultados del cálculo.")
    
    # Inicializar estados en session_state
    if 'diagram_action' not in st.session_state:
        st.session_state['diagram_action'] = None
    if 'diagram_expander_open' not in st.session_state:
        st.session_state['diagram_expander_open'] = True  # Abrir por defecto si hay resultados
    
    # Asegurar que el expander esté abierto si hay resultados
    if calculation_results and bool(calculation_results):
        st.session_state['diagram_expander_open'] = True
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        generate_btn = st.button(
            "🔄 Generar Diagrama Actualizado", 
            width='stretch', 
            type="primary", 
            disabled=bool(missing_keys),
            key="btn_generate_diagram"
        )
        # Establecer estado inmediatamente cuando se hace clic
        if generate_btn:
            st.session_state['diagram_action'] = 'generate'
            st.session_state['diagram_expander_open'] = True
    
    with col2:
        view_vars_btn = st.button(
            "📋 Ver Variables", 
            width='stretch', 
            disabled=bool(missing_keys),
            key="btn_view_vars"
        )
        # Establecer estado inmediatamente cuando se hace clic
        if view_vars_btn:
            st.session_state['diagram_action'] = 'view_vars'
            st.session_state['diagram_expander_open'] = True
    
    with col3:
        download_btn = st.button(
            "📥 Descargar Diagrama", 
            width='stretch',
            key="btn_download_diagram"
        )
        # Establecer estado inmediatamente cuando se hace clic
        if download_btn:
            st.session_state['diagram_action'] = 'download'
            st.session_state['diagram_expander_open'] = True
    
    # Ejecutar acciones basadas en session_state
    if st.session_state.get('diagram_action') == 'generate':
        try:
            # Mostrar información sobre el proceso
            st.info("🔄 **Iniciando generación del diagrama P&ID...**")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Paso 1: Inicializar agente
            status_text.text("📋 Paso 1/5: Inicializando agente de diagramas...")
            progress_bar.progress(20)
            agent = DrawIOAgent(output_path=DELIVERABLE_XML)
            
            # Paso 2: Verificar instrucciones de ingeniería
            status_text.text("📄 Paso 2/5: Verificando instrucciones de ingeniería...")
            progress_bar.progress(40)
            doc_path = DELIVERABLE_MD if hasattr(st, 'session_state') and 'proyecto_cliente' in st.session_state else None
            if doc_path:
                st.info("ℹ️ Se encontraron instrucciones de ingeniería. El diagrama se generará según estas especificaciones.")
            else:
                st.warning("⚠️ No se encontraron instrucciones de ingeniería. El diagrama se generará con la configuración estándar.")
            
            # Paso 3: Generar diagrama
            status_text.text("⚙️ Paso 3/5: Generando componentes y conexiones del diagrama...")
            progress_bar.progress(60)
            xml_content = agent.generate_diagram_from_engineering(
                calculation_results,
                client_name,
                doc_path=doc_path
            )
            
            # Paso 4: Guardar diagrama
            status_text.text("💾 Paso 4/5: Guardando diagrama en archivo...")
            progress_bar.progress(80)
            agent.save_diagram(xml_content)
            
            # Paso 5: Finalizar
            status_text.text("✅ Paso 5/5: Proceso completado exitosamente!")
            progress_bar.progress(100)
            
            # Limpiar indicadores de progreso
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"✅ **Diagrama generado exitosamente!**")
            st.info(f"📁 **Ubicación del archivo:** `{DELIVERABLE_XML}`")
            st.success("💡 **Próximos pasos:** Puede ver las variables del diagrama o descargarlo usando los botones de arriba.")
            
            # Guardar en session_state para descarga
            st.session_state['diagram_xml'] = xml_content
            st.session_state['diagram_generated'] = True
            # Mantener el expander abierto después de generar
            st.session_state['diagram_expander_open'] = True
            # Mantener la acción para que el expander se mantenga abierto
            # No limpiar la acción para mantener el expander abierto
                
        except Exception as e:
            st.error(f"❌ **Error al generar diagrama**")
            st.error(f"**Detalles del error:** {str(e)}")
            st.warning("💡 **Sugerencias para resolver el problema:**")
            st.markdown("""
            - Verifique que todos los datos del cálculo estén completos
            - Asegúrese de que los resultados del cálculo sean válidos
            - Revise que el archivo de instrucciones de ingeniería (si existe) esté en el formato correcto
            - Intente generar el diagrama nuevamente después de verificar los datos
            """)
            st.exception(e)
            # Mantener el expander abierto incluso si hay error
            st.session_state['diagram_expander_open'] = True
    
    if st.session_state.get('diagram_action') == 'view_vars':
        try:
            st.info("📋 **Cargando variables del diagrama...**")
            agent = DrawIOAgent()
            agent.load_calculation_variables(calculation_results)
            
            st.success("✅ **Variables cargadas exitosamente**")
            st.subheader("📊 Variables del Diagrama")
            st.markdown("""
            **ℹ️ Estas son las variables que se utilizarán en el diagrama P&ID.**
            Puede revisar estos valores antes de generar el diagrama para asegurarse de que sean correctos.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🔧 Parámetros del Sistema:**")
                st.json({
                    'Número de tanques': agent.variables.get('numero_tanques'),
                    'Presión de llenado': f"{agent.variables.get('presion_llenado', 0):.0f} bar",
                    'Volumen por tanque': f"{agent.variables.get('volumen_tanque_litros', 0):.0f} L",
                    'Temperatura operación': f"{agent.variables.get('temperatura_operacion', 0):.1f} °C"
                })
            
            with col2:
                st.write("**📈 Rangos de Presión:**")
                st.json({
                    'Alta presión': f"{agent.variables.get('presion_etapa1_in', 0):.0f}-{agent.variables.get('presion_llenado_max', 0):.0f} bar",
                    'Media presión': f"{agent.variables.get('presion_etapa1_out', 0)-10:.0f}-{agent.variables.get('presion_etapa1_out', 0)+10:.0f} bar",
                    'Baja presión': f"{agent.variables.get('presion_etapa2_out', 0)-1.5:.1f}-{agent.variables.get('presion_etapa2_out', 0)+1.5:.1f} bar"
                })
            
            st.write("**⚡ Variables de Cálculo:**")
            st.json({
                'Volumen total de gas': f"{agent.variables.get('volumen_gas_total', 0):.2f} m³",
                'Masa CH₄ requerida': f"{agent.variables.get('masa_ch4', 0):.2f} kg",
                'Energía requerida': f"{agent.variables.get('energia_requerida', 0):.2f} MJ",
                'Consumo diésel': f"{agent.variables.get('consumo_diesel', 0):.1f} L/100km",
                'Autonomía objetivo': f"{agent.variables.get('autonomia', 0):.0f} km"
            })
            
            st.info("💡 **Nota:** Si necesita modificar estos valores, actualice los parámetros en la pestaña de cálculo y vuelva a ejecutar el cálculo.")
            
            # Mantener el expander abierto
            st.session_state['diagram_expander_open'] = True
            
        except Exception as e:
            st.error(f"❌ **Error al cargar variables**")
            st.error(f"**Detalles:** {str(e)}")
            st.warning("💡 **Sugerencias:** Verifique que los resultados del cálculo estén completos y sean válidos.")
            # Mantener el expander abierto incluso si hay error
            st.session_state['diagram_expander_open'] = True
    
    if st.session_state.get('diagram_action') == 'download':
        if 'diagram_xml' in st.session_state and st.session_state.get('diagram_generated'):
            xml_content = st.session_state['diagram_xml']
            filename = f"diagrama_gnv_{client_name}_{st.session_state.get('proyecto_fecha', 'v1')}.drawio.xml"
            
            st.success("✅ **Diagrama disponible para descarga**")
            st.info("💡 **Instrucciones:** Haga clic en el botón de abajo para descargar el archivo. Puede abrirlo en [draw.io](https://app.diagrams.net) o [diagrams.net](https://diagrams.net)")
            
            st.download_button(
                label="📥 Descargar Diagrama (.drawio.xml)",
                data=xml_content,
                file_name=filename,
                mime="application/xml",
                width='stretch'
            )
        else:
            st.warning("""
            ⚠️ **Diagrama no disponible para descarga**
            
            **Razón:** El diagrama aún no ha sido generado.
            
            **Pasos para descargar:**
            1. ✅ Asegúrese de haber completado el cálculo del sistema
            2. 🔄 Haga clic en "🔄 Generar Diagrama Actualizado"
            3. ⏳ Espere a que se complete la generación
            4. 📥 Luego podrá descargar el diagrama
            
            **Nota:** El diagrama se genera automáticamente con las variables de los cálculos realizados.
            """)
            # Mantener el expander abierto
            st.session_state['diagram_expander_open'] = True
    
    # Información adicional
    st.markdown("---")
    st.info("""
    💡 **Información del Diagrama:**
    - El diagrama incluye todos los componentes del sistema GNV con las variables calculadas del proyecto
    - Puede abrirse y editarse en [draw.io](https://app.diagrams.net) o [diagrams.net](https://diagrams.net)
    - Las presiones y variables se actualizan automáticamente según los cálculos realizados
    - El diagrama cumple con las especificaciones de la fase de ingeniería
    """)

