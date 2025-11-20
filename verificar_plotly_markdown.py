#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script completo para verificar Plotly y Markdown en el servidor y localmente
Verifica instalación, funcionalidad y compatibilidad con el proyecto
"""

import sys
import os
from pathlib import Path
from typing import Tuple, Dict, Any

# Colores para output (compatible con Windows y Linux)
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
except ImportError:
    GREEN = RED = YELLOW = BLUE = CYAN = RESET = BOLD = ''


def print_header(texto: str):
    """Imprime un encabezado formateado"""
    print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
    print(f"{BOLD}{BLUE}{texto.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 70}{RESET}\n")


def print_section(texto: str):
    """Imprime una sección formateada"""
    print(f"\n{CYAN}{'─' * 70}{RESET}")
    print(f"{BOLD}{CYAN}{texto}{RESET}")
    print(f"{CYAN}{'─' * 70}{RESET}\n")


def verificar_plotly() -> Tuple[bool, Dict[str, Any]]:
    """
    Verifica que Plotly esté instalado y funcional
    
    Returns:
        Tuple[bool, Dict]: (éxito, información detallada)
    """
    resultado = {
        'instalado': False,
        'version': None,
        'express_disponible': False,
        'graph_objects_disponible': False,
        'funcionalidad_basica': False,
        'streamlit_compatible': False,
        'errores': []
    }
    
    print_section("📊 VERIFICANDO PLOTLY")
    
    # 1. Verificar importación básica
    try:
        import plotly
        resultado['instalado'] = True
        resultado['version'] = plotly.__version__
        print(f"  {GREEN}✅ Plotly está instalado{RESET}")
        print(f"     Versión: {BOLD}{resultado['version']}{RESET}")
    except ImportError as e:
        resultado['errores'].append(f"Importación fallida: {str(e)}")
        print(f"  {RED}❌ Plotly NO está instalado{RESET}")
        print(f"     Error: {str(e)}")
        return False, resultado
    
    # 2. Verificar plotly.express
    try:
        import plotly.express as px
        resultado['express_disponible'] = True
        print(f"  {GREEN}✅ plotly.express disponible{RESET}")
    except ImportError as e:
        resultado['errores'].append(f"plotly.express no disponible: {str(e)}")
        print(f"  {RED}❌ plotly.express NO disponible{RESET}")
        print(f"     Error: {str(e)}")
    
    # 3. Verificar plotly.graph_objects
    try:
        import plotly.graph_objects as go
        resultado['graph_objects_disponible'] = True
        print(f"  {GREEN}✅ plotly.graph_objects disponible{RESET}")
    except ImportError as e:
        resultado['errores'].append(f"plotly.graph_objects no disponible: {str(e)}")
        print(f"  {YELLOW}⚠️  plotly.graph_objects NO disponible (opcional){RESET}")
    
    # 4. Prueba de funcionalidad básica
    if resultado['express_disponible']:
        try:
            import plotly.express as px
            import pandas as pd
            
            # Crear un gráfico de prueba
            df_test = pd.DataFrame({
                'x': ['A', 'B', 'C'],
                'y': [1, 2, 3]
            })
            fig = px.bar(df_test, x='x', y='y', title='Test Plotly')
            
            # Verificar que el objeto figure se creó correctamente
            if hasattr(fig, 'data') and hasattr(fig, 'layout'):
                resultado['funcionalidad_basica'] = True
                print(f"  {GREEN}✅ Funcionalidad básica OK (gráfico de prueba creado){RESET}")
            else:
                resultado['errores'].append("El objeto figure no tiene la estructura esperada")
                print(f"  {YELLOW}⚠️  El gráfico se creó pero tiene estructura inesperada{RESET}")
        except Exception as e:
            resultado['errores'].append(f"Error en funcionalidad básica: {str(e)}")
            print(f"  {RED}❌ Error al crear gráfico de prueba{RESET}")
            print(f"     Error: {str(e)}")
    
    # 5. Verificar compatibilidad con Streamlit
    try:
        import streamlit as st
        resultado['streamlit_compatible'] = True
        print(f"  {GREEN}✅ Streamlit disponible (compatibilidad OK){RESET}")
    except ImportError:
        print(f"  {YELLOW}⚠️  Streamlit no disponible (no crítico para esta verificación){RESET}")
    
    # Resumen
    exito = (resultado['instalado'] and 
             resultado['express_disponible'] and 
             resultado['funcionalidad_basica'])
    
    if exito:
        print(f"\n  {BOLD}{GREEN}✓ PLOTLY ESTÁ FUNCIONANDO CORRECTAMENTE{RESET}")
    else:
        print(f"\n  {BOLD}{RED}✗ PLOTLY TIENE PROBLEMAS{RESET}")
        if resultado['errores']:
            print(f"     Errores encontrados: {len(resultado['errores'])}")
    
    return exito, resultado


def verificar_markdown() -> Tuple[bool, Dict[str, Any]]:
    """
    Verifica que Markdown esté instalado y funcional
    
    Returns:
        Tuple[bool, Dict]: (éxito, información detallada)
    """
    resultado = {
        'instalado': False,
        'version': None,
        'extensiones_disponibles': [],
        'conversion_funcional': False,
        'extensiones_requeridas': ['tables', 'fenced_code', 'codehilite', 'toc'],
        'errores': []
    }
    
    print_section("📝 VERIFICANDO MARKDOWN")
    
    # 1. Verificar importación básica
    try:
        import markdown
        resultado['instalado'] = True
        resultado['version'] = markdown.__version__
        print(f"  {GREEN}✅ Markdown está instalado{RESET}")
        print(f"     Versión: {BOLD}{resultado['version']}{RESET}")
    except ImportError as e:
        resultado['errores'].append(f"Importación fallida: {str(e)}")
        print(f"  {RED}❌ Markdown NO está instalado{RESET}")
        print(f"     Error: {str(e)}")
        return False, resultado
    
    # 2. Verificar extensiones requeridas por el proyecto
    if resultado['instalado']:
        import markdown
        extensiones_disponibles = []
        extensiones_faltantes = []
        
        for ext in resultado['extensiones_requeridas']:
            try:
                # Intentar crear un objeto Markdown con la extensión
                md = markdown.Markdown(extensions=[ext])
                extensiones_disponibles.append(ext)
                print(f"  {GREEN}✅ Extensión '{ext}' disponible{RESET}")
            except Exception as e:
                extensiones_faltantes.append(ext)
                print(f"  {YELLOW}⚠️  Extensión '{ext}' no disponible{RESET}")
                resultado['errores'].append(f"Extensión '{ext}' no disponible: {str(e)}")
        
        resultado['extensiones_disponibles'] = extensiones_disponibles
        
        if extensiones_faltantes:
            print(f"     Extensiones faltantes: {', '.join(extensiones_faltantes)}")
    
    # 3. Prueba de conversión funcional
    if resultado['instalado']:
        try:
            import markdown
            
            # Contenido Markdown de prueba
            contenido_md = """# Título de Prueba

Este es un **texto en negrita** y este es un *texto en cursiva*.

## Lista
- Item 1
- Item 2

### Código
```python
print("Hello, World!")
```
"""
            
            # Intentar convertir con las extensiones que usa el proyecto
            md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite', 'toc'])
            html = md.convert(contenido_md)
            
            # Verificar que la conversión produjo HTML válido
            if html and len(html) > 0:
                # Verificar elementos esperados (búsqueda flexible)
                checks = [
                    ('<h1', 'Título convertido'),  # Buscar <h1 o <h1> o <h1 id=...
                    ('<strong>', 'Negrita convertida'),
                    ('<em>', 'Cursiva convertida'),
                    ('<ul>', 'Lista convertida'),
                    ('<code', 'Código convertido')
                ]
                
                checks_ok = 0
                for check, desc in checks:
                    if check in html:
                        checks_ok += 1
                        print(f"  {GREEN}✅ {desc}{RESET}")
                    else:
                        print(f"  {YELLOW}⚠️  {desc} no encontrado en HTML{RESET}")
                
                # Considerar funcional si al menos 4 de 5 checks pasan
                if checks_ok >= 4:
                    resultado['conversion_funcional'] = True
                    print(f"  {GREEN}✅ Conversión Markdown → HTML funcional ({checks_ok}/5 elementos verificados){RESET}")
                else:
                    resultado['errores'].append(f"La conversión no produjo el HTML esperado ({checks_ok}/5 elementos verificados)")
            else:
                resultado['errores'].append("La conversión produjo HTML vacío")
                print(f"  {RED}❌ La conversión produjo HTML vacío{RESET}")
                
        except Exception as e:
            resultado['errores'].append(f"Error en conversión: {str(e)}")
            print(f"  {RED}❌ Error al convertir Markdown{RESET}")
            print(f"     Error: {str(e)}")
    
    # Resumen
    exito = (resultado['instalado'] and 
             resultado['conversion_funcional'] and
             len(resultado['extensiones_disponibles']) >= 2)  # Al menos 2 extensiones
    
    if exito:
        print(f"\n  {BOLD}{GREEN}✓ MARKDOWN ESTÁ FUNCIONANDO CORRECTAMENTE{RESET}")
    else:
        print(f"\n  {BOLD}{RED}✗ MARKDOWN TIENE PROBLEMAS{RESET}")
        if resultado['errores']:
            print(f"     Errores encontrados: {len(resultado['errores'])}")
    
    return exito, resultado


def verificar_requirements_txt() -> Tuple[bool, Dict[str, Any]]:
    """
    Verifica que Plotly y Markdown estén en requirements.txt
    
    Returns:
        Tuple[bool, Dict]: (éxito, información detallada)
    """
    resultado = {
        'archivo_existe': False,
        'plotly_en_requirements': False,
        'markdown_en_requirements': False,
        'plotly_version': None,
        'markdown_version': None,
        'errores': []
    }
    
    print_section("📋 VERIFICANDO requirements.txt")
    
    requirements_path = Path('requirements.txt')
    
    if not requirements_path.exists():
        resultado['errores'].append("requirements.txt no existe")
        print(f"  {RED}❌ requirements.txt no encontrado{RESET}")
        return False, resultado
    
    resultado['archivo_existe'] = True
    print(f"  {GREEN}✅ requirements.txt encontrado{RESET}")
    
    try:
        with open(requirements_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            lineas = contenido.split('\n')
        
        # Buscar Plotly
        for linea in lineas:
            linea_lower = linea.lower().strip()
            if 'plotly' in linea_lower and not linea_lower.startswith('#'):
                resultado['plotly_en_requirements'] = True
                # Extraer versión si está especificada
                if '>=' in linea:
                    resultado['plotly_version'] = linea.split('>=')[-1].strip()
                print(f"  {GREEN}✅ Plotly está en requirements.txt{RESET}")
                if resultado['plotly_version']:
                    print(f"     Versión requerida: {BOLD}{resultado['plotly_version']}{RESET}")
                break
        
        if not resultado['plotly_en_requirements']:
            print(f"  {RED}❌ Plotly NO está en requirements.txt{RESET}")
            resultado['errores'].append("Plotly no encontrado en requirements.txt")
        
        # Buscar Markdown
        for linea in lineas:
            linea_lower = linea.lower().strip()
            if 'markdown' in linea_lower and not linea_lower.startswith('#'):
                resultado['markdown_en_requirements'] = True
                # Extraer versión si está especificada
                if '>=' in linea:
                    resultado['markdown_version'] = linea.split('>=')[-1].strip()
                print(f"  {GREEN}✅ Markdown está en requirements.txt{RESET}")
                if resultado['markdown_version']:
                    print(f"     Versión requerida: {BOLD}{resultado['markdown_version']}{RESET}")
                break
        
        if not resultado['markdown_en_requirements']:
            print(f"  {RED}❌ Markdown NO está en requirements.txt{RESET}")
            resultado['errores'].append("Markdown no encontrado en requirements.txt")
        
    except Exception as e:
        resultado['errores'].append(f"Error al leer requirements.txt: {str(e)}")
        print(f"  {RED}❌ Error al leer requirements.txt{RESET}")
        print(f"     Error: {str(e)}")
        return False, resultado
    
    exito = resultado['plotly_en_requirements'] and resultado['markdown_en_requirements']
    return exito, resultado


def verificar_uso_en_proyecto() -> Dict[str, Any]:
    """
    Verifica dónde se usan Plotly y Markdown en el proyecto
    
    Returns:
        Dict: Información sobre el uso en el proyecto
    """
    resultado = {
        'archivos_con_plotly': [],
        'archivos_con_markdown': [],
        'plotly_en_codigo': False,
        'markdown_en_codigo': False
    }
    
    print_section("🔍 VERIFICANDO USO EN EL PROYECTO")
    
    # Buscar archivos Python que usan Plotly
    archivos_python = list(Path('src').rglob('*.py')) if Path('src').exists() else []
    archivos_python.extend(list(Path('.').glob('*.py')))
    
    for archivo in archivos_python:
        try:
            contenido = archivo.read_text(encoding='utf-8', errors='ignore')
            
            # Buscar uso de Plotly
            if 'plotly' in contenido.lower() or 'plotly.express' in contenido or 'plotly.graph_objects' in contenido:
                resultado['archivos_con_plotly'].append(str(archivo))
                resultado['plotly_en_codigo'] = True
            
            # Buscar uso de Markdown (importación, no solo st.markdown)
            if 'import markdown' in contenido or 'from markdown' in contenido:
                resultado['archivos_con_markdown'].append(str(archivo))
                resultado['markdown_en_codigo'] = True
        except Exception:
            continue
    
    if resultado['plotly_en_codigo']:
        print(f"  {GREEN}✅ Plotly se usa en el proyecto{RESET}")
        print(f"     Archivos encontrados: {len(resultado['archivos_con_plotly'])}")
        for archivo in resultado['archivos_con_plotly'][:5]:  # Mostrar máximo 5
            print(f"       - {archivo}")
        if len(resultado['archivos_con_plotly']) > 5:
            print(f"       ... y {len(resultado['archivos_con_plotly']) - 5} más")
    else:
        print(f"  {YELLOW}⚠️  No se encontró uso directo de Plotly en el código{RESET}")
    
    if resultado['markdown_en_codigo']:
        print(f"  {GREEN}✅ Markdown se usa en el proyecto{RESET}")
        print(f"     Archivos encontrados: {len(resultado['archivos_con_markdown'])}")
        for archivo in resultado['archivos_con_markdown'][:5]:  # Mostrar máximo 5
            print(f"       - {archivo}")
        if len(resultado['archivos_con_markdown']) > 5:
            print(f"       ... y {len(resultado['archivos_con_markdown']) - 5} más")
    else:
        print(f"  {YELLOW}⚠️  No se encontró uso directo de Markdown en el código{RESET}")
    
    return resultado


def generar_reporte_final(
    plotly_ok: bool, 
    plotly_info: Dict[str, Any],
    markdown_ok: bool, 
    markdown_info: Dict[str, Any],
    requirements_ok: bool,
    requirements_info: Dict[str, Any],
    uso_info: Dict[str, Any]
):
    """Genera un reporte final con recomendaciones"""
    
    print_header("📊 REPORTE FINAL")
    
    # Resumen de estado
    print(f"\n{BOLD}ESTADO DE LAS DEPENDENCIAS:{RESET}\n")
    
    estado_plotly = f"{GREEN}✅ FUNCIONAL{RESET}" if plotly_ok else f"{RED}❌ CON PROBLEMAS{RESET}"
    estado_markdown = f"{GREEN}✅ FUNCIONAL{RESET}" if markdown_ok else f"{RED}❌ CON PROBLEMAS{RESET}"
    estado_requirements = f"{GREEN}✅ COMPLETO{RESET}" if requirements_ok else f"{YELLOW}⚠️  INCOMPLETO{RESET}"
    
    print(f"  Plotly:     {estado_plotly}")
    if plotly_info.get('version'):
        print(f"              Versión instalada: {BOLD}{plotly_info['version']}{RESET}")
    
    print(f"  Markdown:   {estado_markdown}")
    if markdown_info.get('version'):
        print(f"              Versión instalada: {BOLD}{markdown_info['version']}{RESET}")
    
    print(f"  Requirements.txt: {estado_requirements}")
    
    # Recomendaciones
    print(f"\n{BOLD}RECOMENDACIONES:{RESET}\n")
    
    if not plotly_ok:
        print(f"  {YELLOW}⚠️  Para instalar/corregir Plotly:{RESET}")
        print(f"     pip install --upgrade plotly>=5.17.0")
        if sys.platform.startswith('linux'):
            print(f"     (En Debian 13+: pip3 install --upgrade plotly>=5.17.0 --break-system-packages)")
    
    if not markdown_ok:
        print(f"  {YELLOW}⚠️  Para instalar/corregir Markdown:{RESET}")
        print(f"     pip install --upgrade markdown>=3.4.0")
        if sys.platform.startswith('linux'):
            print(f"     (En Debian 13+: pip3 install --upgrade markdown>=3.4.0 --break-system-packages)")
    
    if not requirements_ok:
        print(f"  {YELLOW}⚠️  Para actualizar requirements.txt:{RESET}")
        print(f"     Asegúrate de que contenga:")
        print(f"     plotly>=5.17.0")
        print(f"     markdown>=3.4.0")
    
    if plotly_ok and markdown_ok:
        print(f"  {GREEN}✅ Todas las dependencias están funcionando correctamente{RESET}")
        print(f"     El proyecto debería funcionar sin problemas relacionados con Plotly y Markdown")
    
    # Información del sistema
    print(f"\n{BOLD}INFORMACIÓN DEL SISTEMA:{RESET}\n")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Plataforma: {sys.platform}")
    print(f"  Directorio de trabajo: {os.getcwd()}")


def main():
    """Función principal"""
    print_header("VERIFICACIÓN DE PLOTLY Y MARKDOWN")
    print(f"{CYAN}Este script verifica que Plotly y Markdown estén instalados,")
    print(f"funcionando correctamente y compatibles con el proyecto.{RESET}\n")
    
    # Verificaciones
    plotly_ok, plotly_info = verificar_plotly()
    markdown_ok, markdown_info = verificar_markdown()
    requirements_ok, requirements_info = verificar_requirements_txt()
    uso_info = verificar_uso_en_proyecto()
    
    # Reporte final
    generar_reporte_final(
        plotly_ok, plotly_info,
        markdown_ok, markdown_info,
        requirements_ok, requirements_info,
        uso_info
    )
    
    # Código de salida
    if plotly_ok and markdown_ok:
        print(f"\n{BOLD}{GREEN}{'=' * 70}{RESET}")
        print(f"{BOLD}{GREEN}✅ VERIFICACIÓN COMPLETADA - TODO FUNCIONA CORRECTAMENTE{RESET}")
        print(f"{BOLD}{GREEN}{'=' * 70}{RESET}\n")
        return 0
    else:
        print(f"\n{BOLD}{RED}{'=' * 70}{RESET}")
        print(f"{BOLD}{RED}❌ VERIFICACIÓN COMPLETADA - HAY PROBLEMAS QUE RESOLVER{RESET}")
        print(f"{BOLD}{RED}{'=' * 70}{RESET}\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Verificación cancelada por el usuario{RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}❌ Error inesperado: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

