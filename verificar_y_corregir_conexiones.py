"""
Script para verificar y corregir conexiones del diagrama
- Verifica que todas las conexiones estén correctas
- Añade waypoints para evitar que pasen por encima de bloques
- Completa tags y etiquetas
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
        return {'x': x, 'y': y, 'width': width, 'height': height, 'right': x + width, 'bottom': y + height}
    return None

def punto_en_bloque(x, y, bloque):
    """Verifica si un punto está dentro de un bloque"""
    return (bloque['x'] <= x <= bloque['right'] and 
            bloque['y'] <= y <= bloque['bottom'])

def crear_waypoints(source_pos, target_pos, bloques):
    """Crea waypoints para evitar bloques"""
    waypoints = []
    
    # Calcular punto medio vertical para rutas horizontales
    mid_y = (source_pos['y'] + source_pos['height']/2 + target_pos['y'] + target_pos['height']/2) / 2
    
    # Si la conexión es horizontal (misma altura aproximada)
    if abs((source_pos['y'] + source_pos['height']/2) - (target_pos['y'] + target_pos['height']/2)) < 50:
        # Añadir waypoint arriba o abajo según sea necesario
        offset_y = 40  # Offset para evitar bloques
        
        # Verificar si hay bloques en el camino directo
        camino_directo_ok = True
        for bloque in bloques:
            if (bloque['x'] < source_pos['right'] and bloque['right'] > source_pos['x'] and
                bloque['y'] < mid_y + 20 and bloque['bottom'] > mid_y - 20):
                camino_directo_ok = False
                break
        
        if not camino_directo_ok:
            # Añadir waypoint arriba
            waypoint_y = min(source_pos['y'], target_pos['y']) - offset_y
            waypoint_x = source_pos['right'] + (target_pos['x'] - source_pos['right']) / 2
            waypoints.append({'x': waypoint_x, 'y': waypoint_y})
    
    return waypoints

def verificar_y_corregir_conexiones(archivo_entrada, archivo_salida):
    """Verifica y corrige todas las conexiones del diagrama"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Obtener todas las posiciones de los bloques (vértices)
    bloques = {}
    vertices = {}
    
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell_id and cell.get('vertex') == '1':
            pos = obtener_posicion_elemento(cell)
            if pos:
                bloques[cell_id] = pos
                vertices[cell_id] = cell
    
    print(f"📊 Encontrados {len(bloques)} bloques/vértices")
    
    # Procesar todas las conexiones (edges)
    conexiones_corregidas = 0
    conexiones_sin_etiqueta = []
    
    for edge in root.findall('.//mxCell[@edge="1"]'):
        source_id = edge.get('source')
        target_id = edge.get('target')
        
        if not source_id or not target_id:
            print(f"⚠️ Conexión sin source o target: {edge.get('id')}")
            continue
        
        if source_id not in bloques or target_id not in bloques:
            print(f"⚠️ Conexión con IDs inválidos: {source_id} -> {target_id}")
            continue
        
        source_pos = bloques[source_id]
        target_pos = bloques[target_id]
        
        # Verificar si la conexión necesita waypoints
        geometry = edge.find('mxGeometry')
        if geometry is None:
            geometry = ET.SubElement(edge, 'mxGeometry')
            geometry.set('relative', '1')
            geometry.set('as', 'geometry')
        
        # Crear waypoints si es necesario
        waypoints = crear_waypoints(source_pos, target_pos, 
                                   [b for bid, b in bloques.items() 
                                    if bid not in [source_id, target_id]])
        
        if waypoints:
            # Añadir waypoints usando Array de puntos
            points = ET.SubElement(geometry, 'Array')
            points.set('as', 'points')
            for wp in waypoints:
                point = ET.SubElement(points, 'mxPoint')
                point.set('x', str(wp['x']))
                point.set('y', str(wp['y']))
            conexiones_corregidas += 1
        
        # Verificar y completar etiquetas
        value = edge.get('value', '')
        if not value or value.strip() == '':
            # Añadir etiqueta según el tipo de conexión
            style = edge.get('style', '')
            if 'strokeColor=#6c8ebf' in style:  # Conexión de gas (azul)
                if source_id in ['3', '4', '5']:  # Tanques
                    edge.set('value', 'Gas CNG')
                elif 'bar' not in value:
                    # Determinar presión según posición
                    if '8' in [source_id, target_id]:  # Manifold
                        edge.set('value', '200-250 bar')
            elif 'strokeColor=#82b366' in style:  # Conexión de gas regulado (verde)
                if not value:
                    edge.set('value', 'Gas Regulado')
            elif 'strokeColor=#d79b00' in style:  # Señales ECU (naranja)
                if not value:
                    edge.set('value', 'Señales')
            elif 'strokeColor=#d6b656' in style:  # Sensores (amarillo)
                if not value:
                    edge.set('value', 'Datos')
        
        # Verificar que la etiqueta esté completa
        if edge.get('value'):
            conexiones_sin_etiqueta.append(edge.get('id'))
    
    print(f"✅ Conexiones con waypoints añadidos: {conexiones_corregidas}")
    print(f"✅ Conexiones con etiquetas: {len(conexiones_sin_etiqueta)}")
    
    # Añadir conexiones faltantes importantes
    conexiones_esperadas = [
        # Sensores que faltan conexiones
        ('15', '13', 'T', 'strokeColor=#d6b656'),  # T1 -> ECU
        ('16', '13', 'P', 'strokeColor=#d6b656'),  # P2 -> ECU
        ('17', '13', 'T', 'strokeColor=#d6b656'),  # T2 -> ECU
        ('18', '13', 'P', 'strokeColor=#d6b656'),  # P3 -> ECU
    ]
    
    # Obtener el siguiente ID disponible
    max_id = max([int(cell.get('id', '0')) for cell in root.findall('.//mxCell') if cell.get('id', '0').isdigit()])
    nuevo_id = max_id + 1
    
    conexiones_añadidas = 0
    for source_id, target_id, label, color_style in conexiones_esperadas:
        if source_id in bloques and target_id in bloques:
            # Verificar si ya existe la conexión
            existe = False
            for edge in root.findall('.//mxCell[@edge="1"]'):
                if edge.get('source') == source_id and edge.get('target') == target_id:
                    existe = True
                    break
            
            if not existe:
                # Crear nueva conexión
                nueva_conexion = ET.SubElement(root.find('.//root'), 'mxCell')
                nueva_conexion.set('id', str(nuevo_id))
                nueva_conexion.set('value', label)
                nueva_conexion.set('style', f'endArrow=classic;html=1;strokeWidth=1;{color_style};dashed=1;fontSize=10;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0')
                nueva_conexion.set('edge', '1')
                nueva_conexion.set('source', source_id)
                nueva_conexion.set('target', target_id)
                nueva_conexion.set('parent', '1')
                
                geometry = ET.SubElement(nueva_conexion, 'mxGeometry')
                geometry.set('width', '50')
                geometry.set('height', '50')
                geometry.set('relative', '1')
                geometry.set('as', 'geometry')
                
                nuevo_id += 1
                conexiones_añadidas += 1
    
    print(f"✅ Conexiones añadidas: {conexiones_añadidas}")
    
    # Guardar el archivo
    tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)
    print(f"✅ Archivo corregido guardado en: {archivo_salida}")

if __name__ == "__main__":
    archivo_entrada = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    archivo_salida = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    verificar_y_corregir_conexiones(archivo_entrada, archivo_salida)

