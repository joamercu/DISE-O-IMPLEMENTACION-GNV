"""
Script para corregir y completar todas las conexiones del diagrama P&ID
"""
import xml.etree.ElementTree as ET

# Leer el archivo
tree = ET.parse('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml')
root = tree.getroot()

# Obtener el siguiente ID disponible
def get_next_id(root_elem):
    max_id = 0
    for cell in root_elem.findall('.//mxCell[@id]'):
        try:
            cell_id = int(cell.get('id', '0'))
            max_id = max(max_id, cell_id)
        except:
            pass
    return max_id + 1

# Conexiones que deben existir según el flujo del sistema
required_connections = [
    # Flujo principal de gas
    {'source': '49', 'target': '9', 'label': 'Gas CNG\n200-250 bar', 'style': 'endArrow=classic;html=1;strokeWidth=3;strokeColor=#6c8ebf;edgeStyle=orthogonalEdgeStyle;jumpStyle=arc;jettySize=8;fontSize=10;exitX=1;exitY=0.5;entryX=0;entryY=0.5'},
    
    # Conexión desde filtro baja presión a inyectores (ya existe id=65, verificar)
    # Conexión desde válvula EFC a shut-off (falta)
]

print("=== CORRIGIENDO CONEXIONES ===\n")

# Verificar y agregar conexiones faltantes
for diagram in root.findall('.//diagram'):
    for mxGraphModel in diagram.findall('.//mxGraphModel'):
        for root_elem in mxGraphModel.findall('.//root'):
            next_id = get_next_id(root_elem)
            
            # Verificar si existe conexión de EFC (49) a Shut-off (9)
            efc_to_shutoff_exists = False
            for cell in root_elem.findall('.//mxCell[@edge="1"]'):
                if cell.get('source') == '49' and cell.get('target') == '9':
                    efc_to_shutoff_exists = True
                    break
            
            if not efc_to_shutoff_exists:
                print("   ➕ Agregando conexión: Válvula EFC → Válvula Shut-off")
                new_edge = ET.SubElement(root_elem, 'mxCell')
                new_edge.set('id', str(next_id))
                new_edge.set('value', 'Gas CNG\n200-250 bar')
                new_edge.set('style', 'endArrow=classic;html=1;strokeWidth=3;strokeColor=#6c8ebf;edgeStyle=orthogonalEdgeStyle;jumpStyle=arc;jettySize=8;fontSize=10;exitX=1;exitY=0.5;entryX=0;entryY=0.5')
                new_edge.set('edge', '1')
                new_edge.set('source', '49')
                new_edge.set('target', '9')
                new_edge.set('parent', '1')
                
                geo = ET.SubElement(new_edge, 'mxGeometry')
                geo.set('width', '50')
                geo.set('height', '50')
                geo.set('relative', '1')
                geo.set('as', 'geometry')
                
                array = ET.SubElement(geo, 'Array')
                array.set('as', 'points')
                next_id += 1
            
            # Corregir conexión existente de manifold a EFC (debe ser directa)
            for cell in root_elem.findall('.//mxCell[@edge="1"]'):
                if cell.get('source') == '8' and cell.get('target') == '49':
                    # Mejorar waypoints
                    geo = cell.find('mxGeometry')
                    if geo is not None:
                        array = geo.find('Array')
                        if array is None:
                            array = ET.SubElement(geo, 'Array')
                            array.set('as', 'points')
                        
                        # Limpiar waypoints existentes
                        for point in array.findall('mxPoint'):
                            array.remove(point)
                        
                        # Waypoints mejorados
                        point1 = ET.SubElement(array, 'mxPoint')
                        point1.set('x', '840')
                        point1.set('y', '230')
                        
                        point2 = ET.SubElement(array, 'mxPoint')
                        point2.set('x', '950')
                        point2.set('y', '230')
            
            # Verificar conexión de filtro baja presión a inyectores
            flp_to_inj_exists = False
            for cell in root_elem.findall('.//mxCell[@edge="1"]'):
                if cell.get('source') == '56' and cell.get('target') == '20':
                    flp_to_inj_exists = True
                    # Mejorar waypoints de esta conexión
                    geo = cell.find('mxGeometry')
                    if geo is not None:
                        array = geo.find('Array')
                        if array is None:
                            array = ET.SubElement(geo, 'Array')
                            array.set('as', 'points')
                        
                        # Limpiar y agregar waypoints mejorados
                        for point in array.findall('mxPoint'):
                            array.remove(point)
                        
                        # Waypoints verticales para conectar filtro a inyectores
                        point1 = ET.SubElement(array, 'mxPoint')
                        point1.set('x', '1850')
                        point1.set('y', '320')
                        
                        point2 = ET.SubElement(array, 'mxPoint')
                        point2.set('x', '1880')
                        point2.set('y', '320')
                        
                        point3 = ET.SubElement(array, 'mxPoint')
                        point3.set('x', '1880')
                        point3.set('y', '400')
                    break
            
            if not flp_to_inj_exists:
                print("   ➕ Agregando conexión: Filtro Baja Presión → Inyectores")
                new_edge = ET.SubElement(root_elem, 'mxCell')
                new_edge.set('id', str(next_id))
                new_edge.set('value', 'Gas a Inyectores\n7-10 bar')
                new_edge.set('style', 'endArrow=classic;html=1;strokeWidth=2;strokeColor=#82b366;edgeStyle=orthogonalEdgeStyle;jumpStyle=arc;jettySize=8;fontSize=10;exitX=1;exitY=0.5;entryX=0.5;entryY=0')
                new_edge.set('edge', '1')
                new_edge.set('source', '56')
                new_edge.set('target', '20')
                new_edge.set('parent', '1')
                
                geo = ET.SubElement(new_edge, 'mxGeometry')
                geo.set('width', '50')
                geo.set('height', '50')
                geo.set('relative', '1')
                geo.set('as', 'geometry')
                
                array = ET.SubElement(geo, 'Array')
                array.set('as', 'points')
                
                point1 = ET.SubElement(array, 'mxPoint')
                point1.set('x', '1850')
                point1.set('y', '320')
                
                point2 = ET.SubElement(array, 'mxPoint')
                point2.set('x', '1880')
                point2.set('y', '320')
                
                point3 = ET.SubElement(array, 'mxPoint')
                point3.set('x', '1880')
                point3.set('y', '400')
                next_id += 1

# Guardar
tree.write('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', encoding='utf-8', xml_declaration=True)
print("\n✅ Conexiones corregidas y completadas")

