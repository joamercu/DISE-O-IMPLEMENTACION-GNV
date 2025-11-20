import re

# Leer el archivo
with open('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# Eliminar todos los mxPoint vacíos dentro de mxGeometry
content = re.sub(r'\s*<mxPoint as="offset" />\s*\n\s*</mxGeometry>', '</mxGeometry>', content)
content = re.sub(r'\s*<mxPoint as="offset" />\s*</mxGeometry>', '</mxGeometry>', content)

# Guardar
with open('diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Elementos mxPoint vacíos eliminados de todos los puertos')

