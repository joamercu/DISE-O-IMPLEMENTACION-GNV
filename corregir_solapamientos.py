"""
Script para corregir solapamientos detectados
"""
import xml.etree.ElementTree as ET
from pathlib import Path

def corregir_solapamientos(archivo_entrada, archivo_salida):
    """Corrige los solapamientos detectados"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Ajustes de posiciones para corregir solapamientos
    ajustes_posicion = {
        # PRV - mover más arriba para no solapar con tanques
        '7': {'x': 100, 'y': 20, 'width': 50, 'height': 50},
        
        # Sensores - ajustar posiciones para no solapar con reguladores
        '14': {'x': 940, 'y': 140, 'width': 35, 'height': 35},  # P1 - más a la izquierda
        '15': {'x': 1020, 'y': 100, 'width': 35, 'height': 35},  # T1 - más arriba
        '16': {'x': 1200, 'y': 120, 'width': 35, 'height': 35},  # P2 - más arriba
        '17': {'x': 1300, 'y': 100, 'width': 35, 'height': 35},  # T2 - más arriba
        '18': {'x': 1400, 'y': 100, 'width': 35, 'height': 35},  # P3 - más arriba
        
        # Lambda - mover para no solapar con inyectores
        '19': {'x': 1500, 'y': 330, 'width': 35, 'height': 35},
        
        # Leyenda - ajustar espaciado
        '39': {'x': 50, 'y': 560, 'width': 120, 'height': 40},
        '40': {'x': 50, 'y': 610, 'width': 70, 'height': 50},
        '41': {'x': 140, 'y': 610, 'width': 70, 'height': 50},
        '42': {'x': 230, 'y': 610, 'width': 70, 'height': 50},
        '43': {'x': 320, 'y': 610, 'width': 50, 'height': 40},
        '44': {'x': 390, 'y': 610, 'width': 70, 'height': 50},
    }
    
    print("🔧 Corrigiendo solapamientos...")
    
    elementos_corregidos = 0
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell_id in ajustes_posicion:
            geometry = cell.find('mxGeometry')
            if geometry is not None:
                nueva_pos = ajustes_posicion[cell_id]
                geometry.set('x', str(nueva_pos['x']))
                geometry.set('y', str(nueva_pos['y']))
                geometry.set('width', str(nueva_pos['width']))
                geometry.set('height', str(nueva_pos['height']))
                elementos_corregidos += 1
                print(f"   ✅ Elemento {cell_id} reposicionado")
    
    print(f"✅ {elementos_corregidos} elementos corregidos")
    
    # Guardar el archivo
    tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)
    print(f"✅ Archivo corregido guardado en: {archivo_salida}")

if __name__ == "__main__":
    archivo_entrada = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    archivo_salida = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    corregir_solapamientos(archivo_entrada, archivo_salida)

