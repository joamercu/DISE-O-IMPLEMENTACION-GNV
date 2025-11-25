"""
Verificar que todas las mejoras del plan estén completadas
"""
import xml.etree.ElementTree as ET

def verificar_mejoras(xml_file: str):
    """Verifica que todas las mejoras estén implementadas"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    print("="*80)
    print("VERIFICACIÓN DE MEJORAS COMPLETADAS")
    print("="*80)
    print()
    
    # Verificar 1: Aristas con source y target válidos
    print("1. VERIFICACIÓN DE ARISTAS:")
    all_node_ids = set()
    for cell in root.findall('.//mxCell[@vertex="1"]'):
        node_id = cell.get('id', '')
        if node_id and node_id not in ['0', '1']:
            all_node_ids.add(node_id)
    
    edges_valid = 0
    edges_invalid = 0
    for cell in root.findall('.//mxCell[@edge="1"]'):
        source_id = cell.get('source', '')
        target_id = cell.get('target', '')
        
        if source_id and target_id and source_id in all_node_ids and target_id in all_node_ids:
            edges_valid += 1
        else:
            edges_invalid += 1
    
    print(f"   ✅ Edges válidos: {edges_valid}")
    if edges_invalid > 0:
        print(f"   ⚠️ Edges inválidos: {edges_invalid}")
    else:
        print(f"   ✅ Todas las aristas tienen source y target válidos")
    print()
    
    # Verificar 2: Ruteo ortogonal
    print("2. VERIFICACIÓN DE RUTEO ORTOGONAL:")
    edges_orthogonal = 0
    edges_with_jumps = 0
    edges_with_waypoints = 0
    
    for cell in root.findall('.//mxCell[@edge="1"]'):
        style = cell.get('style', '')
        if 'edgeStyle=orthogonalEdgeStyle' in style:
            edges_orthogonal += 1
        if 'jumpStyle=' in style:
            edges_with_jumps += 1
        
        geo = cell.find('mxGeometry')
        if geo is not None:
            array = geo.find('Array')
            if array is not None and len(array.findall('mxPoint')) > 0:
                edges_with_waypoints += 1
    
    total_edges = len(list(root.findall('.//mxCell[@edge="1"]')))
    print(f"   ✅ Edges con ruteo ortogonal: {edges_orthogonal}/{total_edges}")
    print(f"   ✅ Edges con saltos visuales: {edges_with_jumps}/{total_edges}")
    print(f"   ✅ Edges con waypoints: {edges_with_waypoints}/{total_edges}")
    print()
    
    # Verificar 3: Etiquetado ISA
    print("3. VERIFICACIÓN DE ETIQUETADO ISA:")
    sensors_isa = []
    sensors_without_tag = []
    
    for cell in root.findall('.//mxCell[@vertex="1"]'):
        value = cell.get('value', '')
        if 'PT-' in value or 'TT-' in value or 'LT-' in value or 'FT-' in value or 'XI-' in value:
            sensors_isa.append(cell.get('id', 'unknown'))
            # Verificar que tenga formato completo
            if 'Tag:' not in value and '=' not in value:
                sensors_without_tag.append(cell.get('id', 'unknown'))
    
    print(f"   ✅ Sensores con nomenclatura ISA: {len(sensors_isa)}")
    if sensors_without_tag:
        print(f"   ⚠️ Sensores sin formato completo: {len(sensors_without_tag)}")
    else:
        print(f"   ✅ Todos los sensores tienen formato ISA completo")
    print()
    
    # Verificar 4: Validación general
    print("4. VALIDACIÓN GENERAL:")
    print(f"   ✅ Total nodos: {len(all_node_ids)}")
    print(f"   ✅ Total edges: {total_edges}")
    print(f"   ✅ Estructura XML válida")
    print()
    
    # Resumen
    print("="*80)
    print("RESUMEN")
    print("="*80)
    all_ok = (edges_invalid == 0 and 
              edges_orthogonal == total_edges and 
              len(sensors_without_tag) == 0)
    
    if all_ok:
        print("✅ TODAS LAS MEJORAS COMPLETADAS EXITOSAMENTE")
    else:
        print("⚠️ Algunas mejoras requieren atención:")
        if edges_invalid > 0:
            print(f"   • {edges_invalid} edges con conexiones inválidas")
        if edges_orthogonal < total_edges:
            print(f"   • {total_edges - edges_orthogonal} edges sin ruteo ortogonal")
        if len(sensors_without_tag) > 0:
            print(f"   • {len(sensors_without_tag)} sensores sin formato completo")
    print("="*80)

if __name__ == '__main__':
    verificar_mejoras('diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.xml')




