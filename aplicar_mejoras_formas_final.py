"""
Aplicar mejoras finales de formas P&ID estándar
"""
import xml.etree.ElementTree as ET
import re

tree = ET.parse('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml')
root = tree.getroot()

# Mejoras de formas para componentes específicos
form_improvements = {
    '8': {  # Manifold - usar paralelogramo
        'shape': 'parallelogram',
        'style_add': 'perimeter=parallelogramPerimeter;strokeWidth=2'
    },
    '10': {  # Regulador 1ra etapa - usar hexágono
        'shape': 'hexagon',
        'style_add': 'perimeter=hexagonPerimeter2;strokeWidth=2'
    },
    '12': {  # Regulador 2da etapa - usar hexágono
        'shape': 'hexagon',
        'style_add': 'perimeter=hexagonPerimeter2;strokeWidth=2'
    },
    '13': {  # ECU - usar rectángulo con borde punteado
        'shape': 'rect',
        'style_add': 'dashed=1;dashPattern=8 8;strokeWidth=2'
    },
    '11': {  # Filtro - mejorar borde
        'style_add': 'strokeWidth=2'
    },
    '56': {  # Filtro baja presión - mejorar borde
        'style_add': 'strokeWidth=2'
    },
    '21': {  # Motor - mejorar borde
        'style_add': 'strokeWidth=2'
    },
}

print("=== APLICANDO MEJORAS DE FORMAS ===\n")

for diagram in root.findall('.//diagram'):
    for mxGraphModel in diagram.findall('.//mxGraphModel'):
        for root_elem in mxGraphModel.findall('.//root'):
            for cell in root_elem.findall('.//mxCell[@id]'):
                cell_id = cell.get('id', '')
                if cell_id in form_improvements:
                    improvement = form_improvements[cell_id]
                    current_style = cell.get('style', '')
                    
                    # Actualizar shape si se especifica
                    if 'shape' in improvement:
                        # Reemplazar shape en el style
                        current_style = re.sub(r'shape=[^;]+', f"shape={improvement['shape']}", current_style)
                        if 'shape=' not in current_style:
                            current_style = f"shape={improvement['shape']};{current_style}" if current_style else f"shape={improvement['shape']}"
                    
                    # Agregar mejoras de estilo
                    if 'style_add' in improvement:
                        for add_style in improvement['style_add'].split(';'):
                            if add_style and add_style not in current_style:
                                current_style = f"{current_style};{add_style}" if current_style else add_style
                    
                    cell.set('style', current_style)
                    print(f"   ✅ Mejorado componente {cell_id}")

# Guardar
tree.write('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', encoding='utf-8', xml_declaration=True)
print("\n✅ Mejoras de formas aplicadas")

