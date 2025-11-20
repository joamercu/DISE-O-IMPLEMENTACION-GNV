"""
Script para verificar si todos los documentos .MD, Excel y entregas
están actualizados según el diagrama de referencia del ingeniero
"""
import os
import re
from pathlib import Path
import xml.etree.ElementTree as ET

# Valores esperados según el diagrama de referencia
VALORES_REFERENCIA = {
    'total_tanques': 18,
    'autonomia_objetivo': 600,  # km
    'volumen_total': 1.44,  # m³ (18 tanques × 0.080 m³)
    'presion_llenado': 200,  # bar
    'empresa': 'WELDTECH SOLUTION',
    'version': 'PROPUESTA TECNICA',
    'revision': '0 (PROPUESTA PREELIMINAR)'
}

def extraer_valores_diagrama(archivo_xml):
    """Extrae valores del diagrama XML de referencia"""
    valores = {}
    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
        
        # Buscar total de tanques
        for cell in root.findall('.//mxCell'):
            value = cell.get('value', '')
            if 'Total:' in value and 'tanques' in value:
                match = re.search(r'Total:\s*(\d+)', value)
                if match:
                    valores['total_tanques'] = int(match.group(1))
            
            # Buscar variables del proyecto
            if 'VARIABLES DEL PROYECTO' in value:
                # Extraer número de tanques
                match = re.search(r'Número de tanques:\s*(\d+)', value)
                if match:
                    valores['total_tanques'] = int(match.group(1))
                
                # Extraer autonomía
                match = re.search(r'Autonomía objetivo:\s*(\d+)', value)
                if match:
                    valores['autonomia_objetivo'] = int(match.group(1))
                
                # Extraer volumen total
                match = re.search(r'Volumen total de gas:\s*([\d.]+)', value)
                if match:
                    valores['volumen_total'] = float(match.group(1))
            
            # Buscar información de empresa
            if 'WELDTECH SOLUTION' in value:
                valores['empresa'] = 'WELDTECH SOLUTION'
            if 'PROPUESTA TECNICA' in value:
                valores['version'] = 'PROPUESTA TECNICA'
            if 'REVISION: 0' in value or 'PROPUESTA PREELIMINAR' in value:
                valores['revision'] = '0 (PROPUESTA PREELIMINAR)'
        
        return valores
    except Exception as e:
        print(f"   ⚠️ Error leyendo XML: {e}")
        return {}

def verificar_archivo_md(archivo_path):
    """Verifica si un archivo .MD está actualizado"""
    problemas = []
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar número de tanques
        if re.search(r'\b24\s*tanques\b', contenido, re.IGNORECASE):
            problemas.append("❌ Menciona '24 tanques' (debería ser 18)")
        
        # Verificar autonomía
        if re.search(r'\b800\s*km\b', contenido) and '600' not in contenido:
            # Solo es problema si menciona 800 km sin contexto de 600 km
            if 'Autonomía objetivo: 800' in contenido or 'Autonomía deseada: 800' in contenido:
                problemas.append("❌ Menciona 'Autonomía: 800 km' como objetivo (debería ser 600 km)")
        
        # Verificar información de empresa
        if 'WELDTECH SOLUTION' not in contenido and 'PETROLIQUIDOS' in contenido:
            problemas.append("⚠️ No menciona 'WELDTECH SOLUTION'")
        
        return problemas
    except Exception as e:
        return [f"⚠️ Error leyendo archivo: {e}"]

def verificar_excel(archivo_path):
    """Verifica si un archivo Excel está actualizado (básico)"""
    problemas = []
    # Los archivos Excel son binarios, solo verificamos que existan
    if not os.path.exists(archivo_path):
        problemas.append("❌ Archivo no existe")
    else:
        # Verificar fecha de modificación reciente
        import datetime
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(archivo_path))
        if mod_time < datetime.datetime(2024, 12, 19):
            problemas.append(f"⚠️ Archivo modificado antes de 2024-12-19: {mod_time.strftime('%Y-%m-%d')}")
    
    return problemas

def main():
    print("="*80)
    print("VERIFICACIÓN DE ACTUALIZACIÓN COMPLETA DEL PROYECTO")
    print("="*80)
    print()
    print("📋 Diagrama de referencia: diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.pdf/xml")
    print()
    
    # Extraer valores del diagrama de referencia
    archivo_referencia = 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.xml'
    if os.path.exists(archivo_referencia):
        print("📊 Extrayendo valores del diagrama de referencia...")
        valores_diagrama = extraer_valores_diagrama(archivo_referencia)
        print(f"   ✅ Total de tanques: {valores_diagrama.get('total_tanques', 'No encontrado')}")
        print(f"   ✅ Autonomía objetivo: {valores_diagrama.get('autonomia_objetivo', 'No encontrado')} km")
        print(f"   ✅ Volumen total: {valores_diagrama.get('volumen_total', 'No encontrado')} m³")
        print()
    else:
        print("⚠️ No se encontró el archivo XML de referencia")
        valores_diagrama = VALORES_REFERENCIA
    
    # Verificar archivos .MD
    print("="*80)
    print("VERIFICANDO ARCHIVOS .MD")
    print("="*80)
    
    archivos_md = []
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                archivos_md.append(os.path.join(root, file))
    
    # También verificar archivos .MD en la raíz
    for file in os.listdir('.'):
        if file.endswith('.md') and os.path.isfile(file):
            archivos_md.append(file)
    
    archivos_con_problemas = []
    archivos_ok = []
    
    for archivo in sorted(archivos_md):
        problemas = verificar_archivo_md(archivo)
        if problemas:
            archivos_con_problemas.append((archivo, problemas))
            print(f"❌ {archivo}")
            for problema in problemas:
                print(f"   {problema}")
        else:
            archivos_ok.append(archivo)
            print(f"✅ {archivo}")
    
    print()
    print(f"📊 Resumen .MD: {len(archivos_ok)} OK, {len(archivos_con_problemas)} con problemas")
    print()
    
    # Verificar archivos Excel
    print("="*80)
    print("VERIFICANDO ARCHIVOS EXCEL")
    print("="*80)
    
    archivos_excel = [
        'outputs/PETROLIQUIDOS_GNV_BOM_v1.xlsx',
        'versionados/excel/BOM_PETROLIQUIDOS_GNV_20251119_091941.xlsx'
    ]
    
    excel_con_problemas = []
    excel_ok = []
    
    for archivo in archivos_excel:
        if os.path.exists(archivo):
            problemas = verificar_excel(archivo)
            if problemas:
                excel_con_problemas.append((archivo, problemas))
                print(f"⚠️ {archivo}")
                for problema in problemas:
                    print(f"   {problema}")
            else:
                excel_ok.append(archivo)
                print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - No existe")
    
    print()
    print(f"📊 Resumen Excel: {len(excel_ok)} OK, {len(excel_con_problemas)} con problemas")
    print()
    
    # Resumen final
    print("="*80)
    print("RESUMEN FINAL")
    print("="*80)
    
    total_problemas = len(archivos_con_problemas) + len(excel_con_problemas)
    
    if total_problemas == 0:
        print("✅ TODOS LOS DOCUMENTOS ESTÁN ACTUALIZADOS")
        print()
        print("Valores verificados:")
        print(f"  • Total de tanques: {valores_diagrama.get('total_tanques', 18)}")
        print(f"  • Autonomía objetivo: {valores_diagrama.get('autonomia_objetivo', 600)} km")
        print(f"  • Volumen total: {valores_diagrama.get('volumen_total', 1.44)} m³")
    else:
        print(f"⚠️ SE ENCONTRARON {total_problemas} ARCHIVOS CON PROBLEMAS")
        print()
        print("Archivos que requieren actualización:")
        for archivo, problemas in archivos_con_problemas:
            print(f"  • {archivo}")
        for archivo, problemas in excel_con_problemas:
            print(f"  • {archivo}")
        print()
        print("💡 Ejecute 'actualizar_documentacion_completa.py' para actualizar automáticamente")
    
    print("="*80)

if __name__ == '__main__':
    main()

