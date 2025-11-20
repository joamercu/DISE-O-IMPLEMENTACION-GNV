"""
Verificación final del diagrama mejorado
"""
import xml.etree.ElementTree as ET

tree = ET.parse('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml')
root = tree.getroot()

print("=== VERIFICACIÓN FINAL DEL DIAGRAMA ===\n")

# Verificar componentes
components = {}
for cell in root.findall('.//mxCell[@vertex="1"]'):
    comp_id = cell.get('id', '')
    value = cell.get('value', '')
    if comp_id and value:
        components[comp_id] = value

print(f"✅ Total componentes: {len(components)}")

# Verificar conexiones
edges = []
for cell in root.findall('.//mxCell[@edge="1"]'):
    edge = {
        'id': cell.get('id', ''),
        'source': cell.get('source', ''),
        'target': cell.get('target', ''),
        'value': cell.get('value', ''),
    }
    edges.append(edge)

print(f"✅ Total conexiones: {len(edges)}")

# Verificar que todas las conexiones tengan source y target
valid_edges = [e for e in edges if e['source'] and e['target']]
print(f"✅ Conexiones válidas: {len(valid_edges)}/{len(edges)}")

# Verificar flujo principal
print("\n=== FLUJO PRINCIPAL DE GAS ===")
flow_path = [
    ('3,4,5', '8', 'Tanques → Manifold'),
    ('8', '49', 'Manifold → EFC'),
    ('49', '9', 'EFC → Shut-off'),
    ('9', '10', 'Shut-off → Regulador 1ra'),
    ('10', '11', 'Regulador 1ra → Filtro Alta'),
    ('11', '12', 'Filtro Alta → Regulador 2da'),
    ('12', '56', 'Regulador 2da → Filtro Baja'),
    ('56', '20', 'Filtro Baja → Inyectores'),
    ('20', '21', 'Inyectores → Motor'),
]

for source_ids, target_id, description in flow_path:
    source_list = source_ids.split(',')
    found = False
    for source_id in source_list:
        if any(e['source'] == source_id and e['target'] == target_id for e in edges):
            found = True
            break
    status = "✅" if found else "❌"
    print(f"   {status} {description}")

# Verificar conexiones de control
print("\n=== CONEXIONES DE CONTROL ===")
control_connections = [
    ('13', '10', 'ECU → Regulador 1ra'),
    ('13', '20', 'ECU → Inyectores'),
    ('14,15,16,17,18', '13', 'Sensores → ECU'),
    ('19', '13', 'Lambda → ECU'),
    ('55', '13', 'Flujo → ECU'),
    ('50', '13', 'Fugas → ECU'),
]

for source_ids, target_id, description in control_connections:
    source_list = source_ids.split(',')
    found = False
    for source_id in source_list:
        if any(e['source'] == source_id and e['target'] == target_id for e in edges):
            found = True
            break
    status = "✅" if found else "❌"
    print(f"   {status} {description}")

# Verificar formas mejoradas
print("\n=== FORMAS MEJORADAS ===")
shapes_check = {
    '8': ('parallelogram', 'Manifold'),
    '10': ('hexagon', 'Regulador 1ra'),
    '12': ('hexagon', 'Regulador 2da'),
    '13': ('rect', 'ECU'),
}

for comp_id, (expected_shape, name) in shapes_check.items():
    for cell in root.findall(f'.//mxCell[@id="{comp_id}"]'):
        style = cell.get('style', '')
        has_shape = expected_shape in style
        status = "✅" if has_shape else "⚠️"
        print(f"   {status} {name}: {expected_shape}")

print("\n✅ Verificación completada")

