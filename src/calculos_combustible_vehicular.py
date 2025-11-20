"""
CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL
Aplicación Streamlit para cálculo de sistemas GNV/CNG
Basado en: PETROLIQUIDOS_GNV_Informe_v1
"""

import streamlit as st
import math
import pandas as pd
import json
import base64
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar src al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports de módulos propios
from auth_system import verify_user, create_user, get_user_role
from utils.auth_utils import load_remembered_user, save_remembered_user, clear_remembered_user
from utils.manifest_utils import load_manifest, save_manifest, generate_manifest_html
from utils.calculation_engine import calcular_sistema_gnv, calcular_sensibilidad
from utils.file_handler import get_file_mime_type, create_download_link, file_exists, generar_pdf_desde_html
from utils.documentos_utils import convertir_json_a_html, procesar_archivo_md
from utils.drawio_integration import show_diagram_generator
from config import (
    MANIFEST_FILE, REMEMBERED_USER_FILE, USERS_DB_FILE,
    DELIVERABLE_MD, DELIVERABLE_XLSX, DELIVERABLE_XML, DELIVERABLE_PDF,
    DEFAULT_CLIENT, DEFAULT_VERSION, DEFAULT_DATE, DEFAULT_AUTONOMIA,
    DEFAULT_PODER_CALORIFICO, DEFAULT_LHV_CH4, DEFAULT_EFICIENCIA,
    DEFAULT_PRESION, DEFAULT_TEMPERATURA, DEFAULT_FACTOR_Z,
    DEFAULT_VOLUMEN_TANQUE, DEFAULT_PESO_TANQUE,
    DEFAULT_PESO_SOPORTES, DEFAULT_PESO_ACCESORIOS,
    CONSTANTE_GASES, MASA_MOLAR_CH4
)

# Imports para sistema de notificaciones y seguimiento
try:
    from database import init_database, create_submission, add_calculos_to_submission, add_diagrama_to_submission
    from notifications import send_notifications
    from admin_panel import show_admin_panel
    NOTIFICATIONS_ENABLED = True
except ImportError as e:
    print(f"⚠️ Advertencia: Sistema de notificaciones no disponible: {e}")
    NOTIFICATIONS_ENABLED = False

# Configuración de la página
st.set_page_config(
    page_title="Cálculos Combustible Vehicular GNC/GNL",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# FUNCIÓN HELPER PARA LOGO WELDTECH SOLUTIONS
# ============================================
def show_weldtech_logo(size="medium", align="center"):
    """
    Muestra el logo de Weldtech Solutions usando HTML/CSS
    
    Args:
        size: "small", "medium", "large" - Tamaño del logo
        align: "left", "center", "right" - Alineación del logo
    """
    size_map = {
        "small": {"logo_width": "40px", "logo_height": "40px", "font_main": "18px", "font_sub": "12px"},
        "medium": {"logo_width": "60px", "logo_height": "60px", "font_main": "24px", "font_sub": "16px"},
        "large": {"logo_width": "80px", "logo_height": "80px", "font_main": "32px", "font_sub": "20px"}
    }
    
    sizes = size_map.get(size, size_map["medium"])
    
    logo_html = f"""
    <div style="display: flex; align-items: center; justify-content: {align}; gap: 12px; margin: 10px 0;">
        <svg width="{sizes['logo_width']}" height="{sizes['logo_height']}" viewBox="0 0 100 100" style="flex-shrink: 0;">
            <defs>
                <linearGradient id="weldtechGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#FF6B35;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#C73E1D;stop-opacity:1" />
                </linearGradient>
            </defs>
            <!-- Forma de W estilizada con picos angulares -->
            <path d="M 10 20 L 25 20 L 30 50 L 40 20 L 50 20 L 60 50 L 70 20 L 85 20 L 90 80 L 75 80 L 70 50 L 60 80 L 50 80 L 40 50 L 30 80 L 15 80 Z" 
                  fill="url(#weldtechGradient)" 
                  stroke="#FF6B35" 
                  stroke-width="1"/>
        </svg>
        <div style="display: flex; flex-direction: column; justify-content: center;">
            <div style="
                font-family: 'Arial', 'Helvetica', sans-serif;
                font-weight: bold;
                font-size: {sizes['font_main']};
                color: #FFFFFF;
                letter-spacing: 1.5px;
                line-height: 1.1;
                text-transform: uppercase;
            ">WELDTECH</div>
            <div style="
                font-family: 'Arial', 'Helvetica', sans-serif;
                font-size: {sizes['font_sub']};
                color: #CCCCCC;
                letter-spacing: 0.8px;
                margin-left: 4px;
                line-height: 1.1;
                text-transform: uppercase;
            ">SOLUTIONS</div>
        </div>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)

# ============================================
# SISTEMA DE AUTENTICACIÓN
# ============================================
# Las funciones load_remembered_user, save_remembered_user y clear_remembered_user
# están importadas desde utils.auth_utils

def show_login_page():
    """Muestra la página de inicio de sesión"""
    # Logo de Weldtech Solutions en la página de login
    col_logo_login = st.columns([1, 2, 1])
    with col_logo_login[1]:
        show_weldtech_logo(size="large", align="center")
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.title("🔐 Sistema de Autenticación")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.subheader("Iniciar Sesión")
            
            # Cargar usuario recordado si existe
            remembered_username, remembered_role = load_remembered_user()
            
            username = st.text_input(
                "👤 Nombre de Usuario", 
                value=remembered_username,
                placeholder="Ingrese su usuario"
            )
            password = st.text_input(
                "🔒 Contraseña", 
                type="password", 
                placeholder="Ingrese su contraseña"
            )
            role = st.selectbox(
                "👥 Rol", 
                ["Cliente", "Administrador"], 
                index=0 if remembered_role == 'Cliente' else 1,
                help="Seleccione su rol de usuario"
            )
            
            # Checkbox para recordar usuario
            remember_user = st.checkbox(
                "💾 Recordar usuario",
                value=bool(remembered_username),
                help="Guarda tu nombre de usuario para el próximo inicio de sesión (la contraseña NO se guarda por seguridad)"
            )
            
            submitted = st.form_submit_button("🚀 Iniciar Sesión")
            
            if submitted:
                if not username or not password:
                    st.error("⚠️ Por favor, complete todos los campos")
                else:
                    user = verify_user(username, password)
                    if user and user['role'] == role:
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        st.session_state['user_role'] = role
                        
                        # Guardar o eliminar usuario recordado según el checkbox
                        if remember_user:
                            save_remembered_user(username, role)
                        else:
                            clear_remembered_user()
                        
                        st.success(f"✅ Bienvenido, {username} ({role})")
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas o rol no coincide")
        
        # Mostrar opción para limpiar usuario recordado si existe
        if load_remembered_user()[0]:
            st.markdown("---")
            if st.button("🗑️ Olvidar usuario guardado", width='stretch'):
                clear_remembered_user()
                st.success("✅ Usuario recordado eliminado")
                st.rerun()

# Verificar autenticación
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    show_login_page()
    st.stop()

# Usuario autenticado - mostrar contenido principal
# Botón de cerrar sesión en el sidebar
with st.sidebar:
    # Logo de Weldtech Solutions en el sidebar
    show_weldtech_logo(size="small", align="center")
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", width='stretch'):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.session_state['user_role'] = None
        st.rerun()
    
    st.markdown(f"""
    **Usuario:** {st.session_state.get('username', 'N/A')}  
    **Rol:** {st.session_state.get('user_role', 'N/A')}
    """)

# Título principal con logo
col_logo, col_title = st.columns([1, 4])
with col_logo:
    show_weldtech_logo(size="medium", align="left")
with col_title:
    st.title("⛽ CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL")
st.markdown("---")

# Inicializar valores del proyecto en session_state si no existen
if 'proyecto_cliente' not in st.session_state:
    st.session_state['proyecto_cliente'] = DEFAULT_CLIENT
if 'proyecto_version' not in st.session_state:
    st.session_state['proyecto_version'] = DEFAULT_VERSION
if 'proyecto_fecha' not in st.session_state:
    st.session_state['proyecto_fecha'] = DEFAULT_DATE

# Sidebar con información del proyecto
with st.sidebar:
    st.header("📋 Información del Proyecto")
    
    # Campos editables para información del proyecto (solo Administrador)
    if st.session_state.get('user_role') == 'Administrador':
        with st.expander("⚙️ Editar Información del Proyecto", expanded=False):
            st.session_state['proyecto_cliente'] = st.text_input(
                "Cliente",
                value=st.session_state['proyecto_cliente'],
                help="Nombre del cliente o empresa"
            )
            st.session_state['proyecto_version'] = st.text_input(
                "Versión",
                value=st.session_state['proyecto_version'],
                help="Versión del proyecto o informe"
            )
            st.session_state['proyecto_fecha'] = st.text_input(
                "Fecha",
                value=st.session_state['proyecto_fecha'],
                help="Fecha del proyecto (formato: YYYY-MM-DD)"
            )
    else:
        # Cliente solo puede ver, no editar
        st.info("ℹ️ Solo los administradores pueden editar la información del proyecto")
    
    st.markdown(f"""
    **Cliente:** {st.session_state['proyecto_cliente']}  
    **Versión:** {st.session_state['proyecto_version']}  
    **Fecha:** {st.session_state['proyecto_fecha']}
    
    ---
    
    ### Relevancia del Proyecto
    
    Esta herramienta permite calcular los parámetros técnicos 
    necesarios para la conversión de vehículos pesados a Gas 
    Natural Vehicular (GNV/CNG), incluyendo:
    
    - Dimensionamiento de tanques
    - Cálculo de energía requerida
    - Estimación de peso adicional
    - Análisis de sensibilidad
    
    ---
    
    ### Parámetros por Defecto
    
    Los valores por defecto están basados en el informe técnico
    y pueden ser ajustados según necesidades específicas.
    """)

# ============================================
# FUNCIONES AUXILIARES PARA MANIFEST
# ============================================
# Las funciones load_manifest, save_manifest y generate_manifest_html
# están importadas desde utils.manifest_utils

# Tabs para organizar la aplicación
# Siempre crear los mismos tabs para evitar problemas de comparación de arrays
tabs_list = [
    "🔢 Cálculos Principales", 
    "👤 Datos del Cliente",
    "📐 Fórmulas y Procedimientos",
    "📊 Análisis de Sensibilidad",
    "📋 Manifest del Proyecto",
    "ℹ️ Información Técnica"
]

# Agregar tab de administración solo para administradores
if st.session_state.get('user_role') == 'Administrador' and NOTIFICATIONS_ENABLED:
    tabs_list.append("🔧 Panel de Administración")

tabs = st.tabs(tabs_list)

# Índices de tabs (siempre los mismos)
TAB_CALCULOS = 0
TAB_DATOS_CLIENTE = 1
TAB_FORMULAS = 2
TAB_SENSIBILIDAD = 3
TAB_MANIFEST = 4
TAB_INFO = 5
TAB_ADMIN = 6 if st.session_state.get('user_role') == 'Administrador' and NOTIFICATIONS_ENABLED else None

# Inicializar base de datos si está habilitado
if NOTIFICATIONS_ENABLED:
    if 'db_initialized' not in st.session_state:
        try:
            init_database()
            st.session_state['db_initialized'] = True
        except Exception as e:
            st.warning(f"⚠️ No se pudo inicializar la base de datos: {str(e)}")
            st.info("💡 El sistema de notificaciones no estará disponible. Verifique la configuración de PostgreSQL.")

# ============================================
# TAB 1: CÁLCULOS PRINCIPALES
# ============================================
with tabs[TAB_CALCULOS]:
    st.header("Cálculo de Sistema GNV/CNG")
    
    # Dividir en columnas para mejor organización
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Parámetros de Entrada")
        
        # Parámetros de operación
        st.markdown("#### Parámetros de Operación")
        consumo_diesel = st.number_input(
            "Consumo de Diésel (L/100 km)",
            min_value=1.0,
            max_value=200.0,
            value=35.0,
            step=0.5,
            help="Consumo de combustible diésel del vehículo"
        )
        
        autonomia_deseada = st.number_input(
            "Autonomía Deseada (km)",
            min_value=100.0,
            max_value=2000.0,
            value=DEFAULT_AUTONOMIA,
            step=10.0,
            help="Distancia que se desea recorrer con un tanque lleno"
        )
        
        # Parámetros técnicos
        st.markdown("#### Parámetros Técnicos")
        poder_calorifico_diesel = st.number_input(
            "Poder Calorífico Diésel (MJ/L)",
            min_value=30.0,
            max_value=40.0,
            value=35.8,
            step=0.1,
            help="Poder calorífico del diésel (ASTM D975)"
        )
        
        lhv_ch4 = st.number_input(
            "LHV CH₄ - Poder Calorífico Inferior (MJ/kg)",
            min_value=45.0,
            max_value=55.0,
            value=50.0,
            step=0.1,
            help="Lower Heating Value del metano (ISO 6976:2016)"
        )
        
        eficiencia_conversion = st.number_input(
            "Eficiencia de Conversión GNV vs Diésel",
            min_value=0.80,
            max_value=1.0,
            value=0.95,
            step=0.01,
            help="Factor de eficiencia del sistema GNV comparado con diésel"
        )
    
    with col2:
        st.subheader("⚙️ Parámetros de Almacenamiento")
        
        # Parámetros de presión y temperatura
        st.markdown("#### Condiciones de Almacenamiento")
        presion_llenado = st.number_input(
            "Presión de Llenado (bar)",
            min_value=150.0,
            max_value=300.0,
            value=200.0,
            step=10.0,
            help="Presión de trabajo de los tanques CNG"
        )
        
        temperatura_operacion = st.number_input(
            "Temperatura de Operación (°C)",
            min_value=0.0,
            max_value=50.0,
            value=25.0,
            step=1.0,
            help="Temperatura ambiente de operación"
        )
        
        factor_compresibilidad = st.number_input(
            "Factor de Compresibilidad Z",
            min_value=0.70,
            max_value=1.0,
            value=0.85,
            step=0.01,
            help="Factor de compresibilidad del gas (NIST Chemistry WebBook)"
        )
        
        # Parámetros de tanques
        st.markdown("#### Características de Tanques")
        volumen_unitario_tanque = st.number_input(
            "Volumen Unitario Tanque (m³)",
            min_value=0.01,
            max_value=0.20,
            value=0.080,
            step=0.005,
            help="Volumen de cada tanque individual"
        )
        
        peso_tanque_vacio = st.number_input(
            "Peso Tanque Vacío (kg)",
            min_value=20.0,
            max_value=150.0,
            value=65.0,
            step=1.0,
            help="Peso de un tanque tipo 3 vacío"
        )
        
        peso_soportes = st.number_input(
            "Peso Soportes por Tanque (kg)",
            min_value=5.0,
            max_value=30.0,
            value=10.0,
            step=0.5,
            help="Peso de soportes y estructura por tanque"
        )
        
        peso_accesorios = st.number_input(
            "Peso Accesorios por Tanque (kg)",
            min_value=1.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            help="Peso de válvulas, conexiones, etc. por tanque"
        )
    
    # Constantes físicas
    st.markdown("---")
    with st.expander("🔬 Constantes Físicas (Editable)"):
        col_const1, col_const2 = st.columns(2)
        with col_const1:
            constante_gases = st.number_input(
                "Constante Universal de Gases R (J/(mol·K))",
                min_value=8.0,
                max_value=9.0,
                value=8.314,
                step=0.001,
                format="%.3f"
            )
            
            masa_molar_ch4 = st.number_input(
                "Masa Molar CH₄ (kg/mol)",
                min_value=0.015,
                max_value=0.020,
                value=0.01604,
                step=0.0001,
                format="%.4f"
            )
    
    # Botón para calcular
    st.markdown("---")
    calcular = st.button("🚀 Calcular Sistema GNV", type="primary", width='stretch')
    
    if calcular:
        # ============================================
        # CÁLCULOS PASO A PASO
        # ============================================
        st.markdown("---")
        st.header("📊 Resultados del Cálculo")
        
        # Usar el motor de cálculos
        resultado = calcular_sistema_gnv(
            consumo_diesel,
            autonomia_deseada,
            poder_calorifico_diesel,
            lhv_ch4,
            eficiencia_conversion,
            presion_llenado,
            temperatura_operacion,
            factor_compresibilidad,
            volumen_unitario_tanque,
            peso_tanque_vacio,
            peso_soportes,
            peso_accesorios,
            constante_gases,
            masa_molar_ch4
        )
        
        # Extraer valores para compatibilidad con código existente
        volumen_diesel_equivalente = resultado['volumen_diesel_equivalente']
        energia_requerida = resultado['energia_requerida']
        masa_ch4_requerida = resultado['masa_ch4_requerida']
        volumen_gas = resultado['volumen_gas']
        numero_tanques = resultado['numero_tanques']
        peso_adicional_total = resultado['peso_adicional_total']
        
        # Conversiones de unidades para la presentación
        temperatura_k = temperatura_operacion + 273.15  # Convertir °C a Kelvin
        presion_pa = presion_llenado * 100000  # Convertir bar a Pascal (1 bar = 100,000 Pa)
        
        # Guardar resultados en session_state para el informe
        st.session_state['calculo_resultado'] = {
            'consumo_base': resultado['consumo_base'],
            'autonomia_objetivo': resultado['autonomia_objetivo'],
            'energia': energia_requerida,
            'masa_ch4': masa_ch4_requerida,
            'volumen': volumen_gas,
            'tanques': numero_tanques,
            'peso': peso_adicional_total,
            'presion_llenado': resultado['presion_llenado'],
            'temperatura': resultado['temperatura_operacion'],
            'volumen_diesel_equivalente': volumen_diesel_equivalente
        }
        
        # Guardar cálculos en BD si hay un submission activo
        if NOTIFICATIONS_ENABLED and 'current_submission_id' in st.session_state:
            try:
                parametros_entrada = {
                    'consumo_diesel': consumo_diesel,
                    'autonomia_deseada': autonomia_deseada,
                    'poder_calorifico_diesel': poder_calorifico_diesel,
                    'lhv_ch4': lhv_ch4,
                    'eficiencia_conversion': eficiencia_conversion,
                    'presion_llenado': presion_llenado,
                    'temperatura_operacion': temperatura_operacion,
                    'factor_compresibilidad': factor_compresibilidad,
                    'volumen_unitario_tanque': volumen_unitario_tanque,
                    'peso_tanque_vacio': peso_tanque_vacio,
                    'peso_soportes': peso_soportes,
                    'peso_accesorios': peso_accesorios,
                    'constante_gases': constante_gases,
                    'masa_molar_ch4': masa_molar_ch4
                }
                
                add_calculos_to_submission(
                    submission_id=st.session_state['current_submission_id'],
                    resultados=st.session_state['calculo_resultado'],
                    parametros=parametros_entrada
                )
            except Exception as e:
                print(f"⚠️ Error al guardar cálculos en BD: {str(e)}")
        
        # ============================================
        # PRESENTACIÓN DE RESULTADOS
        # ============================================
        
        # Mostrar cálculos paso a paso
        st.subheader("🔍 Proceso de Cálculo Paso a Paso")
        
        calculo_col1, calculo_col2 = st.columns(2)
        
        with calculo_col1:
            st.markdown("""
            **Paso 1: Volumen Diésel Equivalente**
            ```
            V_diesel = (Consumo × Autonomía) / 100
            V_diesel = ({:.1f} L/100km × {:.1f} km) / 100
            V_diesel = {:.2f} L
            ```
            """.format(consumo_diesel, autonomia_deseada, volumen_diesel_equivalente))
            
            st.markdown("""
            **Paso 2: Energía Requerida**
            ```
            E = V_diesel × E_diesel
            E = {:.2f} L × {:.1f} MJ/L
            E = {:.2f} MJ
            ```
            """.format(volumen_diesel_equivalente, poder_calorifico_diesel, energia_requerida))
            
            st.markdown("""
            **Paso 3: Masa de CH₄ Requerida**
            ```
            m_CH4 = (E / LHV_CH4) / η
            m_CH4 = ({:.2f} MJ / {:.1f} MJ/kg) / {:.2f}
            m_CH4 = {:.2f} kg
            ```
            """.format(energia_requerida, lhv_ch4, eficiencia_conversion, masa_ch4_requerida))
        
        with calculo_col2:
            st.markdown("""
            **Paso 4: Volumen de Gas a Presión de Llenado**
            ```
            V = (m_CH4 × R × T) / (p × M × Z)
            V = ({:.2f} × {:.3f} × {:.2f}) / ({:.0f} × {:.4f} × {:.2f})
            V = {:.2f} m³
            ```
            """.format(
                masa_ch4_requerida, constante_gases, temperatura_k,
                presion_pa, masa_molar_ch4, factor_compresibilidad, volumen_gas
            ))
            
            st.markdown("""
            **Paso 5: Número de Tanques Requeridos**
            ```
            n_tanques = ceil(V / V_unitario)
            n_tanques = ceil({:.2f} m³ / {:.3f} m³)
            n_tanques = {} tanques
            ```
            """.format(volumen_gas, volumen_unitario_tanque, numero_tanques))
            
            st.markdown("""
            **Paso 6: Peso Adicional Total**
            ```
            P_adicional = n × (m_tanque + m_soportes + m_accesorios)
            P_adicional = {} × ({} + {} + {})
            P_adicional = {:.0f} kg
            ```
            """.format(
                numero_tanques, peso_tanque_vacio, peso_soportes, peso_accesorios, peso_adicional_total
            ))
        
        # Resumen en tabla
        st.markdown("---")
        st.subheader("📋 Resumen de Resultados")
        
        resumen_data = {
            "Parámetro": [
                "Volumen Diésel Equivalente",
                "Energía Requerida",
                "Masa CH₄ Requerida",
                "Volumen de Gas (a {} bar)".format(presion_llenado),
                "Número de Tanques",
                "Peso Adicional Total"
            ],
            "Valor": [
                "{:.2f} L".format(volumen_diesel_equivalente),
                "{:.2f} MJ".format(energia_requerida),
                "{:.2f} kg".format(masa_ch4_requerida),
                "{:.2f} m³ ({:.0f} L)".format(volumen_gas, volumen_gas * 1000),
                "{} unidades".format(numero_tanques),
                "{:.0f} kg ({:.2f} ton)".format(peso_adicional_total, peso_adicional_total / 1000)
            ]
        }
        
        df_resumen = pd.DataFrame(resumen_data)
        st.dataframe(df_resumen, width='stretch', hide_index=True)
        
        # Alertas y recomendaciones
        st.markdown("---")
        st.subheader("⚠️ Alertas y Recomendaciones")
        
        if peso_adicional_total > 2000:
            st.warning("⚠️ **Peso adicional significativo**: El peso adicional de {:.0f} kg puede afectar significativamente la capacidad de carga del vehículo. Considerar reducir la autonomía o usar tanques tipo 4 (más livianos).".format(peso_adicional_total))
        
        if numero_tanques > 25:
            st.warning("⚠️ **Número elevado de tanques**: Se requieren {} tanques, lo que puede ser difícil de acomodar en el chasis. Considerar tanques de mayor volumen o reducir autonomía.".format(numero_tanques))
        
        if volumen_gas > 3.0:
            st.info("ℹ️ **Volumen considerable**: El volumen total de {:.2f} m³ requiere espacio significativo. Validar disponibilidad de espacio en el vehículo.".format(volumen_gas))
        
        if presion_llenado > 220:
            st.info("ℹ️ **Presión elevada**: Presión de {} bar requiere tanques tipo 4 (composite completo), más costosos pero más livianos.".format(presion_llenado))

    # Sección de diagrama P&ID - Visible para todos los usuarios
    # Los clientes solo pueden descargar PDF existente, administradores tienen acceso completo
    st.markdown("---")
    
    # Verificar si hay resultados de cálculo
    if 'calculo_resultado' in st.session_state and st.session_state.get('calculo_resultado'):
        # Si hay resultados, mostrar siempre visible (sin expander) para evitar que se cierre
        st.subheader("📊 Diagrama P&ID del Sistema GNV")
        # Asegurar que el estado se mantenga siempre visible
        st.session_state['diagram_expander_open'] = True
        st.session_state['diagram_visible'] = True
        
        # Usar un container con key para mantener el contenido siempre visible
        with st.container():
            show_diagram_generator(
                st.session_state['calculo_resultado'],
                st.session_state.get('proyecto_cliente', 'PETROLIQUIDOS')
            )
    else:
        # Solo mostrar mensaje si nunca se ha calculado
        with st.expander("📊 Diagrama P&ID del Sistema GNV", expanded=False):
            st.info("ℹ️ Realice un cálculo del sistema primero para generar el diagrama P&ID.")

# ============================================
# TAB: DATOS DEL CLIENTE
# ============================================
with tabs[TAB_DATOS_CLIENTE]:
    st.header("👤 Datos del Cliente y Supuestos")
    
    # Banner informativo
    st.info("""
    📋 **Complete los siguientes campos con la información de su flota.** 
    Use las guías expandibles (ℹ️) para ver ejemplos y saber qué información incluir en cada sección.
    """)
    
    # Inicializar datos del cliente en session_state
    if 'cliente_data' not in st.session_state:
        st.session_state['cliente_data'] = {
            'nombre': st.session_state.get('proyecto_cliente', ''),
            'rol': st.session_state.get('user_role', 'Cliente'),
            'capacidad_de_la_flota': '',
            'supuestos': {
                'operacional': '',
                'componentes': ''
            },
            'fecha_creacion': None,
            'fecha_ultima_actualizacion': None,
            'usuario_creador': None,
            'usuario_ultima_actualizacion': None
        }
    
    with st.form("cliente_form"):
        st.subheader("📋 Información del Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_cliente = st.text_input(
                "Nombre del Cliente",
                value=st.session_state['cliente_data']['nombre'],
                help="Nombre completo del cliente o empresa"
            )
            
            capacidad_flota = st.text_input(
                "Capacidad de la Flota",
                value=st.session_state['cliente_data']['capacidad_de_la_flota'],
                help="Número de vehículos o capacidad total de la flota"
            )
        
        with col2:
            rol_usuario = st.selectbox(
                "Rol",
                ["Cliente", "Administrador"],
                index=0 if st.session_state['cliente_data']['rol'] == 'Cliente' else 1,
                disabled=True,
                help="Rol del usuario (no editable)"
            )
        
        st.subheader("🔧 Supuestos Operativos")
        
        with st.expander("ℹ️ Guía: ¿Qué información incluir en Supuestos Operativos?", expanded=False):
            st.markdown("""
            **Incluya la siguiente información:**
            
            1. **Consumo de combustible actual:**
               - Consumo promedio de diésel (L/100 km)
               - Variación según tipo de ruta (carretera/urbano/mixto)
            
            2. **Perfil de operación:**
               - Kilómetros recorridos por día/mes
               - Porcentaje de operación en carretera vs urbano
               - Altitud típica de operación (metros sobre el nivel del mar)
            
            3. **Autonomía requerida:**
               - Distancia mínima deseada sin recargar (km)
               - Frecuencia de recarga aceptable
            
            4. **Rutas principales:**
               - Rutas más frecuentes
               - Disponibilidad de estaciones GNV en rutas
            
            **Ejemplo:**
            ```
            Consumo promedio: 35-40 L/100km en carretera, 45-50 L/100km en ciudad.
            Operación: 80% carretera, 20% urbano. 15,000 km/mes promedio.
            Altitud: 0-2000 m sobre el nivel del mar.
            Autonomía mínima requerida: 600 km.
            Rutas principales: Bogotá-Medellín, con estaciones GNV disponibles.
            ```
            """)
        
        ejemplo_operacional = """Consumo promedio: 35-40 L/100km en carretera, 45-50 L/100km en ciudad.
Operación: 80% carretera, 20% urbano. 15,000 km/mes promedio.
Altitud: 0-2000 m sobre el nivel del mar.
Autonomía mínima requerida: 600 km.
Rutas principales: Bogotá-Medellín, con estaciones GNV disponibles."""
        
        supuestos_operacional = st.text_area(
            "Supuestos Operativos",
            value=st.session_state['cliente_data']['supuestos']['operacional'] or ejemplo_operacional,
            height=150,
            help="Describa los supuestos operativos: consumo, rutas, autonomía requerida, etc.",
            placeholder="Ingrese información sobre consumo, perfil de operación, autonomía requerida y rutas principales..."
        )
        
        st.subheader("⚙️ Supuestos de Componentes")
        
        with st.expander("ℹ️ Guía: ¿Qué información incluir en Supuestos de Componentes?", expanded=False):
            st.markdown("""
            **Incluya la siguiente información:**
            
            1. **Tipo de tanques preferido:**
               - Tipo 3 (composite con liner metálico) - más económico
               - Tipo 4 (fully composite) - más liviano pero más costoso
            
            2. **Presión de trabajo:**
               - 200 bar (estándar Colombia)
               - 250 bar (mayor densidad, requiere tanques tipo 4)
            
            3. **Restricciones de espacio:**
               - Espacio disponible en chasis para tanques
               - Limitaciones de peso adicional aceptable
            
            4. **Preferencias técnicas:**
               - Sistema bi-fuel (GNV + diésel) o dedicado GNV
               - Tipo de inyección preferido (mezclador/secuencial/directa)
            
            5. **Presupuesto y prioridades:**
               - Prioridad: costo vs peso vs autonomía
            
            **Ejemplo:**
            ```
            Tipo de tanques: Tipo 3 (composite con liner metálico).
            Presión de trabajo: 200 bar (estándar).
            Restricción de peso: Máximo 2000 kg adicionales aceptables.
            Sistema: Bi-fuel (GNV + diésel) para mantener flexibilidad.
            Inyección: Secuencial para mejor eficiencia.
            Prioridad: Balance costo-beneficio, autonomía mínima 600 km.
            ```
            """)
        
        ejemplo_componentes = """Tipo de tanques: Tipo 3 (composite con liner metálico).
Presión de trabajo: 200 bar (estándar).
Restricción de peso: Máximo 2000 kg adicionales aceptables.
Sistema: Bi-fuel (GNV + diésel) para mantener flexibilidad.
Inyección: Secuencial para mejor eficiencia.
Prioridad: Balance costo-beneficio, autonomía mínima 600 km."""
        
        supuestos_componentes = st.text_area(
            "Supuestos de Componentes",
            value=st.session_state['cliente_data']['supuestos']['componentes'] or ejemplo_componentes,
            height=150,
            help="Describa los supuestos de componentes: tipo de tanques, presión, características técnicas, etc.",
            placeholder="Ingrese información sobre tipo de tanques, presión, restricciones y preferencias técnicas..."
        )
        
        submitted = st.form_submit_button("💾 Guardar Datos del Cliente")
        
        if submitted:
            # Obtener timestamp actual
            fecha_actual = datetime.now()
            fecha_iso = fecha_actual.isoformat()
            fecha_formateada = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
            usuario_actual = st.session_state.get('username', 'Desconocido')
            
            # Preservar fecha de creación si es la primera vez
            fecha_creacion = st.session_state['cliente_data'].get('fecha_creacion')
            usuario_creador = st.session_state['cliente_data'].get('usuario_creador')
            
            if fecha_creacion is None:
                fecha_creacion = fecha_iso
                usuario_creador = usuario_actual
            
            # Preparar datos del cliente
            cliente_data_dict = {
                'nombre': nombre_cliente,
                'rol': st.session_state.get('user_role', 'Cliente'),
                'capacidad_de_la_flota': capacidad_flota,
                'supuestos': {
                    'operacional': supuestos_operacional,
                    'componentes': supuestos_componentes
                }
            }
            
            metadata_dict = {
                'fecha_creacion': fecha_creacion,
                'fecha_ultima_actualizacion': fecha_iso,
                'usuario_creador': usuario_creador,
                'usuario_ultima_actualizacion': usuario_actual
            }
            
            # Guardar en session_state
            st.session_state['cliente_data'] = {
                **cliente_data_dict,
                'fecha_creacion': fecha_creacion,
                'fecha_ultima_actualizacion': fecha_iso,
                'usuario_creador': usuario_creador,
                'usuario_ultima_actualizacion': usuario_actual
            }
            
            # Crear submission en BD y enviar notificaciones (solo si está habilitado)
            if NOTIFICATIONS_ENABLED:
                try:
                    submission_id = create_submission(
                        cliente_nombre=nombre_cliente,
                        usuario_cliente=usuario_actual,
                        datos_cliente=cliente_data_dict,
                        metadata=metadata_dict
                    )
                    
                    if submission_id:
                        # Guardar submission_id en session_state para asociar cálculos y diagramas
                        st.session_state['current_submission_id'] = submission_id
                        
                        # Enviar notificaciones
                        notif_results = send_notifications(submission_id, nombre_cliente, usuario_actual)
                        
                        if notif_results.get('email') or notif_results.get('app'):
                            st.success(f"✅ Datos del cliente guardados correctamente el {fecha_formateada}")
                            if notif_results.get('email'):
                                st.info("📧 Notificación por email enviada al administrador.")
                            if notif_results.get('app'):
                                st.info("🔔 Notificación creada en el panel de administración.")
                        else:
                            st.success(f"✅ Datos del cliente guardados correctamente el {fecha_formateada}")
                            st.warning("⚠️ No se pudieron enviar las notificaciones, pero los datos se guardaron correctamente.")
                    else:
                        st.success(f"✅ Datos del cliente guardados correctamente el {fecha_formateada}")
                        st.warning("⚠️ No se pudo crear el registro en la base de datos, pero los datos se guardaron en sesión.")
                except Exception as e:
                    st.success(f"✅ Datos del cliente guardados correctamente el {fecha_formateada}")
                    st.warning(f"⚠️ Error al registrar en base de datos: {str(e)}")
            else:
                st.success(f"✅ Datos del cliente guardados correctamente el {fecha_formateada}")
    
    # Mostrar información de auditoría (visible para todos)
    if st.session_state['cliente_data'].get('fecha_creacion'):
        st.markdown("---")
        st.markdown("#### 📅 Registro de Datos")
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            fecha_creacion = st.session_state['cliente_data'].get('fecha_creacion', '')
            if fecha_creacion:
                try:
                    fecha_creacion_dt = datetime.fromisoformat(fecha_creacion.replace('Z', '+00:00') if 'Z' in fecha_creacion else fecha_creacion)
                    fecha_creacion_formateada = fecha_creacion_dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    fecha_creacion_formateada = fecha_creacion
                st.caption(f"**Creado:** {fecha_creacion_formateada} por {st.session_state['cliente_data'].get('usuario_creador', 'N/A')}")
        
        with col_info2:
            fecha_actualizacion = st.session_state['cliente_data'].get('fecha_ultima_actualizacion', '')
            if fecha_actualizacion:
                try:
                    fecha_actualizacion_dt = datetime.fromisoformat(fecha_actualizacion.replace('Z', '+00:00') if 'Z' in fecha_actualizacion else fecha_actualizacion)
                    fecha_actualizacion_formateada = fecha_actualizacion_dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    fecha_actualizacion_formateada = fecha_actualizacion
                st.caption(f"**Última actualización:** {fecha_actualizacion_formateada} por {st.session_state['cliente_data'].get('usuario_ultima_actualizacion', 'N/A')}")
    
    # Exportar JSON (solo para Administrador)
    if st.session_state.get('user_role') == 'Administrador':
        st.markdown("---")
        st.subheader("📥 Exportar Datos en JSON")
        
        # Mostrar información de auditoría
        if st.session_state['cliente_data'].get('fecha_creacion'):
            st.markdown("#### 📅 Información de Auditoría")
            col_aud1, col_aud2 = st.columns(2)
            
            with col_aud1:
                fecha_creacion = st.session_state['cliente_data'].get('fecha_creacion', '')
                if fecha_creacion:
                    try:
                        fecha_creacion_dt = datetime.fromisoformat(fecha_creacion.replace('Z', '+00:00') if 'Z' in fecha_creacion else fecha_creacion)
                        fecha_creacion_formateada = fecha_creacion_dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        fecha_creacion_formateada = fecha_creacion
                    st.info(f"**Fecha de creación:**\n{fecha_creacion_formateada}\n**Usuario:** {st.session_state['cliente_data'].get('usuario_creador', 'N/A')}")
            
            with col_aud2:
                fecha_actualizacion = st.session_state['cliente_data'].get('fecha_ultima_actualizacion', '')
                if fecha_actualizacion:
                    try:
                        fecha_actualizacion_dt = datetime.fromisoformat(fecha_actualizacion.replace('Z', '+00:00') if 'Z' in fecha_actualizacion else fecha_actualizacion)
                        fecha_actualizacion_formateada = fecha_actualizacion_dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        fecha_actualizacion_formateada = fecha_actualizacion
                    st.info(f"**Última actualización:**\n{fecha_actualizacion_formateada}\n**Usuario:** {st.session_state['cliente_data'].get('usuario_ultima_actualizacion', 'N/A')}")
        
        cliente_json = {
            "cliente": {
                "nombre": st.session_state['cliente_data']['nombre'],
                "rol": st.session_state['cliente_data']['rol'],
                "capacidad_de_la_flota": st.session_state['cliente_data']['capacidad_de_la_flota'],
                "supuestos": {
                    "operacional": st.session_state['cliente_data']['supuestos']['operacional'],
                    "componentes": st.session_state['cliente_data']['supuestos']['componentes']
                },
                "metadata": {
                    "fecha_creacion": st.session_state['cliente_data'].get('fecha_creacion', ''),
                    "fecha_ultima_actualizacion": st.session_state['cliente_data'].get('fecha_ultima_actualizacion', ''),
                    "usuario_creador": st.session_state['cliente_data'].get('usuario_creador', ''),
                    "usuario_ultima_actualizacion": st.session_state['cliente_data'].get('usuario_ultima_actualizacion', '')
                }
            }
        }
        
        # Convertir JSON a HTML para descarga
        # Formato de fecha en español
        meses_es = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
            7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        fecha_obj = datetime.now()
        fecha_actual_es = f"{fecha_obj.day} de {meses_es[fecha_obj.month]} de {fecha_obj.year}"
        
        html_cliente = convertir_json_a_html(
            cliente_json,
            titulo="Datos del Cliente",
            header="Datos del Cliente - WELDTECH SOLUTIONS",
            footer=f"Datos del Cliente | Versión 1.0 | {fecha_actual_es}",
            nombre_archivo="datos_cliente"
        )
        
        # Generar PDF desde HTML
        pdf_data, error_msg = generar_pdf_desde_html(html_cliente)
        if pdf_data:
            b64_pdf = base64.b64encode(pdf_data).decode()
            nombre_archivo_pdf = f"datos_cliente_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{nombre_archivo_pdf}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📄 Descargar Datos del Cliente en PDF</a>'
            st.markdown(href_pdf, unsafe_allow_html=True)
        else:
            # Fallback a HTML si no se puede generar PDF
            b64_html = base64.b64encode(html_cliente.encode('utf-8')).decode()
            href_html = f'<a href="data:text/html;charset=utf-8;base64,{b64_html}" download="datos_cliente_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html" style="background-color: #2AA1FF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 Descargar HTML para Imprimir</a>'
            st.markdown(href_html, unsafe_allow_html=True)
            if error_msg:
                st.warning(f"⚠️ No se pudo generar el PDF: {error_msg}")
                st.info("💡 **Alternativa:** Se ha descargado el HTML. Puede convertirlo a PDF usando su navegador (Archivo > Imprimir > Guardar como PDF)")
        
        # Mantener el expander para ver JSON
        json_str = json.dumps(cliente_json, indent=2, ensure_ascii=False)
        with st.expander("👁️ Ver JSON"):
            st.code(json_str, language="json")

# ============================================
# TAB: FÓRMULAS Y PROCEDIMIENTOS (Solo Administrador)
# ============================================
with tabs[TAB_FORMULAS]:
    if st.session_state.get('user_role') == 'Administrador':
        st.header("📐 Fórmulas y Procedimientos Numéricos")
        
        st.markdown("""
        ## 4.1 Fórmulas Implementadas
        
        ### 4.1.1 Energía Requerida
        
        La energía requerida se calcula multiplicando el volumen de diésel equivalente 
        por el poder calorífico del diésel:
        
        $$
        E \\, (\\text{MJ}) = V_{\\text{diesel}} \\, (\\text{L}) \\times E_{\\text{diesel}} \\, (\\text{MJ/L})
        $$
        
        Donde:
        - $E_{\\text{diesel}} = 35.8 \\, \\text{MJ/L}$ (poder calorífico diésel según ASTM D975)
        
        ---
        
        ### 4.1.2 Masa de CH₄ Requerida
        
        La masa de metano requerida se obtiene dividiendo la energía requerida por el 
        poder calorífico inferior del metano, ajustado por la eficiencia de conversión:
        
        $$
        m_{\\text{CH}_4} \\, (\\text{kg}) = \\frac{E \\, (\\text{MJ})}{\\text{LHV}_{\\text{CH}_4} \\, (\\text{MJ/kg}) \\times \\eta}
        $$
        
        Donde:
        - $\\text{LHV}_{\\text{CH}_4} = 50.0 \\, \\text{MJ/kg}$ (poder calorífico inferior metano según ISO 6976:2016)
        - $\\eta$ = eficiencia de conversión GNV vs diésel (típicamente 0.90-0.95)
        
        ---
        
        ### 4.1.3 Volumen de Gas a Presión de Llenado
        
        Utilizando la ecuación de estado de gases reales:
        
        $$
        pV = Z \\frac{mRT}{M}
        $$
        
        Despejando el volumen:
        
        $$
        V \\, (\\text{m}^3) = \\frac{m_{\\text{CH}_4} \\times R \\times T}{p \\times M \\times Z}
        $$
        
        Donde:
        - $p$ = presión en Pascal (bar × 100,000)
        - $R = 8.314 \\, \\text{J/(mol·K)}$ (constante universal de gases)
        - $T$ = temperatura en Kelvin (°C + 273.15)
        - $M = 0.01604 \\, \\text{kg/mol}$ (masa molar del metano)
        - $Z$ = factor de compresibilidad (típicamente 0.80-0.90 para CH₄ a 200 bar, 25°C)
        
        **Nota**: Se asume CH₄ puro. En realidad, el gas natural vehicular contiene 
        ~90-95% CH₄, 3-5% etano y trazas de otros hidrocarburos. El factor Z puede 
        variar ligeramente según la composición.
        
        ---
        
        ### 4.1.4 Número de Tanques Requeridos
        
        El número de tanques se calcula dividiendo el volumen total requerido entre 
        el volumen unitario de cada tanque, redondeando hacia arriba:
        
        $$
        n_{\\text{tanques}} = \\left\\lceil \\frac{V_{\\text{requerido}} \\, (\\text{m}^3)}{V_{\\text{unitario}} \\, (\\text{m}^3)} \\right\\rceil
        $$
        
        Siempre se requiere un número entero de tanques.
        
        ---
        
        ### 4.1.5 Peso Adicional Estimado
        
        El peso adicional total incluye el peso de los tanques, soportes y accesorios:
        
        $$
        P_{\\text{adicional}} \\, (\\text{kg}) = n_{\\text{tanques}} \\times (m_{\\text{tanque}} + m_{\\text{soportes}} + m_{\\text{accesorios}})
        $$
        
        Donde:
        - $m_{\\text{tanque}}$ = peso del tanque vacío (típicamente 50-80 kg para tipo 3)
        - $m_{\\text{soportes}}$ = peso de soportes y estructura por tanque (típicamente 10-15 kg)
        - $m_{\\text{accesorios}}$ = peso de válvulas, conexiones, etc. por tanque (típicamente 5-10 kg)
        
        ---
        
        ## Ejemplo de Cálculo Completo
        
        **Parámetros de entrada:**
        - Consumo diésel: 35 L/100 km
        - Autonomía deseada: 800 km
        - Presión de llenado: 200 bar
        - Temperatura: 25°C
        
        **Cálculos:**
        
        1. **Volumen diésel equivalente:**
           $$
           V_{\\text{diesel}} = \\frac{35 \\times 800}{100} = 280 \\, \\text{L}
           $$
        
        2. **Energía requerida:**
           $$
           E = 280 \\times 35.8 = 10,024 \\, \\text{MJ}
           $$
        
        3. **Masa de CH₄ requerida (η = 0.95):**
           $$
           m_{\\text{CH}_4} = \\frac{10,024}{50.0 \\times 0.95} = 211.0 \\, \\text{kg}
           $$
        
        4. **Volumen de gas a 200 bar:**
           $$
           V = \\frac{158.0 \\times 8.314 \\times 298}{20,000,000 \\times 0.01604 \\times 0.85} = 1.44 \\, \\text{m}^3
           $$
        
        5. **Número de tanques (V_unitario = 0.080 m³):**
           $$
           n_{\\text{tanques}} = \\left\\lceil \\frac{1.44}{0.080} \\right\\rceil = 18 \\, \\text{tanques}
           $$
        
        6. **Peso adicional:**
           $$
           P_{\\text{adicional}} = 18 \\times (65 + 10 + 5) = 1,440 \\, \\text{kg}
           $$
        """)
    else:
        st.warning("🔒 **Acceso Restringido**: Solo los administradores pueden acceder a esta sección.")
        st.info("Esta sección contiene las fórmulas y procedimientos numéricos detallados del sistema.")

# ============================================
# TAB: ANÁLISIS DE SENSIBILIDAD
# ============================================
with tabs[TAB_SENSIBILIDAD]:
    st.header("📊 Análisis de Sensibilidad")
    
    st.markdown("""
    El análisis de sensibilidad permite evaluar cómo varían los resultados 
    cuando se modifican los parámetros de entrada. Esto es útil para:
    
    - Identificar parámetros críticos
    - Optimizar el diseño del sistema
    - Evaluar escenarios alternativos
    """)
    
    # Parámetros base para análisis
    st.subheader("Parámetros Base")
    col_sens1, col_sens2 = st.columns(2)
    
    with col_sens1:
        consumo_base = st.number_input(
            "Consumo Base (L/100 km)",
            min_value=20.0,
            max_value=60.0,
            value=35.0,
            step=1.0,
            key="sens_consumo"
        )
        
        autonomia_base = st.number_input(
            "Autonomía Base (km)",
            min_value=400.0,
            max_value=1200.0,
            value=DEFAULT_AUTONOMIA,
            step=50.0,
            key="sens_autonomia"
        )
    
    with col_sens2:
        variacion = st.slider(
            "Variación a Analizar (%)",
            min_value=5,
            max_value=30,
            value=20,
            step=5
        )
    
    if st.button("🔄 Calcular Análisis de Sensibilidad", type="primary"):
        # Variable para rastrear errores (solo mostrar una vez) - usando lista para evitar nonlocal
        error_mostrado = [False]
        
        # Función wrapper para usar el motor de cálculos con validación
        def calcular_sistema(consumo, autonomia):
            try:
                # Validar entradas
                if not math.isfinite(consumo) or consumo <= 0:
                    return {'energia': 0, 'masa_ch4': 0, 'volumen': 0, 'tanques': 0, 'peso': 0}
                if not math.isfinite(autonomia) or autonomia <= 0:
                    return {'energia': 0, 'masa_ch4': 0, 'volumen': 0, 'tanques': 0, 'peso': 0}
                
                # Usar el motor de cálculos
                resultado = calcular_sistema_gnv(
                    consumo, autonomia,
                    DEFAULT_PODER_CALORIFICO, DEFAULT_LHV_CH4, DEFAULT_EFICIENCIA,
                    DEFAULT_PRESION, DEFAULT_TEMPERATURA, DEFAULT_FACTOR_Z,
                    DEFAULT_VOLUMEN_TANQUE, DEFAULT_PESO_TANQUE,
                    DEFAULT_PESO_SOPORTES, DEFAULT_PESO_ACCESORIOS,
                    CONSTANTE_GASES, MASA_MOLAR_CH4
                )
                
                # Validar que el resultado tenga todas las claves necesarias
                if not isinstance(resultado, dict):
                    if not error_mostrado[0]:
                        st.error(f"Error: resultado no es un diccionario. Tipo: {type(resultado)}")
                        error_mostrado[0] = True
                    return {'energia': 0, 'masa_ch4': 0, 'volumen': 0, 'tanques': 0, 'peso': 0}
                
                # Validar resultados
                energia = resultado.get('energia_requerida', 0)
                masa_ch4 = resultado.get('masa_ch4_requerida', 0)
                volumen = resultado.get('volumen_gas', 0)
                tanques = resultado.get('numero_tanques', 0)
                peso = resultado.get('peso_adicional_total', 0)
                
                if not all(math.isfinite(v) for v in [energia, masa_ch4, volumen, tanques, peso]):
                    if not error_mostrado[0]:
                        st.warning(f"Algunos valores no son finitos. Verifique los parámetros de entrada.")
                        error_mostrado[0] = True
                    return {'energia': 0, 'masa_ch4': 0, 'volumen': 0, 'tanques': 0, 'peso': 0}
                
                return {
                    'energia': energia,
                    'masa_ch4': masa_ch4,
                    'volumen': volumen,
                    'tanques': int(tanques),
                    'peso': peso
                }
            except Exception as e:
                if not error_mostrado[0]:
                    st.error(f"Error en calcular_sistema: {str(e)}")
                    import traceback
                    st.error(f"Traceback: {traceback.format_exc()}")
                    error_mostrado[0] = True
                return {'energia': 0, 'masa_ch4': 0, 'volumen': 0, 'tanques': 0, 'peso': 0}
        
        # Análisis de variación de consumo
        st.subheader("Variación de Consumo de Combustible")
        
        variaciones_consumo = []
        for var in [-variacion, -variacion//2, 0, variacion//2, variacion]:
            consumo_var = consumo_base * (1 + var/100)
            resultado = calcular_sistema(consumo_var, autonomia_base)
            variaciones_consumo.append({
                'Variación (%)': f"{var:+.0f}%",
                'Consumo (L/100km)': f"{consumo_var:.1f}",
                'Energía (MJ)': f"{resultado['energia']:.0f}",
                'Masa CH₄ (kg)': f"{resultado['masa_ch4']:.2f}",
                'Volumen (m³)': f"{resultado['volumen']:.2f}",
                'N° Tanques': resultado['tanques'],
                'Peso (kg)': f"{resultado['peso']:.0f}"
            })
        
        df_consumo = pd.DataFrame(variaciones_consumo)
        st.dataframe(df_consumo, width='stretch', hide_index=True)
        
        # Análisis de variación de autonomía
        st.subheader("Variación de Autonomía")
        
        variaciones_autonomia = []
        for var in [-variacion, -variacion//2, 0, variacion//2, variacion]:
            autonomia_var = autonomia_base * (1 + var/100)
            resultado = calcular_sistema(consumo_base, autonomia_var)
            variaciones_autonomia.append({
                'Variación (%)': f"{var:+.0f}%",
                'Autonomía (km)': f"{autonomia_var:.0f}",
                'Energía (MJ)': f"{resultado['energia']:.0f}",
                'Masa CH₄ (kg)': f"{resultado['masa_ch4']:.2f}",
                'Volumen (m³)': f"{resultado['volumen']:.2f}",
                'N° Tanques': resultado['tanques'],
                'Peso (kg)': f"{resultado['peso']:.0f}"
            })
        
        df_autonomia = pd.DataFrame(variaciones_autonomia)
        st.dataframe(df_autonomia, width='stretch', hide_index=True)
        
        # Gráficos de sensibilidad
        st.subheader("Visualización de Sensibilidad")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Gráfico de consumo vs número de tanques
            try:
                consumos = [consumo_base * (1 + v/100) for v in [-variacion, -variacion//2, 0, variacion//2, variacion]]
                tanques_consumo = [calcular_sistema(c, autonomia_base)['tanques'] for c in consumos]
                
                # Validar que todos los valores sean finitos y válidos
                datos_validos = [(c, t) for c, t in zip(consumos, tanques_consumo) 
                               if math.isfinite(c) and c > 0 and c < 1000 and 
                                  math.isfinite(t) and t > 0 and t < 1000]
                consumos_validos = [c for c, t in datos_validos]
                tanques_validos = [t for c, t in datos_validos]
                
                # Necesitamos al menos 2 puntos para un gráfico de línea
                if len(consumos_validos) >= 2 and len(tanques_validos) >= 2:
                    # Asegurar que los arrays tengan la misma longitud
                    min_len = min(len(consumos_validos), len(tanques_validos))
                    consumos_validos = consumos_validos[:min_len]
                    tanques_validos = tanques_validos[:min_len]
                    
                    chart_data_consumo = pd.DataFrame({
                        'Consumo (L/100km)': consumos_validos,
                        'N° Tanques': tanques_validos
                    })
                    # Verificar que el DataFrame no esté vacío y tenga valores válidos
                    if not chart_data_consumo.empty and chart_data_consumo['N° Tanques'].min() > 0:
                        st.line_chart(chart_data_consumo, x='Consumo (L/100km)', y='N° Tanques')
                    else:
                        st.warning("⚠️ No hay suficientes datos válidos para generar el gráfico de consumo")
                else:
                    st.warning("⚠️ Se requieren al menos 2 puntos de datos válidos para generar el gráfico")
            except Exception as e:
                st.error(f"Error al generar gráfico de consumo: {str(e)}")
        
        with chart_col2:
            # Gráfico de autonomía vs número de tanques
            try:
                autonomias = [autonomia_base * (1 + v/100) for v in [-variacion, -variacion//2, 0, variacion//2, variacion]]
                tanques_autonomia = [calcular_sistema(consumo_base, a)['tanques'] for a in autonomias]
                
                # Validar que todos los valores sean finitos y válidos
                datos_validos_auto = [(a, t) for a, t in zip(autonomias, tanques_autonomia) 
                                     if math.isfinite(a) and a > 0 and a < 10000 and 
                                        math.isfinite(t) and t > 0 and t < 1000]
                autonomias_validas = [a for a, t in datos_validos_auto]
                tanques_validos_auto = [t for a, t in datos_validos_auto]
                
                # Necesitamos al menos 2 puntos para un gráfico de línea
                if len(autonomias_validas) >= 2 and len(tanques_validos_auto) >= 2:
                    # Asegurar que los arrays tengan la misma longitud
                    min_len = min(len(autonomias_validas), len(tanques_validos_auto))
                    autonomias_validas = autonomias_validas[:min_len]
                    tanques_validos_auto = tanques_validos_auto[:min_len]
                    
                    chart_data_autonomia = pd.DataFrame({
                        'Autonomía (km)': autonomias_validas,
                        'N° Tanques': tanques_validos_auto
                    })
                    # Verificar que el DataFrame no esté vacío y tenga valores válidos
                    if not chart_data_autonomia.empty and chart_data_autonomia['N° Tanques'].min() > 0:
                        st.line_chart(chart_data_autonomia, x='Autonomía (km)', y='N° Tanques')
                    else:
                        st.warning("⚠️ No hay suficientes datos válidos para generar el gráfico de autonomía")
                else:
                    st.warning("⚠️ Se requieren al menos 2 puntos de datos válidos para generar el gráfico")
            except Exception as e:
                st.error(f"Error al generar gráfico de autonomía: {str(e)}")

# ============================================
# TAB: MANIFEST DEL PROYECTO
# ============================================
with tabs[TAB_MANIFEST]:
    st.header("📋 Manifest del Proyecto")
    
    manifest_data = load_manifest()
    
    if manifest_data:
        # Mostrar información del proyecto
        if 'project' in manifest_data:
            project = manifest_data['project']
            st.subheader("📌 Información del Proyecto")
            col_proj1, col_proj2 = st.columns(2)
            
            with col_proj1:
                st.markdown(f"""
                **Nombre:** {project.get('name', 'N/A')}  
                **Cliente:** {project.get('client', 'N/A')}  
                **Versión:** {project.get('version', 'N/A')}
                """)
            
            with col_proj2:
                st.markdown(f"""
                **Fecha de Creación:** {project.get('date_created', 'N/A')}  
                **Estado:** {project.get('status', 'N/A')}  
                **Ingeniero:** {project.get('engineer', 'N/A')}
                """)
        
        # Deliverables
        if 'deliverables' in manifest_data:
            st.markdown("---")
            st.subheader("📦 Entregables")
            
            if st.session_state.get('user_role') == 'Administrador':
                st.info("👤 **Modo Administrador:** Puede descargar los archivos de entregables si están disponibles en el sistema.")
            
            deliverables = manifest_data['deliverables']
            for key, value in deliverables.items():
                if isinstance(value, dict):
                    filename = value.get('filename', key)
                    file_status = value.get('status', 'N/A')
                    
                    with st.expander(f"📄 {filename} - {file_status}"):
                        st.markdown(f"**Formato:** {value.get('format', 'N/A')}")
                        st.markdown(f"**Descripción:** {value.get('description', 'N/A')}")
                        if 'sections' in value:
                            st.markdown("**Secciones incluidas:**")
                            for section in value['sections']:
                                st.markdown(f"- {section}")
                        
                        # Verificar si el archivo existe y permitir descarga (solo administradores)
                        if st.session_state.get('user_role') == 'Administrador':
                            # Solo permitir descarga de archivos en formato PDF y HTML
                            file_ext = os.path.splitext(filename)[1].lower()
                            
                            # Mapear nombres de archivos a rutas completas
                            # NOTA: Se entregan archivos en formato HTML, PDF y Excel
                            file_mapping = {
                                'PETROLIQUIDOS_GNV_Informe_v1.pdf': DELIVERABLE_MD,  # Se convertirá a PDF desde MD
                                'PETROLIQUIDOS_GNV_Informe_v1.html': DELIVERABLE_MD,  # Se convertirá a HTML desde MD
                                'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_FINAL.pdf': DELIVERABLE_PDF,
                                'PETROLIQUIDOS_GNV_PID_v1.pdf': DELIVERABLE_PDF,  # Fallback al PDF en assets
                                'PETROLIQUIDOS_GNV_manifest_v1.pdf': MANIFEST_FILE,  # Se convertirá a PDF desde JSON
                                'PETROLIQUIDOS_GNV_BOM_v1.xlsx': DELIVERABLE_XLSX  # Archivo Excel BOM
                            }
                            
                            # Verificar tipo de archivo y permitir descarga
                            if file_ext == '.pdf':
                                # Buscar el archivo PDF correspondiente
                                if filename in file_mapping:
                                    source_file = file_mapping[filename]
                                    
                                    # Si el archivo fuente es .md, generar PDF y HTML
                                    if source_file == DELIVERABLE_MD and file_exists(DELIVERABLE_MD):
                                        try:
                                            # Generar HTML desde Markdown
                                            html_content, _ = procesar_archivo_md(
                                                Path(DELIVERABLE_MD),
                                                titulo="Informe Técnico Sistema GNV - PETROLIQUIDOS"
                                            )
                                            
                                            # Generar PDF desde HTML
                                            pdf_data, pdf_error = generar_pdf_desde_html(html_content)
                                            
                                            if pdf_data:
                                                # Botón para descargar PDF
                                                b64_pdf = base64.b64encode(pdf_data).decode()
                                                nombre_pdf = filename if filename.endswith('.pdf') else filename.replace('.md', '.pdf')
                                                href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{nombre_pdf}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;">📄 Descargar PDF</a>'
                                                st.markdown(href_pdf, unsafe_allow_html=True)
                                            
                                            # Botón para descargar HTML
                                            b64_html = base64.b64encode(html_content.encode('utf-8')).decode()
                                            nombre_html = filename.replace('.pdf', '.html')
                                            href_html = f'<a href="data:text/html;charset=utf-8;base64,{b64_html}" download="{nombre_html}" style="background-color: #2AA1FF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 Descargar HTML</a>'
                                            st.markdown(href_html, unsafe_allow_html=True)
                                            
                                        except Exception as e:
                                            st.error(f"Error al generar archivos desde Markdown: {str(e)}")
                                    # Si es un PDF directo (diagrama)
                                    elif source_file == DELIVERABLE_PDF and file_exists(DELIVERABLE_PDF):
                                        download_link = create_download_link(DELIVERABLE_PDF, f"📄 Descargar {filename} (PDF)", "default")
                                        if download_link:
                                            st.markdown(download_link, unsafe_allow_html=True)
                                        else:
                                            st.error(f"Error al crear enlace de descarga para {filename}")
                                    # Si es el manifest, generar PDF y HTML
                                    elif source_file == MANIFEST_FILE and file_exists(MANIFEST_FILE):
                                        try:
                                            # Leer manifest JSON
                                            with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
                                                manifest_data = json.load(f)
                                            
                                            # Generar HTML del manifest
                                            html_manifest = generate_manifest_html(manifest_data)
                                            
                                            # Generar PDF desde HTML
                                            pdf_data, pdf_error = generar_pdf_desde_html(html_manifest)
                                            
                                            if pdf_data:
                                                # Botón para descargar PDF
                                                b64_pdf = base64.b64encode(pdf_data).decode()
                                                href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;">📄 Descargar PDF</a>'
                                                st.markdown(href_pdf, unsafe_allow_html=True)
                                            
                                            # Botón para descargar HTML
                                            b64_html = base64.b64encode(html_manifest.encode('utf-8')).decode()
                                            nombre_html = filename.replace('.pdf', '.html')
                                            href_html = f'<a href="data:text/html;charset=utf-8;base64,{b64_html}" download="{nombre_html}" style="background-color: #2AA1FF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 Descargar HTML</a>'
                                            st.markdown(href_html, unsafe_allow_html=True)
                                            
                                        except Exception as e:
                                            st.error(f"Error al generar archivos desde Manifest: {str(e)}")
                                    else:
                                        st.warning(f"⚠️ El archivo fuente para '{filename}' no se encuentra en el sistema.")
                                else:
                                    st.info(f"ℹ️ El archivo '{filename}' no está disponible para descarga.")
                            elif file_ext == '.xlsx':
                                # Manejar archivos Excel
                                if filename in file_mapping:
                                    source_file = file_mapping[filename]
                                    
                                    if source_file == DELIVERABLE_XLSX and file_exists(DELIVERABLE_XLSX):
                                        download_link = create_download_link(
                                            DELIVERABLE_XLSX, 
                                            f"📊 Descargar {filename} (Excel)", 
                                            "default"
                                        )
                                        if download_link:
                                            st.markdown(download_link, unsafe_allow_html=True)
                                        else:
                                            st.error(f"Error al crear enlace de descarga para {filename}")
                                    else:
                                        st.warning(f"⚠️ El archivo fuente para '{filename}' no se encuentra en el sistema.")
                                else:
                                    st.info(f"ℹ️ El archivo '{filename}' no está disponible para descarga.")
                            else:
                                # Si no es PDF ni Excel, informar formatos disponibles
                                st.info(f"ℹ️ Solo se entregan archivos en formato HTML, PDF y Excel. '{filename}' no está disponible para descarga.")
        
        # Parámetros Técnicos
        if 'technical_parameters' in manifest_data:
            st.markdown("---")
            st.subheader("⚙️ Parámetros Técnicos")
            
            tech_params = manifest_data['technical_parameters']
            
            if 'pressure_ranges' in tech_params:
                st.markdown("#### Rangos de Presión")
                pressure_ranges = tech_params['pressure_ranges']
                
                col_p1, col_p2, col_p3 = st.columns(3)
                
                with col_p1:
                    if 'tank_filling' in pressure_ranges:
                        tf = pressure_ranges['tank_filling']
                        st.info(f"""
                        **Llenado de Tanques**  
                        {tf.get('min', 'N/A')}-{tf.get('max', 'N/A')} {tf.get('unit', 'bar')}
                        """)
                
                with col_p2:
                    if 'stage1_regulator' in pressure_ranges:
                        s1 = pressure_ranges['stage1_regulator']
                        st.info(f"""
                        **Regulador 1ra Etapa**  
                        {s1.get('input', {}).get('min', 'N/A')}-{s1.get('input', {}).get('max', 'N/A')} bar  
                        → {s1.get('output', {}).get('min', 'N/A')}-{s1.get('output', {}).get('max', 'N/A')} bar
                        """)
                
                with col_p3:
                    if 'stage2_regulator' in pressure_ranges:
                        s2 = pressure_ranges['stage2_regulator']
                        st.info(f"""
                        **Regulador 2da Etapa**  
                        {s2.get('input', {}).get('min', 'N/A')}-{s2.get('input', {}).get('max', 'N/A')} bar  
                        → {s2.get('output', {}).get('min', 'N/A')}-{s2.get('output', {}).get('max', 'N/A')} bar
                        """)
        
        # Regulaciones
        if 'regulations_compliance' in manifest_data:
            st.markdown("---")
            st.subheader("📜 Cumplimiento de Regulaciones")
            
            regulations = manifest_data['regulations_compliance']
            
            if 'national_colombia' in regulations:
                st.markdown("##### Regulaciones Nacionales (Colombia)")
                for reg in regulations['national_colombia']:
                    with st.expander(f"📋 {reg.get('code', 'N/A')} - {reg.get('title', 'N/A')}"):
                        st.markdown(f"**Estado:** {reg.get('status', 'N/A')}")
                        if reg.get('requirements'):
                            st.markdown("**Requisitos:**")
                            for req in reg['requirements']:
                                st.markdown(f"- {req}")
            
            if 'international' in regulations:
                st.markdown("##### Regulaciones Internacionales")
                for reg in regulations['international']:
                    with st.expander(f"🌍 {reg.get('code', 'N/A')} - {reg.get('title', 'N/A')}"):
                        st.markdown(f"**Estado:** {reg.get('status', 'N/A')}")
                        if reg.get('requirements'):
                            st.markdown("**Requisitos:**")
                            for req in reg['requirements']:
                                st.markdown(f"- {req}")
        
        # Riesgos
        if 'risks_identified' in manifest_data:
            st.markdown("---")
            st.subheader("⚠️ Riesgos Identificados")
            
            risks = manifest_data['risks_identified']
            risks_df = pd.DataFrame(risks)
            st.dataframe(risks_df, width='stretch', hide_index=True)
        
        # Decisiones Pendientes - Formularios Interactivos
        if 'pending_decisions' in manifest_data:
            st.markdown("---")
            st.subheader("❓ Decisiones Pendientes - Formulario de Respuestas")
            
            decisions = manifest_data['pending_decisions']
            
            # Inicializar respuestas en session_state si no existen
            if 'decisiones_respuestas' not in st.session_state:
                st.session_state['decisiones_respuestas'] = {}
            
            # Crear tabs para cada decisión de alta prioridad
            if 'high_priority' in decisions and decisions['high_priority']:
                st.markdown("#### 🔴 Decisiones de Alta Prioridad")
                st.info("Por favor, complete los siguientes formularios. Sus respuestas ayudarán a definir el alcance final del proyecto.")
                
                # Crear tabs para cada decisión
                decision_tabs = st.tabs([f"📋 {i+1}. {d.get('question', 'Pregunta')[:30]}..." for i, d in enumerate(decisions['high_priority'])])
                
                for idx, (decision, tab) in enumerate(zip(decisions['high_priority'], decision_tabs)):
                    with tab:
                        question_id = f"high_{idx}"
                        question = decision.get('question', '')
                        impact = decision.get('impact', '')
                        
                        st.markdown(f"### {question}")
                        st.caption(f"**Impacto:** {impact}")
                        
                        # Formulario específico según la pregunta
                        with st.form(f"form_decision_{question_id}"):
                            if "Modelos específicos" in question or "marca" in question.lower():
                                st.markdown("#### Información del Vehículo")
                                col_v1, col_v2 = st.columns(2)
                                with col_v1:
                                    marca = st.text_input("🏭 Marca del Vehículo", 
                                                        value=st.session_state['decisiones_respuestas'].get(f"{question_id}_marca", ""),
                                                        help="Ejemplo: Volvo, Scania, Mercedes-Benz")
                                    modelo = st.text_input("🚛 Modelo del Vehículo",
                                                         value=st.session_state['decisiones_respuestas'].get(f"{question_id}_modelo", ""),
                                                         help="Ejemplo: FH16, R450, Actros")
                                with col_v2:
                                    año = st.number_input("📅 Año del Vehículo",
                                                         min_value=2000,
                                                         max_value=2030,
                                                         value=st.session_state['decisiones_respuestas'].get(f"{question_id}_año", 2024),
                                                         step=1)
                                    cantidad = st.number_input("🔢 Cantidad de Vehículos",
                                                              min_value=1,
                                                              max_value=100,
                                                              value=st.session_state['decisiones_respuestas'].get(f"{question_id}_cantidad", 1),
                                                              step=1)
                                
                                observaciones = st.text_area("📝 Observaciones Adicionales",
                                                            value=st.session_state['decisiones_respuestas'].get(f"{question_id}_observaciones", ""),
                                                            help="Cualquier información adicional sobre los vehículos (configuración, motor, etc.)",
                                                            height=100)
                                
                                if st.form_submit_button("💾 Guardar Respuesta"):
                                    st.session_state['decisiones_respuestas'][f"{question_id}_marca"] = marca
                                    st.session_state['decisiones_respuestas'][f"{question_id}_modelo"] = modelo
                                    st.session_state['decisiones_respuestas'][f"{question_id}_año"] = año
                                    st.session_state['decisiones_respuestas'][f"{question_id}_cantidad"] = cantidad
                                    st.session_state['decisiones_respuestas'][f"{question_id}_observaciones"] = observaciones
                                    st.session_state['decisiones_respuestas'][f"{question_id}_estado"] = "Respondido"
                                    st.success("✅ Respuesta guardada correctamente")
                            
                            elif "Presupuesto" in question or "presupuesto" in question.lower():
                                st.markdown("#### Presupuesto por Unidad")
                                st.info("💡 Esta información nos ayudará a seleccionar los componentes más adecuados para su proyecto.")
                                
                                presupuesto_usd = st.number_input("💰 Presupuesto Máximo por Unidad (USD)",
                                                                 min_value=0.0,
                                                                 max_value=1000000.0,
                                                                 value=float(st.session_state['decisiones_respuestas'].get(f"{question_id}_presupuesto_usd", 0)),
                                                                 step=1000.0,
                                                                 format="%.0f",
                                                                 help="Presupuesto máximo disponible por cada vehículo convertido")
                                
                                presupuesto_cop = st.number_input("💰 Presupuesto Máximo por Unidad (COP)",
                                                                 min_value=0.0,
                                                                 max_value=5000000000.0,
                                                                 value=float(st.session_state['decisiones_respuestas'].get(f"{question_id}_presupuesto_cop", 0)),
                                                                 step=100000.0,
                                                                 format="%.0f")
                                
                                preferencia = st.radio("🎯 Prioridad del Presupuesto",
                                                      ["Costo mínimo", "Balance costo-beneficio", "Calidad/prestaciones máximas"],
                                                      index=st.session_state['decisiones_respuestas'].get(f"{question_id}_preferencia", 1) if isinstance(st.session_state['decisiones_respuestas'].get(f"{question_id}_preferencia"), int) else 1,
                                                      help="¿Qué es más importante para su proyecto?")
                                
                                observaciones = st.text_area("📝 Observaciones",
                                                            value=st.session_state['decisiones_respuestas'].get(f"{question_id}_observaciones", ""),
                                                            help="Restricciones presupuestarias adicionales o consideraciones especiales",
                                                            height=100)
                                
                                if st.form_submit_button("💾 Guardar Respuesta"):
                                    st.session_state['decisiones_respuestas'][f"{question_id}_presupuesto_usd"] = presupuesto_usd
                                    st.session_state['decisiones_respuestas'][f"{question_id}_presupuesto_cop"] = presupuesto_cop
                                    st.session_state['decisiones_respuestas'][f"{question_id}_preferencia"] = preferencia
                                    st.session_state['decisiones_respuestas'][f"{question_id}_observaciones"] = observaciones
                                    st.session_state['decisiones_respuestas'][f"{question_id}_estado"] = "Respondido"
                                    st.success("✅ Respuesta guardada correctamente")
                            
                            elif "Perfil operativo" in question or "operativo" in question.lower():
                                st.markdown("#### Perfil de Operación de la Flota")
                                st.info("💡 Esta información nos ayudará a dimensionar correctamente el sistema según su uso real.")
                                
                                col_op1, col_op2 = st.columns(2)
                                with col_op1:
                                    km_dia = st.number_input("📏 Kilómetros Recorridos por Día",
                                                           min_value=0.0,
                                                           max_value=2000.0,
                                                           value=float(st.session_state['decisiones_respuestas'].get(f"{question_id}_km_dia", 0)),
                                                           step=10.0,
                                                           help="Promedio de kilómetros recorridos diariamente")
                                    
                                    km_mes = st.number_input("📏 Kilómetros Recorridos por Mes",
                                                           min_value=0.0,
                                                           max_value=60000.0,
                                                           value=float(st.session_state['decisiones_respuestas'].get(f"{question_id}_km_mes", 0)),
                                                           step=100.0,
                                                           help="Total de kilómetros recorridos mensualmente")
                                
                                with col_op2:
                                    pct_carretera = st.slider("🛣️ Porcentaje en Carretera (%)",
                                                            min_value=0,
                                                            max_value=100,
                                                            value=st.session_state['decisiones_respuestas'].get(f"{question_id}_pct_carretera", 80),
                                                            step=5,
                                                            help="¿Qué porcentaje del tiempo operan en carretera?")
                                    
                                    pct_urbano = 100 - pct_carretera
                                    st.metric("🏙️ Porcentaje en Ciudad", f"{pct_urbano}%")
                                
                                altitud = st.slider("⛰️ Altitud Promedio de Operación (m.s.n.m.)",
                                                  min_value=0,
                                                  max_value=5000,
                                                  value=st.session_state['decisiones_respuestas'].get(f"{question_id}_altitud", 1000),
                                                  step=100,
                                                  help="La altitud afecta el rendimiento del motor")
                                
                                observaciones = st.text_area("📝 Observaciones",
                                                            value=st.session_state['decisiones_respuestas'].get(f"{question_id}_observaciones", ""),
                                                            help="Rutas principales, condiciones especiales de operación, etc.",
                                                            height=100)
                                
                                if st.form_submit_button("💾 Guardar Respuesta"):
                                    st.session_state['decisiones_respuestas'][f"{question_id}_km_dia"] = km_dia
                                    st.session_state['decisiones_respuestas'][f"{question_id}_km_mes"] = km_mes
                                    st.session_state['decisiones_respuestas'][f"{question_id}_pct_carretera"] = pct_carretera
                                    st.session_state['decisiones_respuestas'][f"{question_id}_altitud"] = altitud
                                    st.session_state['decisiones_respuestas'][f"{question_id}_observaciones"] = observaciones
                                    st.session_state['decisiones_respuestas'][f"{question_id}_estado"] = "Respondido"
                                    st.success("✅ Respuesta guardada correctamente")
                            
                            elif "Tipo de conversión" in question or "bi-fuel" in question.lower() or "dedicado" in question.lower():
                                st.markdown("#### Tipo de Sistema de Conversión")
                                st.info("💡 Elija el tipo de sistema según sus necesidades operativas.")
                                
                                tipo_conversion = st.radio("⚙️ Tipo de Conversión",
                                                          ["Bi-fuel (GNV + Diésel)", "Dedicado GNV (solo gas)"],
                                                          index=st.session_state['decisiones_respuestas'].get(f"{question_id}_tipo", 0) if isinstance(st.session_state['decisiones_respuestas'].get(f"{question_id}_tipo"), int) else 0,
                                                          help="Bi-fuel permite usar ambos combustibles, dedicado solo usa GNV")
                                
                                if tipo_conversion == "Bi-fuel (GNV + Diésel)":
                                    st.success("✅ **Ventajas:** Flexibilidad para usar diésel cuando no hay GNV disponible")
                                    modo_uso = st.selectbox("🔄 Modo de Uso Preferido",
                                                          ["Automático (cambia según disponibilidad)", "Manual (el conductor elige)", "Prioridad GNV (usa diésel solo si es necesario)"],
                                                          index=st.session_state['decisiones_respuestas'].get(f"{question_id}_modo_uso", 0) if isinstance(st.session_state['decisiones_respuestas'].get(f"{question_id}_modo_uso"), int) else 0)
                                else:
                                    st.info("ℹ️ **Ventajas:** Mayor eficiencia y menor complejidad del sistema")
                                    st.warning("⚠️ **Consideración:** Requiere disponibilidad confiable de estaciones GNV")
                                
                                razon = st.text_area("💭 Razón de la Elección",
                                                   value=st.session_state['decisiones_respuestas'].get(f"{question_id}_razon", ""),
                                                   help="Explique por qué prefiere este tipo de conversión",
                                                   height=100)
                                
                                observaciones = st.text_area("📝 Observaciones Adicionales",
                                                            value=st.session_state['decisiones_respuestas'].get(f"{question_id}_observaciones", ""),
                                                            height=100)
                                
                                if st.form_submit_button("💾 Guardar Respuesta"):
                                    st.session_state['decisiones_respuestas'][f"{question_id}_tipo"] = tipo_conversion
                                    if tipo_conversion == "Bi-fuel (GNV + Diésel)":
                                        st.session_state['decisiones_respuestas'][f"{question_id}_modo_uso"] = modo_uso
                                    st.session_state['decisiones_respuestas'][f"{question_id}_razon"] = razon
                                    st.session_state['decisiones_respuestas'][f"{question_id}_observaciones"] = observaciones
                                    st.session_state['decisiones_respuestas'][f"{question_id}_estado"] = "Respondido"
                                    st.success("✅ Respuesta guardada correctamente")
                            
                            elif "Plazo objetivo" in question or "plazo" in question.lower() or "piloto" in question.lower():
                                st.markdown("#### Cronograma del Proyecto")
                                st.info("💡 Esta información nos ayudará a planificar las actividades y priorizar tareas.")
                                
                                fecha_objetivo = st.date_input("📅 Fecha Objetivo para Primera Unidad Piloto",
                                                              value=st.session_state['decisiones_respuestas'].get(f"{question_id}_fecha", None) if st.session_state['decisiones_respuestas'].get(f"{question_id}_fecha") else None,
                                                              min_value=datetime.now().date(),
                                                              help="Fecha en la que desea tener la primera unidad convertida y funcionando")
                                
                                urgencia = st.radio("⏰ Nivel de Urgencia",
                                                   ["Baja (flexible)", "Media (importante pero negociable)", "Alta (fecha crítica)"],
                                                   index=st.session_state['decisiones_respuestas'].get(f"{question_id}_urgencia", 1) if isinstance(st.session_state['decisiones_respuestas'].get(f"{question_id}_urgencia"), int) else 1)
                                
                                unidades_piloto = st.number_input("🔢 Número de Unidades Piloto",
                                                                 min_value=1,
                                                                 max_value=10,
                                                                 value=st.session_state['decisiones_respuestas'].get(f"{question_id}_unidades", 1),
                                                                 step=1,
                                                                 help="¿Cuántas unidades desea convertir inicialmente como prueba?")
                                
                                observaciones = st.text_area("📝 Observaciones",
                                                            value=st.session_state['decisiones_respuestas'].get(f"{question_id}_observaciones", ""),
                                                            help="Restricciones de tiempo, eventos importantes, dependencias, etc.",
                                                            height=100)
                                
                                if st.form_submit_button("💾 Guardar Respuesta"):
                                    if fecha_objetivo:
                                        st.session_state['decisiones_respuestas'][f"{question_id}_fecha"] = fecha_objetivo.isoformat()
                                    st.session_state['decisiones_respuestas'][f"{question_id}_urgencia"] = urgencia
                                    st.session_state['decisiones_respuestas'][f"{question_id}_unidades"] = unidades_piloto
                                    st.session_state['decisiones_respuestas'][f"{question_id}_observaciones"] = observaciones
                                    st.session_state['decisiones_respuestas'][f"{question_id}_estado"] = "Respondido"
                                    st.success("✅ Respuesta guardada correctamente")
                            
                            else:
                                # Formulario genérico para otras preguntas
                                respuesta = st.text_area("✍️ Su Respuesta",
                                                        value=st.session_state['decisiones_respuestas'].get(f"{question_id}_respuesta", ""),
                                                        height=150,
                                                        help="Por favor, proporcione información detallada")
                                
                                observaciones = st.text_area("📝 Observaciones Adicionales",
                                                            value=st.session_state['decisiones_respuestas'].get(f"{question_id}_observaciones", ""),
                                                            height=100)
                                
                                if st.form_submit_button("💾 Guardar Respuesta"):
                                    st.session_state['decisiones_respuestas'][f"{question_id}_respuesta"] = respuesta
                                    st.session_state['decisiones_respuestas'][f"{question_id}_observaciones"] = observaciones
                                    st.session_state['decisiones_respuestas'][f"{question_id}_estado"] = "Respondido"
                                    st.success("✅ Respuesta guardada correctamente")
                        
                        # Mostrar resumen de respuesta guardada si existe
                        if st.session_state['decisiones_respuestas'].get(f"{question_id}_estado") == "Respondido":
                            st.markdown("---")
                            st.success("✅ **Respuesta guardada** - Esta decisión ha sido respondida")
            
            # Decisiones de prioridad media
            if 'medium_priority' in decisions and decisions['medium_priority']:
                st.markdown("---")
                st.markdown("#### 🟡 Decisiones de Prioridad Media")
                
                for decision in decisions['medium_priority']:
                    with st.expander(f"📋 {decision.get('question', 'N/A')}"):
                        st.info(f"**Impacto:** {decision.get('impact', 'N/A')}")
                        st.caption(f"**Estado:** {decision.get('status', 'N/A')}")
                        
                        # Formulario simple para prioridad media
                        question_id_med = f"med_{decision.get('question', '')[:20]}"
                        with st.form(f"form_med_{question_id_med}"):
                            respuesta_med = st.text_area("✍️ Su Respuesta",
                                                          value=st.session_state['decisiones_respuestas'].get(f"{question_id_med}_respuesta", ""),
                                                          height=100)
                            if st.form_submit_button("💾 Guardar"):
                                st.session_state['decisiones_respuestas'][f"{question_id_med}_respuesta"] = respuesta_med
                                st.session_state['decisiones_respuestas'][f"{question_id_med}_estado"] = "Respondido"
                                st.success("✅ Respuesta guardada")
            
            # Botón para descargar decisiones pendientes en HTML
            if st.session_state.get('decisiones_respuestas'):
                st.markdown("---")
                st.subheader("⬇️ Descargar Decisiones Pendientes en HTML")
                
                from datetime import datetime
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Generar HTML de decisiones pendientes
                html_decisiones = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="utf-8">
                <title>Decisiones Pendientes - {st.session_state.get('proyecto_cliente', 'PETROLIQUIDOS')}</title>
                <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 900px;
                    margin: 40px auto;
                    padding: 20px;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    border-bottom: 3px solid #FF7A00;
                    padding-bottom: 15px;
                    margin-bottom: 30px;
                }}
                h1 {{
                    color: #0F1216;
                    margin: 0;
                    font-size: 24pt;
                }}
                h2 {{
                    color: #124272;
                    border-bottom: 2px solid #2AA1FF;
                    padding-bottom: 8px;
                    margin-top: 30px;
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
                }}
                .decision-box {{
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 15px 0;
                }}
                .decision-box.high-priority {{
                    border-left: 5px solid #dc3545;
                }}
                .decision-box.medium-priority {{
                    border-left: 5px solid #ffc107;
                }}
                .response-box {{
                    background-color: #e7f3ff;
                    border-left: 4px solid #2AA1FF;
                    padding: 12px;
                    margin: 10px 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                    font-family: Arial;
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
                .valor-destacado {{
                    font-weight: bold;
                    color: #0F1216;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 0.9em;
                    color: #6B7280;
                    text-align: center;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 0.9em;
                    font-weight: bold;
                }}
                .status-respondido {{
                    background-color: #d4edda;
                    color: #155724;
                }}
                .status-pendiente {{
                    background-color: #fff3cd;
                    color: #856404;
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
                    <h1>Decisiones Pendientes - Formulario de Respuestas</h1>
                    <p><strong>Cliente:</strong> {st.session_state.get('proyecto_cliente', 'PETROLIQUIDOS')}<br>
                    <strong>Versión:</strong> {st.session_state.get('proyecto_version', 'v1')}<br>
                    <strong>Fecha del Proyecto:</strong> {st.session_state.get('proyecto_fecha', 'N/A')}<br>
                    <strong>Fecha de Generación:</strong> {fecha_actual}</p>
                </div>
                """
                
                # Agregar decisiones de alta prioridad
                if 'pending_decisions' in manifest_data and 'high_priority' in manifest_data['pending_decisions']:
                    html_decisiones += "<h2>🔴 Decisiones de Alta Prioridad</h2>"
                    for idx, decision in enumerate(manifest_data['pending_decisions']['high_priority']):
                        question_id = f"high_{idx}"
                        estado = st.session_state['decisiones_respuestas'].get(f"{question_id}_estado", "Pendiente")
                        status_class = "status-respondido" if estado == "Respondido" else "status-pendiente"
                        
                        html_decisiones += f"""
                        <div class="decision-box high-priority">
                            <h3>{idx+1}. {decision.get('question', 'N/A')}</h3>
                            <p><strong>Impacto:</strong> {decision.get('impact', 'N/A')}</p>
                            <p><strong>Estado:</strong> <span class="status-badge {status_class}">{estado}</span></p>
                        """
                        
                        # Agregar respuestas guardadas
                        if estado == "Respondido":
                            html_decisiones += '<div class="response-box"><strong>Respuestas Guardadas:</strong><ul>'
                            
                            # Verificar qué tipo de respuesta es
                            if st.session_state['decisiones_respuestas'].get(f"{question_id}_marca"):
                                html_decisiones += f"<li><strong>Marca:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_marca', 'N/A')}</li>"
                                html_decisiones += f"<li><strong>Modelo:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_modelo', 'N/A')}</li>"
                                html_decisiones += f"<li><strong>Año:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_año', 'N/A')}</li>"
                                html_decisiones += f"<li><strong>Cantidad:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_cantidad', 'N/A')}</li>"
                            
                            if st.session_state['decisiones_respuestas'].get(f"{question_id}_presupuesto_usd"):
                                html_decisiones += f"<li><strong>Presupuesto USD:</strong> ${st.session_state['decisiones_respuestas'].get(f'{question_id}_presupuesto_usd', 0):,.0f}</li>"
                                html_decisiones += f"<li><strong>Presupuesto COP:</strong> ${st.session_state['decisiones_respuestas'].get(f'{question_id}_presupuesto_cop', 0):,.0f}</li>"
                                html_decisiones += f"<li><strong>Prioridad:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_preferencia', 'N/A')}</li>"
                            
                            if st.session_state['decisiones_respuestas'].get(f"{question_id}_km_dia"):
                                html_decisiones += f"<li><strong>Km/día:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_km_dia', 0):,.0f}</li>"
                                html_decisiones += f"<li><strong>Km/mes:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_km_mes', 0):,.0f}</li>"
                                html_decisiones += f"<li><strong>% Carretera:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_pct_carretera', 0)}%</li>"
                                html_decisiones += f"<li><strong>Altitud:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_altitud', 0)} m.s.n.m.</li>"
                            
                            if st.session_state['decisiones_respuestas'].get(f"{question_id}_tipo"):
                                html_decisiones += f"<li><strong>Tipo de Conversión:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_tipo', 'N/A')}</li>"
                                if st.session_state['decisiones_respuestas'].get(f"{question_id}_modo_uso"):
                                    html_decisiones += f"<li><strong>Modo de Uso:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_modo_uso', 'N/A')}</li>"
                            
                            if st.session_state['decisiones_respuestas'].get(f"{question_id}_fecha"):
                                html_decisiones += f"<li><strong>Fecha Objetivo:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_fecha', 'N/A')}</li>"
                                html_decisiones += f"<li><strong>Urgencia:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_urgencia', 'N/A')}</li>"
                                html_decisiones += f"<li><strong>Unidades Piloto:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_unidades', 'N/A')}</li>"
                            
                            if st.session_state['decisiones_respuestas'].get(f"{question_id}_respuesta"):
                                html_decisiones += f"<li><strong>Respuesta:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_respuesta', 'N/A')}</li>"
                            
                            if st.session_state['decisiones_respuestas'].get(f"{question_id}_observaciones"):
                                html_decisiones += f"<li><strong>Observaciones:</strong> {st.session_state['decisiones_respuestas'].get(f'{question_id}_observaciones', 'N/A')}</li>"
                            
                            html_decisiones += '</ul></div>'
                        
                        html_decisiones += "</div>"
                
                # Agregar decisiones de prioridad media
                if 'pending_decisions' in manifest_data and 'medium_priority' in manifest_data['pending_decisions']:
                    html_decisiones += "<h2>🟡 Decisiones de Prioridad Media</h2>"
                    for decision in manifest_data['pending_decisions']['medium_priority']:
                        question_id_med = f"med_{decision.get('question', '')[:20]}"
                        estado = st.session_state['decisiones_respuestas'].get(f"{question_id_med}_estado", "Pendiente")
                        status_class = "status-respondido" if estado == "Respondido" else "status-pendiente"
                        
                        html_decisiones += f"""
                        <div class="decision-box medium-priority">
                            <h3>{decision.get('question', 'N/A')}</h3>
                            <p><strong>Impacto:</strong> {decision.get('impact', 'N/A')}</p>
                            <p><strong>Estado:</strong> <span class="status-badge {status_class}">{estado}</span></p>
                        """
                        
                        if estado == "Respondido" and st.session_state['decisiones_respuestas'].get(f"{question_id_med}_respuesta"):
                            html_decisiones += f"""
                            <div class="response-box">
                                <strong>Respuesta:</strong><br>
                                {st.session_state['decisiones_respuestas'].get(f'{question_id_med}_respuesta', 'N/A')}
                            </div>
                            """
                        
                        html_decisiones += "</div>"
                
                # Footer
                html_decisiones += f"""
                <div class="footer">
                    <p><strong>DECISIONES PENDIENTES - FORMULARIO DE RESPUESTAS</strong></p>
                    <p>Este documento contiene las decisiones pendientes y las respuestas proporcionadas por el cliente.<br>
                    <em>Confidencial - Uso exclusivo del cliente {st.session_state.get('proyecto_cliente', 'PETROLIQUIDOS')}</em></p>
                    <p><small>Versión {st.session_state.get('proyecto_version', 'v1')} | Generado el {fecha_actual}</small></p>
                </div>
                </body>
                </html>
                """
                
                import base64
                b64_decisiones = base64.b64encode(html_decisiones.encode('utf-8')).decode()
                cliente_nombre = st.session_state.get('proyecto_cliente', 'PETROLIQUIDOS')
                fecha_descarga = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo_html = f"decisiones_pendientes_{cliente_nombre}_{fecha_descarga}.html"
                href_decisiones = f'<a href="data:text/html;charset=utf-8;base64,{b64_decisiones}" download="{nombre_archivo_html}" style="background-color: #FF7A00; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;">📥 Descargar Decisiones Pendientes en HTML</a>'
                st.markdown(href_decisiones, unsafe_allow_html=True)
                
                # Botón para generar PDF
                try:
                    from weasyprint import HTML
                    from io import BytesIO
                    
                    # Generar PDF desde HTML
                    pdf_buffer = BytesIO()
                    HTML(string=html_decisiones).write_pdf(pdf_buffer)
                    pdf_buffer.seek(0)
                    pdf_data = pdf_buffer.read()
                    b64_pdf = base64.b64encode(pdf_data).decode()
                    
                    nombre_archivo_pdf = f"decisiones_pendientes_{cliente_nombre}_{fecha_descarga}.pdf"
                    href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{nombre_archivo_pdf}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📄 Descargar Decisiones Pendientes en PDF</a>'
                    st.markdown(href_pdf, unsafe_allow_html=True)
                    
                except ImportError:
                    # Si weasyprint no está instalado, mostrar mensaje informativo
                    st.info("💡 **Para generar PDF:** Instale la librería `weasyprint` ejecutando: `pip install weasyprint`")
                except Exception as e:
                    st.warning(f"⚠️ No se pudo generar el PDF: {str(e)}")
                    st.info("💡 **Alternativa:** Descargue el HTML y conviértalo a PDF usando su navegador (Archivo > Imprimir > Guardar como PDF)")
                
                st.markdown("<br>", unsafe_allow_html=True)
        
        # Resumen de respuestas (solo para administradores)
        if st.session_state.get('user_role') == 'Administrador' and st.session_state.get('decisiones_respuestas'):
            st.markdown("---")
            st.subheader("📊 Resumen de Respuestas del Cliente")
            with st.expander("👁️ Ver todas las respuestas guardadas"):
                st.json(st.session_state['decisiones_respuestas'])
        
        # Costos
        if 'cost_estimates' in manifest_data:
            st.markdown("---")
            st.subheader("💰 Estimaciones de Costo")
            
            costs = manifest_data['cost_estimates']
            
            if 'breakdown' in costs:
                breakdown = costs['breakdown']
                col_cost1, col_cost2 = st.columns(2)
                
                with col_cost1:
                    st.metric("Subtotal Componentes (USD)", f"${breakdown.get('subtotal_components', {}).get('usd', 0):,.0f}")
                    st.metric("Contingencia (15%)", f"${breakdown.get('contingency', {}).get('usd', 0):,.0f}")
                    st.metric("Margen (20%)", f"${breakdown.get('margin', {}).get('usd', 0):,.0f}")
                
                with col_cost2:
                    total = breakdown.get('total_estimated', {})
                    st.metric("Total Estimado (USD)", f"${total.get('usd', 0):,.0f}")
                    st.metric("Total Estimado (COP)", f"${total.get('cop', 0):,.0f}")
                    st.caption(f"Tasa de cambio: {costs.get('exchange_rate', 'N/A')} COP/USD")
                
                # Visualización por porcentajes de sistemas
                if 'distribution_by_category' in breakdown:
                    st.markdown("#### Distribución de Costos por Sistema")
                    distribution = breakdown['distribution_by_category']
                    
                    if distribution:
                        try:
                            import plotly.express as px
                            
                            # Preparar datos para el gráfico
                            categorias = [cat.get('categoria', 'N/A') for cat in distribution]
                            porcentajes = [cat.get('porcentaje', 0) for cat in distribution]
                            totales_usd = [cat.get('total_usd', 0) for cat in distribution]
                            totales_cop = [cat.get('total_cop', 0) for cat in distribution]
                            
                            # Crear DataFrame
                            df_dist = pd.DataFrame({
                                'Categoría': categorias,
                                'Porcentaje (%)': porcentajes,
                                'Total USD': totales_usd,
                                'Total COP': totales_cop
                            })
                            
                            # Crear gráfico de barras horizontal
                            fig = px.bar(
                                df_dist,
                                x='Porcentaje (%)',
                                y='Categoría',
                                orientation='h',
                                text='Porcentaje (%)',
                                title='Distribución de Costos por Sistema',
                                labels={'Porcentaje (%)': 'Porcentaje (%)', 'Categoría': 'Sistema'},
                                hover_data={'Total USD': ':$,.0f', 'Total COP': ':,.0f'},
                                color='Porcentaje (%)',
                                color_continuous_scale='Blues'
                            )
                            
                            # Formatear el texto en las barras
                            fig.update_traces(
                                texttemplate='%{text:.2f}%',
                                textposition='outside'
                            )
                            
                            # Mejorar el layout
                            fig.update_layout(
                                height=400,
                                showlegend=False,
                                xaxis_title='Porcentaje del Total (%)',
                                yaxis_title='',
                                yaxis={'categoryorder': 'total ascending'}
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Mostrar tabla detallada
                            with st.expander("📊 Ver Detalles por Categoría"):
                                for cat in distribution:
                                    st.markdown(f"**{cat.get('categoria', 'N/A')}**")
                                    st.markdown(f"- Porcentaje: {cat.get('porcentaje', 0):.2f}%")
                                    st.markdown(f"- Total USD: ${cat.get('total_usd', 0):,.0f}")
                                    st.markdown(f"- Total COP: ${cat.get('total_cop', 0):,.0f}")
                                    if cat.get('componentes'):
                                        st.markdown(f"- Componentes: {len(cat['componentes'])}")
                                    st.markdown("---")
                        except ImportError:
                            st.warning("⚠️ Plotly no está disponible. Mostrando datos en tabla.")
                            # Fallback a tabla si plotly no está disponible
                            df_dist = pd.DataFrame(distribution)
                            st.dataframe(df_dist[['categoria', 'porcentaje', 'total_usd', 'total_cop']], 
                                       use_container_width=True, hide_index=True)
        
        # Próximos Pasos
        if 'next_steps' in manifest_data:
            st.markdown("---")
            st.subheader("📅 Próximos Pasos")
            
            steps = manifest_data['next_steps']
            for step in steps:
                priority_color = "🔴" if step.get('priority') == 'Alta' else "🟡" if step.get('priority') == 'Media' else "🟢"
                st.markdown(f"""
                {priority_color} **Paso {step.get('step', 'N/A')}:** {step.get('description', 'N/A')}  
                Prioridad: {step.get('priority', 'N/A')} | Duración estimada: {step.get('estimated_duration', 'N/A')}
                """)
        
        # Exportar Manifest (solo Administrador)
        if st.session_state.get('user_role') == 'Administrador':
            st.markdown("---")
            st.subheader("📥 Exportar Manifest Completo")
            
            # Integrar datos del cliente con el manifest
            manifest_export = manifest_data.copy()
            
            # Agregar datos del cliente al manifest
            if 'cliente_data' in st.session_state:
                manifest_export['cliente_data'] = {
                    "nombre": st.session_state['cliente_data']['nombre'],
                    "rol": st.session_state['cliente_data']['rol'],
                    "capacidad_de_la_flota": st.session_state['cliente_data']['capacidad_de_la_flota'],
                    "supuestos": st.session_state['cliente_data']['supuestos'],
                    "metadata": {
                        "fecha_creacion": st.session_state['cliente_data'].get('fecha_creacion', ''),
                        "fecha_ultima_actualizacion": st.session_state['cliente_data'].get('fecha_ultima_actualizacion', ''),
                        "usuario_creador": st.session_state['cliente_data'].get('usuario_creador', ''),
                        "usuario_ultima_actualizacion": st.session_state['cliente_data'].get('usuario_ultima_actualizacion', '')
                    }
                }
            
            # Generar HTML del manifest y luego PDF
            html_manifest = generate_manifest_html(manifest_export)
            
            # Generar JSON string para el expander (solo visualización)
            json_str = json.dumps(manifest_export, indent=2, ensure_ascii=False)
            
            # Generar PDF desde HTML
            pdf_data, error_msg = generar_pdf_desde_html(html_manifest)
            if pdf_data:
                b64_pdf = base64.b64encode(pdf_data).decode()
                nombre_archivo_pdf = f"manifest_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{nombre_archivo_pdf}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📄 Descargar Manifest en PDF</a>'
                st.markdown(href_pdf, unsafe_allow_html=True)
            else:
                # Fallback a HTML si no se puede generar PDF
                b64_html = base64.b64encode(html_manifest.encode('utf-8')).decode()
                href_html = f'<a href="data:text/html;charset=utf-8;base64,{b64_html}" download="manifest_completo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html" style="background-color: #FF7A00; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;">📥 Descargar Manifest HTML para Imprimir</a>'
                st.markdown(href_html, unsafe_allow_html=True)
                if error_msg:
                    st.warning(f"⚠️ No se pudo generar el PDF: {error_msg}")
                    st.info("💡 **Alternativa:** Se ha descargado el HTML. Puede convertirlo a PDF usando su navegador (Archivo > Imprimir > Guardar como PDF)")
            
            with st.expander("👁️ Ver Manifest JSON Completo"):
                st.code(json_str, language="json")
    else:
        st.warning(f"⚠️ No se encontró el archivo manifest. Asegúrese de que el archivo esté en: {MANIFEST_FILE}")
        st.info("💡 El manifest contiene información completa del proyecto: entregables, parámetros técnicos, regulaciones, riesgos, decisiones pendientes y costos.")

# ============================================
# TAB: INFORMACIÓN TÉCNICA
# ============================================
with tabs[TAB_INFO]:
    st.header("ℹ️ Información Técnica")

    st.markdown("""
    ## 1. Introducción y Relevancia

    Esta sección, además de brindar la información técnica de referencia, permite **generar informes de los resultados de cálculo** obtenidos en la aplicación, en formato HTML y PDF, útiles para reportes de ingeniería, presentaciones o para dejar respaldo documental del análisis realizado.

    ---
    """)

    # Botón para mostrar el informe de resultados de cálculos actuales en formato de ingeniería
    st.subheader("📄 Informe de Resultados de Cálculo (Modo Ingeniería)")
    if 'calculo_resultado' in st.session_state:
        resultado = st.session_state['calculo_resultado']
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        informe_markdown = f"""
### Resultados Principales del Sistema GNV

**Cliente:** {st.session_state['proyecto_cliente']}  
**Fecha de Generación:** {fecha_actual}  
**Versión:** {st.session_state['proyecto_version']}  
**Fecha del Proyecto:** {st.session_state['proyecto_fecha']}

---

#### Parámetros de Entrada

| Parámetro | Valor |
|-----------|-------|
| Consumo base | {resultado['consumo_base']:.2f} L/100km |
| Autonomía objetivo | {resultado['autonomia_objetivo']:.0f} km |
| Presión de llenado | {resultado['presion_llenado']:.0f} bar |
| Temperatura de operación | {resultado['temperatura']:.1f} °C |

---

#### Resultados del Cálculo

| Parámetro | Valor Calculado |
|-----------|------------------|
| **Volumen diésel equivalente** | {resultado['volumen_diesel_equivalente']:.2f} L |
| **Energía requerida** | {resultado['energia']:.2f} MJ |
| **Masa de CH₄ necesaria** | {resultado['masa_ch4']:.2f} kg |
| **Volumen de CH₄ requerido** | {resultado['volumen']:.2f} m³ ({resultado['volumen']*1000:.0f} L) |
| **Número de tanques recomendados** | **{resultado['tanques']} unidades** |
| **Peso adicional total** | **{resultado['peso']:.0f} kg ({resultado['peso']/1000:.2f} ton)** |

---

#### Análisis y Recomendaciones

{"⚠️ **ALERTA:** El peso adicional es significativo (>2000 kg). Considerar reducir la autonomía o usar tanques tipo 4 (más livianos)." if resultado['peso'] > 2000 else ""}

{"⚠️ **ALERTA:** Se requiere un número elevado de tanques (>25). Considerar tanques de mayor volumen o reducir autonomía." if resultado['tanques'] > 25 else ""}

**Notas importantes:**
- Los valores calculados están basados en los parámetros ingresados y deben validarse con datos reales del vehículo.
- El peso adicional de {resultado['peso']:.0f} kg puede afectar la capacidad de carga del vehículo.
- Se requieren {resultado['tanques']} tanques, lo que requiere validar disponibilidad de espacio en el chasis.
- Validar disponibilidad de estaciones GNV en las rutas operativas planificadas.

---

*Informe generado automáticamente por la aplicación "Cálculos Combustible Vehicular GNC/GNL"*  
*Confidencial - Uso exclusivo del cliente {st.session_state['proyecto_cliente']}*
"""
        st.markdown(informe_markdown)
        
        # Botón para copiar el informe
        st.markdown("---")
        st.code(informe_markdown, language="markdown")
    else:
        st.info("ℹ️ Ejecute un cálculo en la pestaña 'Cálculos principales' para mostrar aquí el informe de resultados de ingeniería.")

    # Opción de descarga en HTML como informe de ingeniería
    st.subheader("⬇️ Descargar Informe en HTML")
    if 'calculo_resultado' in st.session_state:
        resultado = st.session_state['calculo_resultado']
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_report = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <title>Informe de Cálculo Sistema GNV - PETROLIQUIDOS</title>
        <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            border-bottom: 3px solid #FF7A00;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #0F1216;
            margin: 0;
            font-size: 24pt;
        }}
        h2 {{
            color: #124272;
            border-bottom: 2px solid #2AA1FF;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        .info-box {{
            background-color: #f4f4f4;
            border-left: 4px solid #FF7A00;
            padding: 15px;
            margin: 20px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-family: Arial;
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
        .valor-destacado {{
            font-weight: bold;
            color: #0F1216;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
            color: #6B7280;
            text-align: center;
        }}
        .alerta {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            margin: 15px 0;
            border-radius: 4px;
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
            <h1>Informe de Cálculo de Sistema Vehicular GNV</h1>
            <p><strong>Cliente:</strong> {st.session_state['proyecto_cliente']}<br>
            <strong>Versión:</strong> {st.session_state['proyecto_version']}<br>
            <strong>Fecha del Proyecto:</strong> {st.session_state['proyecto_fecha']}<br>
            <strong>Fecha de Generación:</strong> {fecha_actual}</p>
        </div>
        
        <h2>Resultados Principales</h2>
        <table>
        <tr>
            <th>Parámetro</th>
            <th>Valor Calculado</th>
        </tr>
        <tr>
            <td><strong>Consumo Base</strong></td>
            <td class="valor-destacado">{resultado['consumo_base']:.2f} L/100km</td>
        </tr>
        <tr>
            <td><strong>Autonomía Objetivo</strong></td>
            <td class="valor-destacado">{resultado['autonomia_objetivo']:.0f} km</td>
        </tr>
        <tr>
            <td><strong>Volumen Diésel Equivalente</strong></td>
            <td>{resultado['volumen_diesel_equivalente']:.2f} L</td>
        </tr>
        <tr>
            <td><strong>Energía Requerida</strong></td>
            <td class="valor-destacado">{resultado['energia']:.2f} MJ</td>
        </tr>
        <tr>
            <td><strong>Masa de CH₄ Necesaria</strong></td>
            <td class="valor-destacado">{resultado['masa_ch4']:.2f} kg</td>
        </tr>
        <tr>
            <td><strong>Volumen de CH₄ Requerido</strong></td>
            <td class="valor-destacado">{resultado['volumen']:.2f} m³ ({resultado['volumen']*1000:.0f} L)</td>
        </tr>
        <tr>
            <td><strong>Presión de Llenado</strong></td>
            <td>{resultado['presion_llenado']:.0f} bar</td>
        </tr>
        <tr>
            <td><strong>Temperatura de Operación</strong></td>
            <td>{resultado['temperatura']:.1f} °C</td>
        </tr>
        <tr>
            <td><strong>Número de Tanques Recomendados</strong></td>
            <td class="valor-destacado">{resultado['tanques']} unidades</td>
        </tr>
        <tr>
            <td><strong>Peso Adicional Total</strong></td>
            <td class="valor-destacado">{resultado['peso']:.0f} kg ({resultado['peso']/1000:.2f} ton)</td>
        </tr>
        </table>
        
        <h2>Análisis y Recomendaciones</h2>
        <div class="info-box">
            <p><strong>Notas Importantes:</strong></p>
            <ul>
                <li>Los valores calculados están basados en los parámetros ingresados y deben validarse con datos reales del vehículo.</li>
                <li>El peso adicional de {resultado['peso']:.0f} kg puede afectar la capacidad de carga del vehículo.</li>
                <li>Se requieren {resultado['tanques']} tanques, lo que requiere validar disponibilidad de espacio en el chasis.</li>
                <li>Validar disponibilidad de estaciones GNV en las rutas operativas planificadas.</li>
            </ul>
        </div>
        
        {"<div class='alerta'><strong>⚠️ Alerta:</strong> El peso adicional es significativo (>2000 kg). Considerar reducir la autonomía o usar tanques tipo 4 (más livianos).</div>" if resultado['peso'] > 2000 else ""}
        {"<div class='alerta'><strong>⚠️ Alerta:</strong> Se requiere un número elevado de tanques (>25). Considerar tanques de mayor volumen o reducir autonomía.</div>" if resultado['tanques'] > 25 else ""}
        
        <div class="footer">
            <p><strong>CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL</strong></p>
            <p>Este informe es generado automáticamente por la aplicación de cálculo.<br>
            <em>Confidencial - Uso exclusivo del cliente {st.session_state['proyecto_cliente']}</em></p>
            <p><small>Versión {st.session_state['proyecto_version']} | Generado el {fecha_actual}</small></p>
        </div>
        </body>
        </html>
        """
        import base64
        b64 = base64.b64encode(html_report.encode('utf-8')).decode()
        href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" download="informe_gnv_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html" style="background-color: #FF7A00; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 Descargar Informe HTML</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ Realice un cálculo en la pestaña 'Cálculos principales' para habilitar la descarga del informe en HTML.")

    st.markdown("""
    Para consultas técnicas o actualizaciones, contactar al equipo de ingeniería.

    ### 1.1 Contexto

    Este sistema de cálculo está diseñado para el dimensionamiento de sistemas 
    de Gas Natural Vehicular (GNV/CNG) para vehículos pesados, específicamente 
    adaptado al mercado colombiano y cumpliendo con las normativas nacionales 
    e internacionales aplicables.

    ### 1.2 Justificación Técnica y Económica

    La conversión a GNV ofrece ventajas significativas:
    - **Reducción de emisiones**: Hasta 30% menos CO₂, 90% menos NOx y 
      eliminación de material particulado comparado con diésel
    - **Ahorro económico**: Reducción de costos de combustible del 30-50% 
      (dependiendo de precios relativos)
    - **Disponibilidad**: Infraestructura de abastecimiento en crecimiento en Colombia
    - **Rendimiento**: Mantiene potencia y torque del motor original

    ---
    ## 2. Alcance y Supuestos

    - **Tipo de vehículos**: Tractores 4x2, 6x4 y volquetas 6x4
    - **Sistema**: Bi-fuel (GNV + diésel) o dedicado GNV
    - **Presión de almacenamiento**: 200-250 bar (tanques tipo 3 o 4)
    - **Regulación**: Dos etapas (200-250 bar → 20-40 bar → 7-10 bar)
    - **Autonomía objetivo**: 600-800 km según tipo de vehículo

    Los valores por defecto en esta aplicación están basados en:
    - Estimaciones de consumo para vehículos similares
    - Normativas internacionales (UNECE R110, ISO 11439)
    - Datos de proveedores colombianos típicos
    - Propiedades termodinámicas del metano (NIST Chemistry WebBook)

    **IMPORTANTE**: Estos valores deben validarse con datos reales del vehículo 
    y condiciones operativas específicas.

    ---
    ## 3. Regulaciones y Certificaciones

    - **Resolución 957 de 2012** (MinComercio): Reglamento Técnico para talleres, 
      equipos y procesos de conversión a gas natural comprimido
    - **Resolución 180540 de 2010** (MinTransporte): Reglamento para la conversión 
      de vehículos a gas natural
    - **RETIE**: Reglamento Técnico de Instalaciones Eléctricas
    - **UNECE R110**: Uniform provisions concerning the approval of specific 
      components of motor vehicles using compressed natural gas (CNG)
    - **ISO 11439**: Gas cylinders — High pressure cylinders for the on-board 
      storage of natural gas as a fuel for automotive vehicles
    - **ISO 15500**: Road vehicles — Compressed natural gas (CNG) fuel systems
    - **SAE J1616**: Recommended Practice for Compressed Natural Gas Vehicle Fuel

    ---
    ## 4. Limitaciones y Exclusiones

    Esta herramienta de cálculo:
    - ✅ Incluye dimensionamiento básico de tanques y peso adicional
    - ❌ No incluye costos de estación de servicio GNV
    - ❌ No incluye costos de capacitación de operadores
    - ❌ No incluye costos de mantenimiento preventivo
    - ❌ No incluye costos de homologación vehicular
    - ⚠️ Asume disponibilidad de estaciones de servicio GNV en rutas operativas

    ---
    ## 5. Recomendaciones

    1. **Validar requerimientos reales**: Antes de proceder, validar consumo real, 
       autonomía mínima aceptable y disponibilidad de estaciones GNV.
    2. **Evaluar impacto de peso**: Realizar análisis económico considerando reducción 
       de capacidad de carga vs ahorro en combustible.
    3. **Considerar tanques tipo 4**: Si el peso es crítico, evaluar tanques tipo 4 
       (más livianos pero más costosos).
    4. **Reducir autonomía si es posible**: Reducir autonomía objetivo puede reducir 
       significativamente costo y peso del sistema.
    5. **Cumplimiento normativo**: Asegurar que todos los componentes cumplan UNECE R110 
       y que el taller de instalación esté certificado.

    ---
    ## 6. Contacto y Soporte
    
    **Cliente**: {st.session_state['proyecto_cliente']}  
    **Versión**: {st.session_state['proyecto_version']}  
    **Fecha**: {st.session_state['proyecto_fecha']}
    
    Para consultas técnicas o actualizaciones, contactar al equipo de ingeniería.
    """)

# ============================================
# TAB: PANEL DE ADMINISTRACIÓN (Solo Administradores)
# ============================================
if TAB_ADMIN is not None and NOTIFICATIONS_ENABLED:
    with tabs[TAB_ADMIN]:
        show_admin_panel()

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6B7280; font-size: 0.9em;'>
    <p><strong>CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL</strong></p>
    <p>Versión {st.session_state['proyecto_version']} | {st.session_state['proyecto_fecha']} | Cliente: {st.session_state['proyecto_cliente']}</p>
    <p>Confidencial - Uso exclusivo del cliente</p>
</div>
""", unsafe_allow_html=True)

