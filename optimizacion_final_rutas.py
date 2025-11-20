"""
Optimización final de rutas de conexiones con waypoints inteligentes
"""
import xml.etree.ElementTree as ET
from pathlib import Path

def obtener_posicion_elemento(cell):
    """Obtiene la posición y tamaño de un elemento"""
    geometry = cell.find('mxGeometry')
    if geometry is not None:
        x = float(geometry.get('x', 0))
        y = float(geometry.get('y', 0))
        width = float(geometry.get('width', 0))
        height = float(geometry.get('height', 0))
        return {
            'x': x, 'y': y, 'width': width, 'height': height,
            'right': x + width, 'bottom': y + height,
            'center_x': x + width/2, 'center_y': y + height/2
        }
    return None

def optimizacion_final_rutas(archivo_entrada, archivo_salida):
    """Optimiza todas las rutas con waypoints inteligentes"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Obtener todas las posiciones
    bloques = {}
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell_id and cell.get('vertex') == '1':
            pos = obtener_posicion_elemento(cell)
            if pos:
                bloques[cell_id] = pos
    
    print(f"📊 Optimizando rutas para {len(bloques)} bloques...")
    
    # Mapeo de conexiones a rutas optimizadas
    rutas_optimizadas = {
        # Conexiones desde tanques al manifold - rutas horizontales directas
        '3->8': [],  # Tanque 1 -> Manifold (directa)
        '4->8': [],  # Tanque 2 -> Manifold (directa)
        '5->8': [],  # Tanque 3 -> Manifold (directa)
        
        # Manifold -> Válvula - directa
        '8->9': [],
        
        # Válvula -> Regulador 1 - directa
        '9->10': [],
        
        # Regulador 1 -> Filtro - directa
        '10->11': [],
        
        # Filtro -> Regulador 2 - directa
        '11->12': [],
        
        # Regulador 2 -> Inyectores - vertical con waypoint
        '12->20': [{'x': 1440, 'y': 280}],  # Waypoint para bajar
        
        # Inyectores -> Motor - directa vertical
        '20->21': [],
        
        # ECU -> Regulador 1 - vertical directa
        '13->10': [],
        
        # ECU -> Inyectores - horizontal con waypoint arriba
        '13->20': [{'x': 1200, 'y': 280}],  # Waypoint para evitar componentes
        
        # Sensores -> ECU - rutas con waypoints
        '14->13': [{'x': 1000, 'y': 147}],  # P1 -> ECU
        '15->13': [{'x': 1000, 'y': 97}],   # T1 -> ECU
        '16->13': [{'x': 1000, 'y': 117}],  # P2 -> ECU
        '17->13': [{'x': 1000, 'y': 97}],   # T2 -> ECU
        '18->13': [{'x': 1000, 'y': 97}],   # P3 -> ECU
        '19->13': [{'x': 1200, 'y': 347}],  # Lambda -> ECU
        
        # Válvula llenado -> Tanque 1 - directa vertical
        '22->3': [],
    }
    
    conexiones_optimizadas = 0
    
    for edge in root.findall('.//mxCell[@edge="1"]'):
        source_id = edge.get('source')
        target_id = edge.get('target')
        
        if not source_id or not target_id:
            continue
        
        key = f"{source_id}->{target_id}"
        
        if key in rutas_optimizadas:
            waypoints = rutas_optimizadas[key]
            
            geometry = edge.find('mxGeometry')
            if geometry is None:
                geometry = ET.SubElement(edge, 'mxGeometry')
                geometry.set('relative', '1')
                geometry.set('as', 'geometry')
            
            # Eliminar waypoints anteriores
            for old_array in geometry.findall('Array'):
                geometry.remove(old_array)
            
            # Añadir nuevos waypoints si existen
            if waypoints:
                points = ET.SubElement(geometry, 'Array')
                points.set('as', 'points')
                for wp in waypoints:
                    point = ET.SubElement(points, 'mxPoint')
                    point.set('x', str(int(wp['x'])))
                    point.set('y', str(int(wp['y'])))
                conexiones_optimizadas += 1
    
    print(f"✅ {conexiones_optimizadas} rutas optimizadas con waypoints")
    
    # Guardar el archivo
    tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)
    print(f"✅ Archivo optimizado guardado en: {archivo_salida}")

if __name__ == "__main__":
    archivo_entrada = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    archivo_salida = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    optimizacion_final_rutas(archivo_entrada, archivo_salida)

