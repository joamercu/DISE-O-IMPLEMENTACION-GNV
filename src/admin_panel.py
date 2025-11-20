"""
Panel de Administración
Vista para administradores: gestión de envíos, notificaciones y seguimiento
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

from database import (
    get_submissions,
    get_submission_by_id,
    update_submission_status,
    get_submission_stats,
    get_unread_notifications,
    mark_notification_read
)


def show_admin_panel():
    """Mostrar panel de administración completo"""
    
    st.header("🔧 Panel de Administración")
    st.markdown("---")
    
    # Obtener estadísticas
    stats = get_submission_stats()
    
    # Mostrar estadísticas en columnas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Envíos", stats['total'])
    
    with col2:
        st.metric("Pendientes", stats['pendientes'], delta=None if stats['pendientes'] == 0 else f"-{stats['pendientes']}")
    
    with col3:
        st.metric("En Revisión", stats['en_revision'])
    
    with col4:
        st.metric("Aprobados", stats['aprobados'])
    
    with col5:
        st.metric("Rechazados", stats['rechazados'])
    
    st.markdown("---")
    
    # Tabs para diferentes secciones
    tab1, tab2, tab3 = st.tabs(["📋 Envíos", "🔔 Notificaciones", "📊 Estadísticas"])
    
    with tab1:
        show_submissions_section()
    
    with tab2:
        show_notifications_section()
    
    with tab3:
        show_statistics_section(stats)


def show_submissions_section():
    """Mostrar sección de envíos con filtros y lista"""
    
    st.subheader("📋 Gestión de Envíos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_estado = st.selectbox(
            "Filtrar por Estado",
            ["Todos", "pendiente", "en_revision", "aprobado", "rechazado"],
            key="filtro_estado"
        )
    
    with col2:
        busqueda_cliente = st.text_input(
            "Buscar por Cliente",
            placeholder="Nombre del cliente...",
            key="busqueda_cliente"
        )
    
    with col3:
        limite = st.number_input(
            "Límite de resultados",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            key="limite_resultados"
        )
    
    # Obtener envíos con filtros
    estado_filtro = None if filtro_estado == "Todos" else filtro_estado
    cliente_filtro = busqueda_cliente if busqueda_cliente else None
    
    submissions = get_submissions(
        estado=estado_filtro,
        cliente_nombre=cliente_filtro,
        limit=limite
    )
    
    if not submissions:
        st.info("📭 No se encontraron envíos con los filtros seleccionados.")
        return
    
    # Mostrar tabla de envíos
    st.markdown(f"### Encontrados {len(submissions)} envío(s)")
    
    # Preparar datos para DataFrame
    df_data = []
    for sub in submissions:
        fecha_envio = datetime.fromisoformat(sub['fecha_envio']).strftime("%d/%m/%Y %H:%M") if sub['fecha_envio'] else "N/A"
        fecha_actualizacion = datetime.fromisoformat(sub['fecha_ultima_actualizacion']).strftime("%d/%m/%Y %H:%M") if sub['fecha_ultima_actualizacion'] else "N/A"
        
        df_data.append({
            'ID': sub['id'],
            'Cliente': sub['cliente_nombre'],
            'Usuario': sub['usuario_cliente'],
            'Estado': sub['estado'].replace('_', ' ').title(),
            'Fecha Envío': fecha_envio,
            'Última Actualización': fecha_actualizacion,
            'Admin Asignado': sub['administrador_asignado'] or "Sin asignar"
        })
    
    df = pd.DataFrame(df_data)
    
    # Mostrar tabla con selección
    selected_indices = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Si hay una selección, mostrar detalles
    if selected_indices.selection.rows:
        selected_index = selected_indices.selection.rows[0]
        submission_id = df.iloc[selected_index]['ID']
        show_submission_details(submission_id)


def show_submission_details(submission_id: int):
    """Mostrar detalles completos de un envío"""
    
    st.markdown("---")
    st.subheader(f"📄 Detalles del Envío #{submission_id}")
    
    submission = get_submission_by_id(submission_id)
    
    if not submission:
        st.error("❌ No se pudo cargar el envío.")
        return
    
    # Información general
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Cliente:** {submission['cliente_nombre']}")
        st.info(f"**Usuario:** {submission['usuario_cliente']}")
        st.info(f"**Estado:** {submission['estado'].replace('_', ' ').title()}")
    
    with col2:
        fecha_envio = datetime.fromisoformat(submission['fecha_envio']).strftime("%d/%m/%Y %H:%M:%S") if submission['fecha_envio'] else "N/A"
        fecha_actualizacion = datetime.fromisoformat(submission['fecha_ultima_actualizacion']).strftime("%d/%m/%Y %H:%M:%S") if submission['fecha_ultima_actualizacion'] else "N/A"
        st.info(f"**Fecha de Envío:** {fecha_envio}")
        st.info(f"**Última Actualización:** {fecha_actualizacion}")
        st.info(f"**Admin Asignado:** {submission['administrador_asignado'] or 'Sin asignar'}")
    
    # Tabs para diferentes secciones del envío
    detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs([
        "📝 Datos del Cliente",
        "🔢 Cálculos",
        "📐 Diagramas",
        "⚙️ Gestión"
    ])
    
    with detail_tab1:
        show_submission_data(submission)
    
    with detail_tab2:
        show_submission_calculos(submission)
    
    with detail_tab3:
        show_submission_diagramas(submission)
    
    with detail_tab4:
        show_submission_management(submission_id, submission)


def show_submission_data(submission: Dict):
    """Mostrar datos del cliente del envío"""
    
    if not submission.get('datos'):
        st.warning("⚠️ No hay datos del cliente registrados para este envío.")
        return
    
    datos = submission['datos']['datos_cliente']
    metadata = submission['datos'].get('metadata', {})
    
    st.markdown("### Información del Cliente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Nombre:** {datos.get('nombre', 'N/A')}")
        st.write(f"**Capacidad de la Flota:** {datos.get('capacidad_de_la_flota', 'N/A')}")
    
    with col2:
        if metadata:
            fecha_creacion = metadata.get('fecha_creacion', 'N/A')
            usuario_creador = metadata.get('usuario_creador', 'N/A')
            st.write(f"**Creado por:** {usuario_creador}")
            st.write(f"**Fecha creación:** {fecha_creacion}")
    
    st.markdown("### Supuestos Operativos")
    if datos.get('supuestos', {}).get('operacional'):
        st.text_area("", datos['supuestos']['operacional'], height=150, disabled=True, key="sup_operacional")
    else:
        st.info("No hay supuestos operativos registrados.")
    
    st.markdown("### Supuestos de Componentes")
    if datos.get('supuestos', {}).get('componentes'):
        st.text_area("", datos['supuestos']['componentes'], height=150, disabled=True, key="sup_componentes")
    else:
        st.info("No hay supuestos de componentes registrados.")


def show_submission_calculos(submission: Dict):
    """Mostrar cálculos del envío"""
    
    calculos = submission.get('calculos', [])
    
    if not calculos:
        st.info("📊 No hay cálculos registrados para este envío.")
        return
    
    st.markdown(f"### Resultados de Cálculos ({len(calculos)} registro(s))")
    
    for idx, calc in enumerate(calculos, 1):
        with st.expander(f"📊 Cálculo #{idx} - {calc.get('fecha_calculo', 'N/A')}"):
            st.markdown("#### Parámetros de Entrada")
            if calc.get('parametros_entrada'):
                st.json(calc['parametros_entrada'])
            else:
                st.info("No hay parámetros de entrada registrados.")
            
            st.markdown("#### Resultados")
            if calc.get('resultados_calculo'):
                st.json(calc['resultados_calculo'])


def show_submission_diagramas(submission: Dict):
    """Mostrar diagramas del envío"""
    
    diagramas = submission.get('diagramas', [])
    
    if not diagramas:
        st.info("📐 No hay diagramas registrados para este envío.")
        return
    
    st.markdown(f"### Diagramas Generados ({len(diagramas)} diagrama(s))")
    
    for idx, diag in enumerate(diagramas, 1):
        with st.expander(f"📐 Diagrama #{idx} - {diag.get('fecha_generacion', 'N/A')}"):
            st.write(f"**Ruta de archivo:** {diag.get('ruta_archivo', 'N/A')}")
            st.write(f"**Tiene PDF:** {'✅ Sí' if diag.get('tiene_pdf') else '❌ No'}")
            
            if diag.get('diagrama_xml'):
                st.markdown("#### Vista Previa XML (primeros 1000 caracteres)")
                st.code(diag['diagrama_xml'], language='xml')


def show_submission_management(submission_id: int, submission: Dict):
    """Mostrar sección de gestión del envío (cambiar estado, notas)"""
    
    st.markdown("### ⚙️ Gestión del Envío")
    
    # Cambiar estado
    st.markdown("#### Cambiar Estado")
    
    estado_actual = submission['estado']
    nuevo_estado = st.selectbox(
        "Nuevo Estado",
        ["pendiente", "en_revision", "aprobado", "rechazado"],
        index=["pendiente", "en_revision", "aprobado", "rechazado"].index(estado_actual),
        key=f"estado_{submission_id}"
    )
    
    # Notas del administrador
    st.markdown("#### Notas del Administrador")
    notas_actuales = submission.get('notas_administrador', '')
    nuevas_notas = st.text_area(
        "Notas",
        value=notas_actuales,
        height=150,
        placeholder="Agregue notas sobre este envío...",
        key=f"notas_{submission_id}"
    )
    
    # Botón para guardar cambios
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("💾 Guardar Cambios", key=f"guardar_{submission_id}"):
            admin_usuario = st.session_state.get('username', 'admin')
            
            if update_submission_status(
                submission_id=submission_id,
                nuevo_estado=nuevo_estado,
                administrador=admin_usuario,
                notas=nuevas_notas
            ):
                st.success("✅ Cambios guardados correctamente.")
                st.rerun()
            else:
                st.error("❌ Error al guardar los cambios.")
    
    # Historial de notificaciones
    st.markdown("---")
    st.markdown("### 📬 Historial de Notificaciones")
    
    notificaciones = submission.get('notificaciones', [])
    
    if notificaciones:
        for notif in notificaciones:
            estado_icon = "✅" if notif['estado'] == 'leida' else "📬" if notif['estado'] == 'enviada' else "❌"
            fecha = datetime.fromisoformat(notif['fecha_envio']).strftime("%d/%m/%Y %H:%M") if notif['fecha_envio'] else "N/A"
            
            st.write(f"{estado_icon} **{notif['tipo'].upper()}** - {fecha} - {notif['estado'].title()}")
            if notif.get('mensaje'):
                st.caption(f"   {notif['mensaje']}")
    else:
        st.info("No hay notificaciones registradas para este envío.")


def show_notifications_section():
    """Mostrar sección de notificaciones"""
    
    st.subheader("🔔 Notificaciones")
    
    # Obtener notificaciones no leídas
    notificaciones = get_unread_notifications(limit=50)
    
    if not notificaciones:
        st.success("✅ No hay notificaciones pendientes.")
        return
    
    st.markdown(f"### Tienes {len(notificaciones)} notificación(es) no leída(s)")
    
    # Mostrar notificaciones
    for notif in notificaciones:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                fecha = datetime.fromisoformat(notif['fecha_envio']).strftime("%d/%m/%Y %H:%M") if notif['fecha_envio'] else "N/A"
                st.write(f"**📬 {notif['cliente_nombre']}** - {fecha}")
                st.caption(notif.get('mensaje', 'Sin mensaje'))
            
            with col2:
                if st.button("👁️ Ver Envío", key=f"ver_{notif['id']}"):
                    st.session_state['selected_submission_id'] = notif['submission_id']
                    st.rerun()
            
            with col3:
                if st.button("✅ Marcar Leída", key=f"leer_{notif['id']}"):
                    if mark_notification_read(notif['id']):
                        st.success("✅ Notificación marcada como leída.")
                        st.rerun()
                    else:
                        st.error("❌ Error al marcar como leída.")
            
            st.divider()
    
    # Si hay un envío seleccionado, mostrarlo
    if 'selected_submission_id' in st.session_state:
        st.markdown("---")
        show_submission_details(st.session_state['selected_submission_id'])


def show_statistics_section(stats: Dict):
    """Mostrar sección de estadísticas detalladas"""
    
    st.subheader("📊 Estadísticas Detalladas")
    
    # Gráfico de distribución por estado
    st.markdown("### Distribución por Estado")
    
    if stats['total'] > 0:
        import plotly.express as px
        
        estados_data = {
            'Estado': ['Pendientes', 'En Revisión', 'Aprobados', 'Rechazados'],
            'Cantidad': [
                stats['pendientes'],
                stats['en_revision'],
                stats['aprobados'],
                stats['rechazados']
            ]
        }
        
        df_estados = pd.DataFrame(estados_data)
        
        fig = px.pie(
            df_estados,
            values='Cantidad',
            names='Estado',
            title="Distribución de Envíos por Estado"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 No hay datos suficientes para mostrar estadísticas.")
    
    # Resumen numérico
    st.markdown("### Resumen Numérico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total de Envíos", stats['total'])
        st.metric("Pendientes", stats['pendientes'])
    
    with col2:
        st.metric("En Revisión", stats['en_revision'])
        st.metric("Aprobados", stats['aprobados'])
        st.metric("Rechazados", stats['rechazados'])

