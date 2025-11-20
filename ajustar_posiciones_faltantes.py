import xml.etree.ElementTree as ET

# Leer el archivo
tree = ET.parse('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml')
root = tree.getroot()

# Componentes que necesitan actualización de posición
component_updates = {
    '9': (850, 200),     # Válvula Shut-off (entre manifold y regulador)
    '49': (950, 200),    # Válvula EFC (después de manifold)
    '56': (1800, 200),   # Filtro baja presión (después de regulador 2da)
    '20': (1800, 400),   # Inyectores
    '21': (1800, 550),   # Motor
    '19': (2000, 450),   # LT-301
    '55': (1900, 200),   # FT-401
    '52': (2100, 50),    # Conmutador
    '53': (2100, 150),   # Indicador presión
    '54': (2100, 250),   # Indicador nivel
    '60': (1100, 650),   # Puerto OBD-II
    '61': (1300, 650),   # Sistema registro
    '22': (50, 450),     # Válvula llenado
    '50': (50, 580),     # Sensor fugas
    '51': (50, 680),     # Válvula cierre rápido
    '57': (950, 350),    # Punto venteo
    '58': (200, 580),    # Sistema ventilación
    '59': (350, 580),    # Soportes
    '37': (50, 1000),    # NOTAS
    '38': (550, 1000),   # VARIABLES
    '39': (50, 850),     # LEYENDA
    '40': (50, 900),     # Tanque leyenda
    '41': (140, 900),    # Regulador leyenda
    '42': (230, 900),    # Válvula leyenda
    '43': (320, 900),    # Sensor leyenda
    '44': (390, 900),    # ECU leyenda
}

# Actualizar posiciones
for diagram in root.findall('.//diagram'):
    for mxGraphModel in diagram.findall('.//mxGraphModel'):
        for root_elem in mxGraphModel.findall('.//root'):
            for cell in root_elem.findall('.//mxCell[@id]'):
                cell_id = cell.get('id', '')
                if cell_id in component_updates:
                    geo = cell.find('mxGeometry')
                    if geo is not None:
                        new_x, new_y = component_updates[cell_id]
                        geo.set('x', str(new_x))
                        geo.set('y', str(new_y))

# Guardar
tree.write('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', encoding='utf-8', xml_declaration=True)
print('✅ Posiciones de componentes faltantes actualizadas')

