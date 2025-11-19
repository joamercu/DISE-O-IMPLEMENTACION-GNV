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

# Agregar src al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports de módulos propios
from auth_system import verify_user, create_user, get_user_role
from utils.auth_utils import load_remembered_user, save_remembered_user, clear_remembered_user
from utils.manifest_utils import load_manifest, save_manifest, generate_manifest_html
from utils.calculation_engine import calcular_sistema_gnv, calcular_sensibilidad
from utils.file_handler import get_file_mime_type, create_download_link, file_exists
from utils.drawio_integration import show_diagram_generator
from config import (
    MANIFEST_FILE, REMEMBERED_USER_FILE, USERS_DB_FILE,
    DELIVERABLE_MD, DELIVERABLE_XLSX, DELIVERABLE_XML,
    DEFAULT_CLIENT, DEFAULT_VERSION, DEFAULT_DATE
)

# Configuración de la página
st.set_page_config(
    page_title="Cálculos Combustible Vehicular GNC/GNL",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# SISTEMA DE AUTENTICACIÓN
# ============================================
# Las funciones load_remembered_user, save_remembered_user y clear_remembered_user
# están importadas desde utils.auth_utils

def show_login_page():
    """Muestra la página de inicio de sesión"""
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
            
            submitted = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
            
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
            if st.button("🗑️ Olvidar usuario guardado", use_container_width=True):
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
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.session_state['user_role'] = None
        st.rerun()
    
    st.markdown(f"""
    **Usuario:** {st.session_state.get('username', 'N/A')}  
    **Rol:** {st.session_state.get('user_role', 'N/A')}
    """)

# Título principal
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

tabs = st.tabs(tabs_list)

# Índices de tabs (siempre los mismos)
TAB_CALCULOS = 0
TAB_DATOS_CLIENTE = 1
TAB_FORMULAS = 2
TAB_SENSIBILIDAD = 3
TAB_MANIFEST = 4
TAB_INFO = 5

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
            value=800.0,
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
    calcular = st.button("🚀 Calcular Sistema GNV", type="primary", use_container_width=True)
    
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
        st.dataframe(df_resumen, use_container_width=True, hide_index=True)
        
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
        
        # Sección de diagrama P&ID
        st.markdown("---")
        with st.expander("📊 Diagrama P&ID del Sistema GNV", expanded=False):
            show_diagram_generator(
                st.session_state['calculo_resultado'],
                st.session_state.get('proyecto_cliente', 'PETROLIQUIDOS')
            )

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
        
        submitted = st.form_submit_button("💾 Guardar Datos del Cliente", use_container_width=True)
        
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
            
            st.session_state['cliente_data'] = {
                'nombre': nombre_cliente,
                'rol': st.session_state.get('user_role', 'Cliente'),
                'capacidad_de_la_flota': capacidad_flota,
                'supuestos': {
                    'operacional': supuestos_operacional,
                    'componentes': supuestos_componentes
                },
                'fecha_creacion': fecha_creacion,
                'fecha_ultima_actualizacion': fecha_iso,
                'usuario_creador': usuario_creador,
                'usuario_ultima_actualizacion': usuario_actual
            }
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
        
        json_str = json.dumps(cliente_json, indent=2, ensure_ascii=False)
        b64_json = base64.b64encode(json_str.encode('utf-8')).decode()
        href_json = f'<a href="data:application/json;base64,{b64_json}" download="datos_cliente_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json" style="background-color: #2AA1FF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 Descargar JSON</a>'
        st.markdown(href_json, unsafe_allow_html=True)
        
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
           V = \\frac{211.0 \\times 8.314 \\times 298}{20,000,000 \\times 0.01604 \\times 0.85} = 1.92 \\, \\text{m}^3
           $$
        
        5. **Número de tanques (V_unitario = 0.080 m³):**
           $$
           n_{\\text{tanques}} = \\left\\lceil \\frac{1.92}{0.080} \\right\\rceil = 24 \\, \\text{tanques}
           $$
        
        6. **Peso adicional:**
           $$
           P_{\\text{adicional}} = 24 \\times (65 + 10 + 5) = 1,920 \\, \\text{kg}
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
            value=800.0,
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
                
                # Validar resultados
                if not all(math.isfinite(v) for v in [
                    resultado['energia_requerida'], resultado['masa_ch4_requerida'],
                    resultado['volumen_gas'], resultado['numero_tanques'], resultado['peso_adicional_total']
                ]):
                    return {'energia': 0, 'masa_ch4': 0, 'volumen': 0, 'tanques': 0, 'peso': 0}
                
                return {
                    'energia': resultado['energia_requerida'],
                    'masa_ch4': resultado['masa_ch4_requerida'],
                    'volumen': resultado['volumen_gas'],
                    'tanques': resultado['numero_tanques'],
                    'peso': resultado['peso_adicional_total']
                }
            except Exception:
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
        st.dataframe(df_consumo, use_container_width=True, hide_index=True)
        
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
        st.dataframe(df_autonomia, use_container_width=True, hide_index=True)
        
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
                            # Mapear nombres de archivos a rutas completas
                            file_mapping = {
                                'PETROLIQUIDOS_GNV_Informe_v1.md': DELIVERABLE_MD,
                                'PETROLIQUIDOS_GNV_BOM_v1.xlsx': DELIVERABLE_XLSX,
                                'PETROLIQUIDOS_GNV_PID_v1.drawio.xml': DELIVERABLE_XML,
                                'PETROLIQUIDOS_GNV_manifest_v1.json': MANIFEST_FILE
                            }
                            
                            file_path = file_mapping.get(filename, filename)
                            
                            if file_exists(file_path):
                                download_link = create_download_link(file_path, f"📥 Descargar {filename}", "default")
                                if download_link:
                                    st.markdown(download_link, unsafe_allow_html=True)
                                else:
                                    st.error(f"Error al crear enlace de descarga para {filename}")
                            else:
                                st.warning(f"⚠️ El archivo '{filename}' no se encuentra en el sistema.")
                                st.caption(f"💡 Ruta esperada: {file_path}")
        
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
            
            if 'configurations_analyzed' in tech_params:
                st.markdown("#### Configuraciones Analizadas")
                configs = tech_params['configurations_analyzed']
                configs_df = pd.DataFrame(configs)
                st.dataframe(configs_df, use_container_width=True, hide_index=True)
        
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
            st.dataframe(risks_df, use_container_width=True, hide_index=True)
        
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
                                
                                if st.form_submit_button("💾 Guardar Respuesta", use_container_width=True):
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
                                
                                if st.form_submit_button("💾 Guardar Respuesta", use_container_width=True):
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
                                
                                if st.form_submit_button("💾 Guardar Respuesta", use_container_width=True):
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
                                
                                if st.form_submit_button("💾 Guardar Respuesta", use_container_width=True):
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
                                
                                if st.form_submit_button("💾 Guardar Respuesta", use_container_width=True):
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
                                
                                if st.form_submit_button("💾 Guardar Respuesta", use_container_width=True):
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
                            if st.form_submit_button("💾 Guardar", use_container_width=True):
                                st.session_state['decisiones_respuestas'][f"{question_id_med}_respuesta"] = respuesta_med
                                st.session_state['decisiones_respuestas'][f"{question_id_med}_estado"] = "Respondido"
                                st.success("✅ Respuesta guardada")
        
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
            
            json_str = json.dumps(manifest_export, indent=2, ensure_ascii=False)
            b64_json = base64.b64encode(json_str.encode('utf-8')).decode()
            href_json = f'<a href="data:application/json;base64,{b64_json}" download="manifest_completo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json" style="background-color: #FF7A00; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;">📥 Descargar Manifest JSON</a>'
            st.markdown(href_json, unsafe_allow_html=True)
            
            # Generar HTML del manifest
            st.markdown("---")
            st.markdown("#### 🌐 Generar Manifest en HTML")
            
            html_manifest = generate_manifest_html(manifest_export)
            b64_html = base64.b64encode(html_manifest.encode('utf-8')).decode()
            href_html = f'<a href="data:text/html;charset=utf-8;base64,{b64_html}" download="manifest_completo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html" style="background-color: #FF7A00; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 Descargar Manifest HTML</a>'
            st.markdown(href_html, unsafe_allow_html=True)
            
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

    Esta sección, además de brindar la información técnica de referencia, permite **generar informes de los resultados de cálculo** obtenidos en la aplicación, tanto en formato visual (markdown) como descargable en HTML, útiles para reportes de ingeniería, presentaciones o para dejar respaldo documental del análisis realizado.

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
        </style>
        </head>
        <body>
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

    st.markdown(f"""
    ---
    ## Referencia Técnica de la Plataforma

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

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6B7280; font-size: 0.9em;'>
    <p><strong>CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL</strong></p>
    <p>Versión {st.session_state['proyecto_version']} | {st.session_state['proyecto_fecha']} | Cliente: {st.session_state['proyecto_cliente']}</p>
    <p>Confidencial - Uso exclusivo del cliente</p>
</div>
""", unsafe_allow_html=True)

