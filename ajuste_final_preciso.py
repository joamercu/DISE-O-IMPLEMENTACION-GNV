"""
Ajuste final preciso para eliminar todos los solapamientos
"""
import xml.etree.ElementTree as ET
from pathlib import Path

def ajuste_final_preciso(archivo_entrada, archivo_salida):
    """Ajuste final preciso de posiciones"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Ajustes precisos finales
    ajustes = {
        # Título - más abajo para no solapar con sensores
        '2': {'x': 600, 'y': 10, 'width': 500, 'height': 50},
        
        # Sensores - posiciones más precisas
        '14': {'x': 900, 'y': 120, 'width': 35, 'height': 35},  # P1 - más separado de válvula
        '15': {'x': 1020, 'y': 70, 'width': 35, 'height': 35},   # T1 - más arriba del regulador
        '16': {'x': 1180, 'y': 90, 'width': 35, 'height': 35},   # P2 - más arriba del filtro
        '17': {'x': 1280, 'y': 70, 'width': 35, 'height': 35},   # T2 - más arriba
        '18': {'x': 1380, 'y': 70, 'width': 35, 'height': 35},   # P3 - más arriba
        
        # Lambda - más separado de inyectores
        '19': {'x': 1540, 'y': 310, 'width': 35, 'height': 35},
        
        # Leyenda - mejor espaciado
        '39': {'x': 50, 'y': 560, 'width': 120, 'height': 40},
        '40': {'x': 50, 'y': 610, 'width': 70, 'height': 50},
        '41': {'x': 140, 'y': 610, 'width': 70, 'height': 50},
        '42': {'x': 230, 'y': 610, 'width': 70, 'height': 50},
        '43': {'x': 320, 'y': 610, 'width': 50, 'height': 40},
        '44': {'x': 390, 'y': 610, 'width': 70, 'height': 50},
    }
    
    print("🔧 Aplicando ajuste final preciso...")
    
    elementos_ajustados = 0
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell_id in ajustes:
            geometry = cell.find('mxGeometry')
            if geometry is not None:
                nueva_pos = ajustes[cell_id]
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
    
    ajuste_final_preciso(archivo_entrada, archivo_salida)

