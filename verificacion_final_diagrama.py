"""
Verificación final del diagrama:
- Detecta solapamientos entre elementos
- Verifica que todas las conexiones estén completas
- Completa tags faltantes
"""
import xml.etree.ElementTree as ET
from pathlib import Path

def obtener_posicion_elemento(cell):
    """Obtiene la posición y tamaño de un elemento"""
    geometry = cell.find('mxGeometry')
    if geometry is not None:
        x = float(geometry.get('x', 0))
        y = float(geometry.get('y', 0))
        width = float(geometry.get('width', 0))
        height = float(geometry.get('height', 0))
        return {
            'x': x, 'y': y, 'width': width, 'height': height,
            'right': x + width, 'bottom': y + height
        }
    return None

def elementos_solapan(pos1, pos2, margen=10):
    """Verifica si dos elementos se solapan"""
    return not (pos1['right'] + margen < pos2['x'] or
                pos2['right'] + margen < pos1['x'] or
                pos1['bottom'] + margen < pos2['y'] or
                pos2['bottom'] + margen < pos1['y'])

def verificacion_final(archivo_entrada, archivo_salida):
    """Realiza verificación final del diagrama"""
    
    tree = ET.parse(archivo_entrada)
    root = tree.getroot()
    
    # Obtener todas las posiciones
    elementos = {}
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell_id and cell.get('vertex') == '1':
            pos = obtener_posicion_elemento(cell)
            if pos:
                elementos[cell_id] = {
                    'pos': pos,
                    'cell': cell,
                    'value': cell.get('value', '')
                }
    
    print(f"📊 Verificando {len(elementos)} elementos...")
    
    # Detectar solapamientos
    solapamientos = []
    ids = list(elementos.keys())
    for i, id1 in enumerate(ids):
        for id2 in ids[i+1:]:
            if elementos_solapan(elementos[id1]['pos'], elementos[id2]['pos']):
                solapamientos.append((id1, id2))
    
    if solapamientos:
        print(f"⚠️ Encontrados {len(solapamientos)} solapamientos:")
        for id1, id2 in solapamientos:
            val1 = elementos[id1]['value'][:30] if elementos[id1]['value'] else id1
            val2 = elementos[id2]['value'][:30] if elementos[id2]['value'] else id2
            print(f"   - {id1} ({val1}) <-> {id2} ({val2})")
    else:
        print("✅ No se encontraron solapamientos")
    
    # Verificar conexiones
    conexiones = {}
    for edge in root.findall('.//mxCell[@edge="1"]'):
        source_id = edge.get('source')
        target_id = edge.get('target')
        if source_id and target_id:
            key = f"{source_id}->{target_id}"
            conexiones[key] = {
                'edge': edge,
                'source': source_id,
                'target': target_id,
                'value': edge.get('value', ''),
                'style': edge.get('style', '')
            }
    
    print(f"\n📊 Verificando {len(conexiones)} conexiones...")
    
    # Verificar conexiones faltantes importantes
    conexiones_esperadas = {
        '3->8': 'Gas CNG',
        '4->8': 'Gas CNG',
        '5->8': 'Gas CNG',
        '8->9': '200-250 bar',
        '9->10': 'Gas CNG',
        '10->11': '20-40 bar',
        '11->12': 'Gas Regulado',
        '12->20': '7.0-10.0 bar',
        '20->21': 'Gas a Motor',
        '13->10': 'Señales',
        '13->20': 'Señales',
        '14->13': 'P',
        '15->13': 'T',
        '16->13': 'P',
        '17->13': 'T',
        '18->13': 'P',
        '19->13': 'λ',
        '22->3': 'Llenado'
    }
    
    conexiones_faltantes = []
    for key, label_esperado in conexiones_esperadas.items():
        if key not in conexiones:
            conexiones_faltantes.append((key, label_esperado))
    
    if conexiones_faltantes:
        print(f"⚠️ Conexiones faltantes: {len(conexiones_faltantes)}")
        for key, label in conexiones_faltantes:
            print(f"   - {key}: {label}")
    else:
        print("✅ Todas las conexiones esperadas están presentes")
    
    # Verificar etiquetas de conexiones
    conexiones_sin_etiqueta = []
    for key, conn in conexiones.items():
        if not conn['value'] or conn['value'].strip() == '':
            conexiones_sin_etiqueta.append(key)
    
    if conexiones_sin_etiqueta:
        print(f"⚠️ Conexiones sin etiqueta: {len(conexiones_sin_etiqueta)}")
        # Completar etiquetas
        for key in conexiones_sin_etiqueta:
            if key in conexiones_esperadas:
                conexiones[key]['edge'].set('value', conexiones_esperadas[key])
                print(f"   ✅ Etiqueta añadida a {key}: {conexiones_esperadas[key]}")
    else:
        print("✅ Todas las conexiones tienen etiquetas")
    
    # Verificar tags completos en elementos principales
    tags_faltantes = []
    elementos_importantes = {
        '3': 'Tanque CNG',
        '4': 'Tanque CNG',
        '5': 'Tanque CNG',
        '8': 'Manifold de Distribución',
        '9': 'Válvula Shut-off Automática',
        '10': 'Regulador 1ra Etapa',
        '11': 'Filtro de Gas Alta Presión',
        '12': 'Regulador 2da Etapa',
        '13': 'ECU',
        '20': 'Inyectores de Gas',
        '21': 'Motor Diésel Convertido'
    }
    
    for elem_id, nombre_esperado in elementos_importantes.items():
        if elem_id in elementos:
            value = elementos[elem_id]['value']
            if not value or nombre_esperado.lower() not in value.lower():
                tags_faltantes.append((elem_id, nombre_esperado))
    
    if tags_faltantes:
        print(f"⚠️ Tags incompletos: {len(tags_faltantes)}")
        for elem_id, nombre in tags_faltantes:
            print(f"   - {elem_id}: {nombre}")
    else:
        print("✅ Todos los tags están completos")
    
    # Guardar el archivo
    tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)
    print(f"\n✅ Verificación completada. Archivo guardado en: {archivo_salida}")
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE VERIFICACIÓN")
    print("="*70)
    print(f"✅ Elementos verificados: {len(elementos)}")
    print(f"{'✅' if not solapamientos else '⚠️'} Solapamientos: {len(solapamientos)}")
    print(f"{'✅' if not conexiones_faltantes else '⚠️'} Conexiones faltantes: {len(conexiones_faltantes)}")
    print(f"{'✅' if not conexiones_sin_etiqueta else '⚠️'} Conexiones sin etiqueta: {len(conexiones_sin_etiqueta)}")
    print(f"{'✅' if not tags_faltantes else '⚠️'} Tags incompletos: {len(tags_faltantes)}")
    print("="*70)

if __name__ == "__main__":
    archivo_entrada = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    archivo_salida = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    verificacion_final(archivo_entrada, archivo_salida)

