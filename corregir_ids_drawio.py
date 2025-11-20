"""
Script para corregir IDs en archivos draw.io y resolver el error "setId is not a function"
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import re

def corregir_ids_drawio(archivo_entrada, archivo_salida):
    """Corrige los IDs del archivo draw.io para que sean compatibles"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Mapeo de IDs antiguos a nuevos (numéricos)
    id_map = {}
    contador = 2  # Empezar desde 2 (0 y 1 ya existen)
    
    # Primero, identificar todos los elementos que necesitan IDs
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell_id and cell_id not in ['0', '1']:
            # Si el ID no es numérico, crear uno nuevo
            if not cell_id.isdigit():
                nuevo_id = str(contador)
                id_map[cell_id] = nuevo_id
                cell.set('id', nuevo_id)
                contador += 1
    
    # Actualizar referencias en atributos source y target
    for cell in root.findall('.//mxCell'):
        source = cell.get('source')
        target = cell.get('target')
        
        if source and source in id_map:
            cell.set('source', id_map[source])
        if target and target in id_map:
            cell.set('target', id_map[target])
    
    # Guardar el archivo corregido
    tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)
    print(f"✅ Archivo corregido guardado en: {archivo_salida}")
    print(f"   IDs corregidos: {len(id_map)}")

if __name__ == "__main__":
    archivo_original = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19.drawio.xml"
    archivo_corregido = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    corregir_ids_drawio(archivo_original, archivo_corregido)

