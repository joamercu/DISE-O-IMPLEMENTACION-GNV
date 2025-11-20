"""
Script para corregir la estructura completa del archivo draw.io
Añade atributos faltantes y corrige el formato
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

def corregir_estructura_drawio(archivo_entrada, archivo_salida):
    """Corrige la estructura completa del archivo draw.io"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Añadir atributos faltantes al elemento mxfile
    if root.tag == 'mxfile':
        if 'modified' not in root.attrib:
            root.set('modified', datetime.now().isoformat() + 'Z')
        if 'etag' not in root.attrib:
            root.set('etag', 'drawio')
        if 'type' not in root.attrib:
            root.set('type', 'device')
    
    # Asegurar que el diagram tenga un ID válido
    for diagram in root.findall('.//diagram'):
        if 'id' not in diagram.attrib or not diagram.attrib['id']:
            diagram.set('id', 'pid-gnv')
    
    # Guardar con formato correcto
    # Usar minidom para formatear correctamente
    from xml.dom import minidom
    
    # Convertir a string y parsear con minidom para formatear
    xml_str = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(xml_str)
    
    # Escribir con formato
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n')
        # Obtener el XML formateado sin la declaración
        xml_pretty = dom.documentElement.toprettyxml(indent='  ', encoding=None)
        # Eliminar la primera línea (declaración XML duplicada)
        lines = xml_pretty.split('\n')
        if lines and '<?xml' in lines[0]:
            lines = lines[1:]
        f.write('\n'.join(lines))
    
    print(f"✅ Archivo corregido guardado en: {archivo_salida}")
    print(f"   Atributos añadidos: modified, etag, type")

if __name__ == "__main__":
    archivo_entrada = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    archivo_salida = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    corregir_estructura_drawio(archivo_entrada, archivo_salida)

