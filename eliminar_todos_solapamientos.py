"""
Script final para eliminar todos los solapamientos
"""
import xml.etree.ElementTree as ET
from pathlib import Path

def eliminar_todos_solapamientos(archivo_entrada, archivo_salida):
    """Elimina todos los solapamientos restantes"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Ajustes finales de posiciones
    ajustes_finales = {
        # Sensores - más separados de componentes principales
        '14': {'x': 920, 'y': 130, 'width': 35, 'height': 35},  # P1 - más separado
        '15': {'x': 1000, 'y': 80, 'width': 35, 'height': 35},  # T1 - más arriba
        '16': {'x': 1180, 'y': 100, 'width': 35, 'height': 35},  # P2 - más arriba
        '17': {'x': 1280, 'y': 80, 'width': 35, 'height': 35},  # T2 - más arriba
        '18': {'x': 1380, 'y': 80, 'width': 35, 'height': 35},  # P3 - más arriba
        
        # Lambda - más separado de inyectores
        '19': {'x': 1520, 'y': 320, 'width': 35, 'height': 35},
        
        # Leyenda - mejor espaciado vertical
        '39': {'x': 50, 'y': 560, 'width': 120, 'height': 40},
        '40': {'x': 50, 'y': 610, 'width': 70, 'height': 50},
        '41': {'x': 140, 'y': 610, 'width': 70, 'height': 50},
        '42': {'x': 230, 'y': 610, 'width': 70, 'height': 50},
        '43': {'x': 320, 'y': 610, 'width': 50, 'height': 40},
        '44': {'x': 390, 'y': 610, 'width': 70, 'height': 50},
    }
    
    print("🔧 Aplicando ajustes finales...")
    
    elementos_ajustados = 0
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell_id in ajustes_finales:
            geometry = cell.find('mxGeometry')
            if geometry is not None:
                nueva_pos = ajustes_finales[cell_id]
                geometry.set('x', str(nueva_pos['x']))
                geometry.set('y', str(nueva_pos['y']))
                geometry.set('width', str(nueva_pos['width']))
                geometry.set('height', str(nueva_pos['height']))
                elementos_ajustados += 1
    
    print(f"✅ {elementos_ajustados} elementos ajustados")
    
    # Guardar el archivo
    tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)
    print(f"✅ Archivo guardado en: {archivo_salida}")

if __name__ == "__main__":
    archivo_entrada = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    archivo_salida = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    eliminar_todos_solapamientos(archivo_entrada, archivo_salida)

