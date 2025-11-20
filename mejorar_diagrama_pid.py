"""
Script para mejorar el diagrama P&ID:
1. Identificar equipos repetidos
2. Verificar todas las conexiones
3. Mejorar formas usando bibliotecas estándar de draw.io
4. Asegurar waypoints adecuados para evitar solapamientos
"""
import xml.etree.ElementTree as ET
import re

# Leer el archivo
tree = ET.parse('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml')
root = tree.getroot()

# Diccionario para rastrear componentes y sus conexiones
components = {}
edges = []
all_ids = set()

print("=== ANÁLISIS DEL DIAGRAMA ===\n")

# Analizar componentes
for diagram in root.findall('.//diagram'):
    for mxGraphModel in diagram.findall('.//mxGraphModel'):
        for root_elem in mxGraphModel.findall('.//root'):
            # Analizar vértices (componentes)
            for cell in root_elem.findall('.//mxCell[@id]'):
                cell_id = cell.get('id', '')
                all_ids.add(cell_id)
                
                if cell.get('vertex') == '1':
                    value = cell.get('value', '')
                    geo = cell.find('mxGeometry')
                    if geo is not None:
                        x = float(geo.get('x', 0))
                        y = float(geo.get('y', 0))
                        w = float(geo.get('width', 0))
                        h = float(geo.get('height', 0))
                        
                        components[cell_id] = {
                            'id': cell_id,
                            'value': value,
                            'x': x, 'y': y, 'w': w, 'h': h,
                            'style': cell.get('style', ''),
                            'bbox': (x, y, x+w, y+h)
                        }
            
            # Analizar edges (conexiones)
            for cell in root_elem.findall('.//mxCell[@edge="1"]'):
                source = cell.get('source')
                target = cell.get('target')
                edge_id = cell.get('id', '')
                
                edges.append({
                    'id': edge_id,
                    'source': source,
                    'target': target,
                    'value': cell.get('value', ''),
                    'style': cell.get('style', '')
                })

# 1. Verificar equipos repetidos
print("1. VERIFICACIÓN DE EQUIPOS REPETIDOS:")
value_counts = {}
for comp_id, comp in components.items():
    # Extraer texto principal del value (sin IDs)
    value_text = re.sub(r'[A-Z]+-\d+', '', comp['value'])
    value_text = re.sub(r'[PTFTLTXI]-\d+', '', value_text)
    value_text = value_text.strip()
    
    if value_text not in value_counts:
        value_counts[value_text] = []
    value_counts[value_text].append(comp_id)

duplicates = {k: v for k, v in value_counts.items() if len(v) > 1 and k.strip()}
if duplicates:
    print("   ⚠️ Componentes con valores similares encontrados:")
    for value, ids in duplicates.items():
        if len(ids) > 1:
            print(f"      - '{value[:50]}...': {len(ids)} instancias (IDs: {ids[:3]})")
else:
    print("   ✅ No se encontraron duplicados problemáticos")

# 2. Verificar conexiones
print("\n2. VERIFICACIÓN DE CONEXIONES:")
missing_source = []
missing_target = []
invalid_source = []
invalid_target = []

for edge in edges:
    if not edge['source']:
        missing_source.append(edge['id'])
    elif edge['source'] not in all_ids:
        invalid_source.append((edge['id'], edge['source']))
    
    if not edge['target']:
        missing_target.append(edge['id'])
    elif edge['target'] not in all_ids:
        invalid_target.append((edge['id'], edge['target']))

if missing_source:
    print(f"   ⚠️ {len(missing_source)} conexiones sin source")
if missing_target:
    print(f"   ⚠️ {len(missing_target)} conexiones sin target")
if invalid_source:
    print(f"   ⚠️ {len(invalid_source)} conexiones con source inválido: {invalid_source[:3]}")
if invalid_target:
    print(f"   ⚠️ {len(invalid_target)} conexiones con target inválido: {invalid_target[:3]}")

if not missing_source and not missing_target and not invalid_source and not invalid_target:
    print("   ✅ Todas las conexiones tienen source y target válidos")

# 3. Mejorar formas y estilos
print("\n3. MEJORANDO FORMAS Y ESTILOS...")

# Mejoras de formas para P&ID estándar
improvements = {
    # Válvulas - usar formas más específicas
    '9': {  # Válvula Shut-off
        'style': 'shape=valve;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;perimeter=valvePerimeter;strokeWidth=2'
    },
    '49': {  # Válvula EFC
        'style': 'shape=valve;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;perimeter=valvePerimeter;strokeWidth=2'
    },
    '22': {  # Válvula Llenado
        'style': 'shape=valve;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;perimeter=valvePerimeter;strokeWidth=2'
    },
    '51': {  # Válvula Cierre Rápido
        'style': 'shape=valve;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;perimeter=valvePerimeter;strokeWidth=2'
    },
    
    # Reguladores - mejorar representación
    '10': {  # Regulador 1ra etapa
        'style': 'shape=hexagon;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;strokeWidth=2;perimeter=hexagonPerimeter2'
    },
    '12': {  # Regulador 2da etapa
        'style': 'shape=hexagon;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;strokeWidth=2;perimeter=hexagonPerimeter2'
    },
    
    # Manifold - usar forma más apropiada
    '8': {
        'style': 'shape=parallelogram;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;strokeWidth=2'
    },
    
    # ECU - mejorar
    '13': {
        'style': 'shape=rect;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;strokeWidth=2;dashed=1;dashPattern=8 8'
    },
    
    # Sensores - mejorar círculos con borde más visible
    '14': {'style': 'shape=ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2'},
    '15': {'style': 'shape=ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2'},
    '16': {'style': 'shape=ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2'},
    '17': {'style': 'shape=ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2'},
    '18': {'style': 'shape=ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2'},
    '19': {'style': 'shape=ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2'},
    '50': {'style': 'shape=ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2'},
    '55': {'style': 'shape=ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2'},
}

# Aplicar mejoras
for diagram in root.findall('.//diagram'):
    for mxGraphModel in diagram.findall('.//mxGraphModel'):
        for root_elem in mxGraphModel.findall('.//root'):
            for cell in root_elem.findall('.//mxCell[@id]'):
                cell_id = cell.get('id', '')
                if cell_id in improvements:
                    new_style = improvements[cell_id].get('style', '')
                    if new_style:
                        cell.set('style', new_style)

# 4. Mejorar conexiones con waypoints para evitar solapamientos
print("\n4. MEJORANDO CONEXIONES CON WAYPOINTS...")

def calculate_waypoints(source_comp, target_comp, edge_type='gas'):
    """Calcula waypoints para evitar solapamientos"""
    sx, sy, sw, sh = source_comp['bbox']
    tx, ty, tw, th = target_comp['bbox']
    
    waypoints = []
    
    # Calcular puntos medios
    source_center_x = sx + sw/2
    source_center_y = sy + sh/2
    target_center_x = tx + tw/2
    target_center_y = ty + th/2
    
    # Si están en la misma línea horizontal
    if abs(sy - ty) < 50:
        # Ruta vertical primero, luego horizontal
        mid_y = min(sy, ty) - 50  # 50px arriba
        waypoints.append((source_center_x, mid_y))
        waypoints.append((target_center_x, mid_y))
    # Si están en la misma línea vertical
    elif abs(sx - tx) < 50:
        # Ruta horizontal primero, luego vertical
        mid_x = min(sx, tx) - 50  # 50px a la izquierda
        waypoints.append((mid_x, source_center_y))
        waypoints.append((mid_x, target_center_y))
    else:
        # Ruta ortogonal estándar
        mid_x = (source_center_x + target_center_x) / 2
        mid_y = (source_center_y + target_center_y) / 2
        waypoints.append((mid_x, source_center_y))
        waypoints.append((mid_x, target_center_y))
    
    return waypoints

# Actualizar conexiones con waypoints mejorados
connections_updated = 0
for diagram in root.findall('.//diagram'):
    for mxGraphModel in diagram.findall('.//mxGraphModel'):
        for root_elem in mxGraphModel.findall('.//root'):
            for cell in root_elem.findall('.//mxCell[@edge="1"]'):
                source_id = cell.get('source')
                target_id = cell.get('target')
                
                if source_id and target_id and source_id in components and target_id in components:
                    source_comp = components[source_id]
                    target_comp = components[target_id]
                    
                    # Verificar si necesita waypoints
                    geo = cell.find('mxGeometry')
                    if geo is not None:
                        # Calcular distancia
                        dist = ((target_comp['x'] - source_comp['x'])**2 + 
                               (target_comp['y'] - source_comp['y'])**2)**0.5
                        
                        # Si la distancia es grande o hay componentes intermedios, agregar waypoints
                        if dist > 200:
                            waypoints = calculate_waypoints(source_comp, target_comp)
                            
                            # Crear o actualizar Array de waypoints
                            array = geo.find('Array')
                            if array is None:
                                array = ET.SubElement(geo, 'Array')
                                array.set('as', 'points')
                            
                            # Limpiar waypoints existentes
                            for point in array.findall('mxPoint'):
                                array.remove(point)
                            
                            # Agregar nuevos waypoints
                            for wx, wy in waypoints:
                                point = ET.SubElement(array, 'mxPoint')
                                point.set('x', str(wx))
                                point.set('y', str(wy))
                            
                            connections_updated += 1

print(f"   ✅ {connections_updated} conexiones mejoradas con waypoints")

# Guardar
tree.write('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', encoding='utf-8', xml_declaration=True)
print("\n✅ Diagrama mejorado y guardado")

