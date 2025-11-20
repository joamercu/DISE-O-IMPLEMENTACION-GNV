import re

# Leer el archivo
with open('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# Mapeo de puertos a componentes y atributos
port_replacements = {
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

# Eliminar todos los puertos (celdas con id="port_...")
content = re.sub(r'          <mxCell id="port_[^"]*"[^>]*>.*?</mxCell>\s*\n', '', content, flags=re.DOTALL)

# Reemplazar referencias a puertos en source y target
for port_id, (comp_id, exit_attrs, entry_attrs) in port_replacements.items():
    # Reemplazar en source
    pattern = rf'source="{re.escape(port_id)}"'
    replacement = f'source="{comp_id}"'
    content = re.sub(pattern, replacement, content)
    
    # Reemplazar en target
    pattern = rf'target="{re.escape(port_id)}"'
    replacement = f'target="{comp_id}"'
    content = re.sub(pattern, replacement, content)
    
    # Agregar exitX/exitY cuando source es este puerto
    pattern = rf'(source="{comp_id}"[^>]*style="[^"]*)"'
    def add_exit(match):
        style = match.group(1)
        if 'exitX' not in style and 'exitY' not in style:
            style = style.rstrip('"') + ';' + exit_attrs + '"'
        return style
    content = re.sub(pattern, add_exit, content)
    
    # Agregar entryX/entryY cuando target es este puerto
    pattern = rf'(target="{comp_id}"[^>]*style="[^"]*)"'
    def add_entry(match):
        style = match.group(1)
        if 'entryX' not in style and 'entryY' not in style:
            style = style.rstrip('"') + ';' + entry_attrs + '"'
        return style
    content = re.sub(pattern, add_entry, content)

# Guardar
with open('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Puertos eliminados y conexiones actualizadas')

