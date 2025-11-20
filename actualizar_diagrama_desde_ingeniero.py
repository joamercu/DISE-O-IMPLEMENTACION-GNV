"""
Script para actualizar el diagrama base con las mejoras del ingeniero
y actualizar toda la documentación relacionada
"""
import xml.etree.ElementTree as ET
import re
from datetime import datetime

def analizar_mejoras_ingeniero(archivo_ingeniero: str):
    """Analiza las mejoras en la versión del ingeniero"""
    tree = ET.parse(archivo_ingeniero)
    root = tree.getroot()
    
    mejoras = {
        'titulo': None,
        'total_tanques': None,
        'componentes': {},
        'posiciones': {},
        'notas': None
    }
    
    # Analizar título
    for cell in root.findall('.//mxCell[@id="2"]'):
        value = cell.get('value', '')
        mejoras['titulo'] = value
    
    # Analizar total de tanques
    for cell in root.findall('.//mxCell'):
        value = cell.get('value', '')
        if 'Total:' in value and 'tanques' in value:
            match = re.search(r'Total:\s*(\d+)', value)
            if match:
                mejoras['total_tanques'] = int(match.group(1))
    
    # Analizar componentes y posiciones
    for cell in root.findall('.//mxCell[@vertex="1"]'):
        cell_id = cell.get('id', '')
        value = cell.get('value', '')
        geo = cell.find('mxGeometry')
        
        if geo is not None and cell_id not in ['0', '1', '2']:
            x = float(geo.get('x', 0))
            y = float(geo.get('y', 0))
            w = float(geo.get('width', 0))
            h = float(geo.get('height', 0))
            
            mejoras['componentes'][cell_id] = {
                'value': value,
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'style': cell.get('style', '')
            }
    
    # Analizar notas
    for cell in root.findall('.//mxCell'):
        value = cell.get('value', '')
        if 'NOTAS:' in value:
            mejoras['notas'] = value
    
    return mejoras

def actualizar_diagrama_base(archivo_base: str, mejoras: dict, archivo_salida: str):
    """Actualiza el diagrama base con las mejoras"""
    tree = ET.parse(archivo_base)
    root = tree.getroot()
    
    # Actualizar título
    for cell in root.findall('.//mxCell[@id="2"]'):
        if mejoras['titulo']:
            cell.set('value', mejoras['titulo'])
    
    # Actualizar total de tanques
    for cell in root.findall('.//mxCell'):
        value = cell.get('value', '')
        if 'Total:' in value and 'tanques' in value:
            if mejoras['total_tanques']:
                nuevo_texto = re.sub(
                    r'Total:\s*\d+\s*tanques',
                    f'Total: {mejoras["total_tanques"]} tanques',
                    value
                )
                nuevo_texto = re.sub(
                    r'\(\d+\s*tanques\s*más\)',
                    f'({mejoras["total_tanques"] - 3} tanques más)',
                    nuevo_texto
                )
                cell.set('value', nuevo_texto)
    
    # Actualizar componentes y posiciones
    for cell_id, datos in mejoras['componentes'].items():
        cell = root.find(f'.//mxCell[@id="{cell_id}"]')
        if cell is not None:
            # Actualizar valor si es diferente
            if cell.get('value') != datos['value']:
                cell.set('value', datos['value'])
            
            # Actualizar estilo si es diferente
            if cell.get('style') != datos['style']:
                cell.set('style', datos['style'])
            
            # Actualizar geometría
            geo = cell.find('mxGeometry')
            if geo is not None:
                geo.set('x', str(datos['x']))
                geo.set('y', str(datos['y']))
                geo.set('width', str(datos['width']))
                geo.set('height', str(datos['height']))
    
    # Actualizar notas
    for cell in root.findall('.//mxCell'):
        value = cell.get('value', '')
        if 'NOTAS:' in value and mejoras['notas']:
            cell.set('value', mejoras['notas'])
    
    # Guardar
    tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)
    print(f"✅ Diagrama actualizado guardado en: {archivo_salida}")

def actualizar_documentacion(mejoras: dict):
    """Actualiza la documentación con los cambios"""
    cambios = []
    
    if mejoras['total_tanques']:
        cambios.append(f"- Total de tanques actualizado: {mejoras['total_tanques']} tanques")
    
    if mejoras['titulo']:
        cambios.append("- Título actualizado con información de empresa y versión")
    
    cambios.append("- Posicionamiento mejorado de componentes")
    cambios.append("- Notas actualizadas con formato mejorado")
    
    return cambios

if __name__ == '__main__':
    print("="*80)
    print("ACTUALIZACIÓN DEL DIAGRAMA DESDE VERSIÓN DEL INGENIERO")
    print("="*80)
    print()
    
    archivo_ingeniero = 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.xml'
    archivo_base = 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml'
    archivo_salida = 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ACTUALIZADO.drawio.xml'
    
    print("📊 Analizando mejoras del ingeniero...")
    mejoras = analizar_mejoras_ingeniero(archivo_ingeniero)
    
    print(f"   ✅ Total de tanques: {mejoras['total_tanques']}")
    print(f"   ✅ Componentes analizados: {len(mejoras['componentes'])}")
    print()
    
    print("📝 Actualizando diagrama base...")
    actualizar_diagrama_base(archivo_base, mejoras, archivo_salida)
    print()
    
    print("📄 Cambios identificados para documentación:")
    cambios = actualizar_documentacion(mejoras)
    for cambio in cambios:
        print(f"   {cambio}")
    print()
    
    print("✅ Proceso completado")

