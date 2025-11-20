import xml.etree.ElementTree as ET
import re

# Leer el archivo
tree = ET.parse('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml')
root = tree.getroot()

# Mapeo de puertos a componentes principales y posiciones
port_mapping = {
    'port_t3_e': ('3', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_t4_e': ('4', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_t5_e': ('5', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_m_w': ('8', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_m_e': ('8', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_vso_w': ('9', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_vso_e': ('9', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_r1_w': ('10', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_r1_e': ('10', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_r1_n': ('10', 'exitX=0.5;exitY=0', 'entryX=0.5;entryY=1'),
    'port_fhp_w': ('11', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_fhp_e': ('11', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_r2_w': ('12', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_r2_e': ('12', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_r2_s': ('12', 'exitX=0.5;exitY=1', 'entryX=0.5;entryY=0'),
    'port_flp_w': ('56', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_flp_e': ('56', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_inj_n': ('20', 'exitX=0.5;exitY=1', 'entryX=0.5;entryY=0'),
    'port_inj_s': ('20', 'exitX=0.5;exitY=1', 'entryX=0.5;entryY=0'),
    'port_inj_w': ('20', 'exitX=0.5;exitY=1', 'entryX=0.5;entryY=0'),
    'port_ecu_n': ('13', 'exitX=0.5;exitY=0', 'entryX=0.5;entryY=1'),
    'port_ecu_s': ('13', 'exitX=0.5;exitY=1', 'entryX=0.5;entryY=0'),
    'port_ecu_e': ('13', 'exitX=1;exitY=0.5', 'entryX=0;entryY=0.5'),
    'port_ecu_w': ('13', 'exitX=0;exitY=0.5', 'entryX=0.5;entryY=0'),
}

# Encontrar y eliminar todos los puertos
for diagram in root.findall('.//diagram'):
    for mxGraphModel in diagram.findall('.//mxGraphModel'):
        for root_elem in mxGraphModel.findall('.//root'):
            # Eliminar puertos (celdas con id que empieza con "port_")
            for cell in root_elem.findall('.//mxCell[@id]'):
                cell_id = cell.get('id', '')
                if cell_id.startswith('port_'):
                    parent = cell.getparent()
                    if parent is not None:
                        parent.remove(cell)
            
            # Actualizar conexiones para usar componentes principales
            for edge in root_elem.findall('.//mxCell[@edge="1"]'):
                source = edge.get('source')
                target = edge.get('target')
                
                if source and source.startswith('port_'):
                    if source in port_mapping:
                        comp_id, exit_attrs, _ = port_mapping[source]
                        edge.set('source', comp_id)
                        # Actualizar style para incluir exitX/exitY
                        style = edge.get('style', '')
                        # Extraer exitX/exitY del mapeo
                        exit_parts = exit_attrs.split(';')
                        for part in exit_parts:
                            if 'exitX' in part or 'exitY' in part:
                                if part not in style:
                                    style = style + ';' + part if style else part
                        edge.set('style', style)
                
                if target and target.startswith('port_'):
                    if target in port_mapping:
                        comp_id, _, entry_attrs = port_mapping[target]
                        edge.set('target', comp_id)
                        # Actualizar style para incluir entryX/entryY
                        style = edge.get('style', '')
                        entry_parts = entry_attrs.split(';')
                        for part in entry_parts:
                            if 'entryX' in part or 'entryY' in part:
                                if part not in style:
                                    style = style + ';' + part if style else part
                        edge.set('style', style)

# Guardar
tree.write('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', encoding='utf-8', xml_declaration=True)
print('✅ Puertos eliminados y conexiones actualizadas para usar componentes principales')

