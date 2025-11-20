"""
Script avanzado para optimizar rutas de conexiones y evitar bloques
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

def calcular_ruta_optima(source_pos, target_pos, bloques, source_id, target_id):
    """Calcula una ruta óptima evitando bloques"""
    waypoints = []
    
    # Puntos de salida y entrada
    source_x = source_pos['right']  # Salida por la derecha
    source_y = source_pos['center_y']
    target_x = target_pos['x']  # Entrada por la izquierda
    target_y = target_pos['center_y']
    
    # Si es conexión horizontal directa
    if abs(source_y - target_y) < 30:
        # Verificar si hay bloques en el camino
        bloque_en_camino = False
        for bid, bloque in bloques.items():
            if bid in [source_id, target_id]:
                continue
            # Verificar si el bloque está entre source y target
            if (bloque['x'] < target_x and bloque['right'] > source_x and
                bloque['y'] < max(source_y, target_y) + 30 and
                bloque['bottom'] > min(source_y, target_y) - 30):
                bloque_en_camino = True
                # Añadir waypoint arriba o abajo
                offset = 60
                waypoint_y = min(bloque['y'] - offset, source_y - offset)
                waypoint_x = source_x + (target_x - source_x) / 2
                waypoints.append({'x': waypoint_x, 'y': waypoint_y})
                break
    
    # Si es conexión vertical o diagonal
    elif abs(source_x - target_x) > 50:
        # Añadir waypoint para hacer la ruta en L
        mid_x = source_x + (target_x - source_x) / 2
        waypoints.append({'x': mid_x, 'y': source_y})
        waypoints.append({'x': mid_x, 'y': target_y})
    
    return waypoints

def optimizar_rutas_conexiones(archivo_entrada, archivo_salida):
    """Optimiza todas las rutas de conexiones"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Obtener todas las posiciones de los bloques
    bloques = {}
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell_id and cell.get('vertex') == '1':
            pos = obtener_posicion_elemento(cell)
            if pos:
                bloques[cell_id] = pos
    
    print(f"📊 Procesando {len(bloques)} bloques")
    
    # Procesar todas las conexiones
    conexiones_optimizadas = 0
    
    for edge in root.findall('.//mxCell[@edge="1"]'):
        source_id = edge.get('source')
        target_id = edge.get('target')
        
        if not source_id or not target_id or source_id not in bloques or target_id not in bloques:
            continue
        
        source_pos = bloques[source_id]
        target_pos = bloques[target_id]
        
        # Calcular ruta óptima
        waypoints = calcular_ruta_optima(source_pos, target_pos, bloques, source_id, target_id)
        
        if waypoints:
            geometry = edge.find('mxGeometry')
            if geometry is None:
                geometry = ET.SubElement(edge, 'mxGeometry')
                geometry.set('relative', '1')
                geometry.set('as', 'geometry')
            
            # Eliminar waypoints anteriores si existen
            for old_array in geometry.findall('Array'):
                geometry.remove(old_array)
            
            # Añadir nuevos waypoints
            if waypoints:
                points = ET.SubElement(geometry, 'Array')
                points.set('as', 'points')
                for wp in waypoints:
                    point = ET.SubElement(points, 'mxPoint')
                    point.set('x', str(int(wp['x'])))
                    point.set('y', str(int(wp['y'])))
                conexiones_optimizadas += 1
    
    print(f"✅ Rutas optimizadas: {conexiones_optimizadas}")
    
    # Asegurar que todas las conexiones tengan etiquetas apropiadas
    etiquetas_completadas = 0
    for edge in root.findall('.//mxCell[@edge="1"]'):
        value = edge.get('value', '')
        style = edge.get('style', '')
        
        # Completar etiquetas según el tipo de conexión
        if not value or value.strip() == '':
            if 'strokeColor=#6c8ebf' in style:  # Gas CNG (azul)
                source_id = edge.get('source')
                if source_id in ['3', '4', '5']:  # Desde tanques
                    edge.set('value', 'Gas CNG')
                    etiquetas_completadas += 1
            elif 'strokeColor=#82b366' in style:  # Gas regulado (verde)
                edge.set('value', 'Gas Regulado')
                etiquetas_completadas += 1
            elif 'strokeColor=#d79b00' in style and 'Señales' not in value:  # Señales ECU
                edge.set('value', 'Señales')
                etiquetas_completadas += 1
            elif 'strokeColor=#d6b656' in style:  # Sensores
                edge.set('value', 'Datos Sensor')
                etiquetas_completadas += 1
    
    print(f"✅ Etiquetas completadas: {etiquetas_completadas}")
    
    # Guardar el archivo
    tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)
    print(f"✅ Archivo optimizado guardado en: {archivo_salida}")

if __name__ == "__main__":
    archivo_entrada = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    archivo_salida = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    optimizar_rutas_conexiones(archivo_entrada, archivo_salida)

