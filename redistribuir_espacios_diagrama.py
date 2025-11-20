"""
Script para redistribuir los espacios del diagrama y evitar solapamientos
"""
import xml.etree.ElementTree as ET
from pathlib import Path

def redistribuir_espacios(archivo_entrada, archivo_salida):
    """Redistribuye los elementos del diagrama con más espacio"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Aumentar el tamaño de la página
    for graph_model in root.findall('.//mxGraphModel'):
        graph_model.set('pageWidth', '1800')
        graph_model.set('pageHeight', '1100')
    
    # Mapeo de IDs a nuevas posiciones
    # Estructura: {id: {'x': x, 'y': y, 'width': width, 'height': height}}
    
    nuevas_posiciones = {
        # Título
        '2': {'x': 600, 'y': 20, 'width': 500, 'height': 50},
        
        # Tanques (más separados)
        '3': {'x': 50, 'y': 120, 'width': 100, 'height': 120},
        '4': {'x': 200, 'y': 120, 'width': 100, 'height': 120},
        '5': {'x': 350, 'y': 120, 'width': 100, 'height': 120},
        '6': {'x': 500, 'y': 150, 'width': 120, 'height': 50},  # Texto "21 tanques más"
        
        # PRV (válvula de alivio) - más arriba y centrada
        '7': {'x': 150, 'y': 60, 'width': 50, 'height': 50},
        
        # Manifold - más separado de los tanques
        '8': {'x': 680, 'y': 140, 'width': 140, 'height': 80},
        
        # Válvula Shut-off - más separada
        '9': {'x': 880, 'y': 145, 'width': 60, 'height': 60},
        
        # Regulador 1ra Etapa - más espacio
        '10': {'x': 1000, 'y': 120, 'width': 160, 'height': 120},
        
        # Filtro - más separado
        '11': {'x': 1220, 'y': 140, 'width': 100, 'height': 80},
        
        # Regulador 2da Etapa - más separado
        '12': {'x': 1360, 'y': 120, 'width': 160, 'height': 120},
        
        # ECU - más abajo y centrado
        '13': {'x': 1000, 'y': 320, 'width': 160, 'height': 80},
        
        # Sensores - mejor posicionados
        '14': {'x': 960, 'y': 150, 'width': 35, 'height': 35},  # P1 (antes del regulador 1)
        '15': {'x': 1040, 'y': 150, 'width': 35, 'height': 35},  # T1
        '16': {'x': 1180, 'y': 150, 'width': 35, 'height': 35},  # P2 (antes del filtro)
        '17': {'x': 1320, 'y': 150, 'width': 35, 'height': 35},  # T2 (antes del regulador 2)
        '18': {'x': 1400, 'y': 150, 'width': 35, 'height': 35},  # P3
        '19': {'x': 1380, 'y': 330, 'width': 35, 'height': 35},  # Lambda (cerca del motor)
        
        # Inyectores - más separados
        '20': {'x': 1360, 'y': 300, 'width': 160, 'height': 80},
        
        # Motor - más abajo
        '21': {'x': 1360, 'y': 420, 'width': 160, 'height': 120},
        
        # Válvula de llenado - más abajo
        '22': {'x': 50, 'y': 300, 'width': 80, 'height': 80},
        
        # Notas y variables - más abajo
        '37': {'x': 50, 'y': 720, 'width': 450, 'height': 140},
        '38': {'x': 550, 'y': 720, 'width': 450, 'height': 140},
        
        # Leyenda - más abajo
        '39': {'x': 50, 'y': 560, 'width': 120, 'height': 40},
        '40': {'x': 50, 'y': 610, 'width': 70, 'height': 50},
        '41': {'x': 140, 'y': 610, 'width': 70, 'height': 50},
        '42': {'x': 230, 'y': 610, 'width': 70, 'height': 50},
        '43': {'x': 320, 'y': 610, 'width': 50, 'height': 40},
        '44': {'x': 390, 'y': 610, 'width': 70, 'height': 50},
    }
    
    # Aplicar nuevas posiciones
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell_id and cell_id in nuevas_posiciones:
            pos = nuevas_posiciones[cell_id]
            geometry = cell.find('mxGeometry')
            if geometry is not None:
                geometry.set('x', str(pos['x']))
                geometry.set('y', str(pos['y']))
                geometry.set('width', str(pos['width']))
                geometry.set('height', str(pos['height']))
    
    # Guardar el archivo
    tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)
    print(f"✅ Diagrama redistribuido guardado en: {archivo_salida}")
    print(f"   Tamaño de página: 1800x1100")
    print(f"   Elementos reposicionados: {len(nuevas_posiciones)}")

if __name__ == "__main__":
    archivo_entrada = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    archivo_salida = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    redistribuir_espacios(archivo_entrada, archivo_salida)

