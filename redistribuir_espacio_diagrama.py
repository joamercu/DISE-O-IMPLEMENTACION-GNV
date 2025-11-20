import xml.etree.ElementTree as ET
import re

# Leer el archivo
tree = ET.parse('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml')
root = tree.getroot()

# Aumentar tamaño del canvas
for mxGraphModel in root.findall('.//mxGraphModel'):
    mxGraphModel.set('pageWidth', '2400')
    mxGraphModel.set('pageHeight', '1800')

# Mapeo de componentes y sus nuevas posiciones con espaciado adecuado
# Formato: (id, nueva_x, nueva_y)
component_positions = {
    # Título
    '2': (700, 20),
    
    # Tanques CNG (izquierda, más separados)
    '3': (50, 200),      # Tanque 1
    '4': (200, 200),     # Tanque 2
    '5': (350, 200),     # Tanque 3
    '6': (500, 200),     # Texto "...21 tanques más"
    '7': (150, 80),      # PRV
    
    # Válvula de llenado y componentes de seguridad (izquierda abajo)
    '22': (50, 450),     # Válvula de llenado
    '50': (50, 580),     # Sensor de fugas
    '51': (50, 680),     # Válvula cierre rápido
    
    # Manifold (centro-izquierda, más espacio)
    '8': (700, 200),     # Manifold
    
    # Válvula EFC y punto de venteo
    '49': (900, 200),    # Válvula EFC
    '57': (900, 350),    # Punto de venteo
    
    # Regulador 1ra etapa (centro, más espacio arriba)
    '10': (1100, 200),   # Regulador 1ra etapa
    '14': (1000, 200),   # PT-HP-101
    '15': (1100, 100),   # TT-HP-201
    
    # Filtro alta presión
    '11': (1350, 200),   # Filtro alta presión
    '16': (1300, 200),   # PT-IP-102
    '17': (1400, 100),   # TT-IP-202
    
    # Regulador 2da etapa
    '12': (1600, 200),   # Regulador 2da etapa
    '18': (1700, 100),   # PT-LP-103
    
    # Filtro baja presión
    '56': (1850, 200),   # Filtro baja presión
    '55': (1950, 200),   # FT-401
    
    # Inyectores y motor (derecha)
    '20': (1850, 400),   # Inyectores
    '21': (1850, 550),   # Motor
    '19': (2050, 450),   # LT-301
    
    # ECU (centro-abajo, más espacio)
    '13': (1100, 500),   # ECU
    
    # Componentes de control (derecha arriba)
    '52': (2100, 50),    # Conmutador
    '53': (2100, 150),   # Indicador presión
    '54': (2100, 250),   # Indicador nivel
    
    # Componentes de diagnóstico (centro-abajo)
    '60': (1100, 650),   # Puerto OBD-II
    '61': (1300, 650),   # Sistema registro
    
    # Componentes de infraestructura (izquierda abajo)
    '58': (200, 580),    # Sistema ventilación
    '59': (350, 580),    # Soportes
    
    # Leyenda (abajo izquierda)
    '39': (50, 850),     # LEYENDA
    '40': (50, 900),     # Tanque CNG
    '41': (140, 900),    # Regulador
    '42': (230, 900),    # Válvula
    '43': (320, 900),    # Sensor
    '44': (390, 900),    # ECU
    
    # Notas y variables (abajo)
    '37': (50, 1000),    # NOTAS
    '38': (550, 1000),   # VARIABLES DEL PROYECTO
}

# Actualizar posiciones de componentes
for diagram in root.findall('.//diagram'):
    for mxGraphModel in diagram.findall('.//mxGraphModel'):
        for root_elem in mxGraphModel.findall('.//root'):
            for cell in root_elem.findall('.//mxCell[@id]'):
                cell_id = cell.get('id', '')
                if cell_id in component_positions:
                    geo = cell.find('mxGeometry')
                    if geo is not None:
                        new_x, new_y = component_positions[cell_id]
                        geo.set('x', str(new_x))
                        geo.set('y', str(new_y))

# Guardar
tree.write('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', encoding='utf-8', xml_declaration=True)
print('✅ Espacio de trabajo ampliado y componentes redistribuidos con espaciado adecuado')
print('   Nuevo tamaño: 2400 x 1800 puntos')

