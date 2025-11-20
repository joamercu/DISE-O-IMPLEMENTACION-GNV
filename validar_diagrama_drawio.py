"""
Script para validar la compatibilidad de archivos draw.io XML
Verifica estructura, sintaxis y elementos requeridos
"""
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
import re

def validar_xml_estructura(archivo):
    """Valida la estructura básica del XML"""
    errores = []
    advertencias = []
    
    try:
        tree = ET.parse(archivo)
        root = tree.getroot()
        
        # Verificar que la raíz sea mxfile
        if root.tag != 'mxfile':
            errores.append(f"❌ La raíz debe ser 'mxfile', encontrado: {root.tag}")
        else:
            print("✅ Elemento raíz 'mxfile' encontrado")
        
        # Verificar atributos requeridos en mxfile
        if 'host' not in root.attrib:
            advertencias.append("⚠️ Atributo 'host' no encontrado en mxfile")
        else:
            print(f"✅ Atributo 'host': {root.attrib['host']}")
        
        if 'version' not in root.attrib:
            advertencias.append("⚠️ Atributo 'version' no encontrado en mxfile")
        else:
            print(f"✅ Atributo 'version': {root.attrib['version']}")
        
        # Verificar que exista al menos un diagram
        diagrams = root.findall('.//diagram')
        if len(diagrams) == 0:
            errores.append("❌ No se encontró ningún elemento 'diagram'")
        else:
            print(f"✅ Encontrados {len(diagrams)} diagrama(s)")
            for i, diagram in enumerate(diagrams):
                if 'name' in diagram.attrib:
                    print(f"   - Diagrama {i+1}: {diagram.attrib['name']}")
                if 'id' in diagram.attrib:
                    print(f"   - ID: {diagram.attrib['id']}")
        
        # Verificar mxGraphModel
        graph_models = root.findall('.//mxGraphModel')
        if len(graph_models) == 0:
            errores.append("❌ No se encontró ningún elemento 'mxGraphModel'")
        else:
            print(f"✅ Encontrados {len(graph_models)} mxGraphModel(s)")
        
        # Verificar root dentro de mxGraphModel
        roots = root.findall('.//mxGraphModel/root')
        if len(roots) == 0:
            errores.append("❌ No se encontró ningún elemento 'root' dentro de mxGraphModel")
        else:
            print(f"✅ Encontrado elemento 'root'")
        
        # Verificar mxCell
        cells = root.findall('.//mxCell')
        if len(cells) == 0:
            errores.append("❌ No se encontró ningún elemento 'mxCell'")
        else:
            print(f"✅ Encontrados {len(cells)} elemento(s) mxCell")
        
        return errores, advertencias, root
        
    except ET.ParseError as e:
        errores.append(f"❌ Error de parsing XML: {e}")
        return errores, [], None
    except Exception as e:
        errores.append(f"❌ Error inesperado: {e}")
        return errores, [], None

def validar_atributos_mxcell(root):
    """Valida atributos importantes de los elementos mxCell"""
    errores = []
    advertencias = []
    
    cells = root.findall('.//mxCell')
    
    # Contar tipos de elementos
    vertices = 0
    edges = 0
    sin_tipo = 0
    
    for cell in cells:
        # Verificar que tenga id
        if 'id' not in cell.attrib:
            advertencias.append("⚠️ mxCell sin atributo 'id' encontrado")
        
        # Verificar tipo (vertex o edge)
        if 'vertex' in cell.attrib:
            vertices += 1
        elif 'edge' in cell.attrib:
            edges += 1
        else:
            # Algunos mxCell pueden no tener tipo (como el root)
            sin_tipo += 1
    
    print(f"\n📊 Estadísticas de elementos:")
    print(f"   - Vértices: {vertices}")
    print(f"   - Aristas (edges): {edges}")
    print(f"   - Sin tipo (root, etc.): {sin_tipo}")
    
    return errores, advertencias

def validar_caracteres_especiales(archivo):
    """Valida que no haya caracteres problemáticos"""
    errores = []
    advertencias = []
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Caracteres problemáticos conocidos
        caracteres_problematicos = {
            '→': 'Flecha (→) - puede causar problemas',
            'λ': 'Lambda (λ) - puede causar problemas',
            '•': 'Bullet (•) - puede causar problemas',
            '³': 'Superíndice 3 (³) - puede causar problemas',
            '₄': 'Subíndice 4 (₄) - puede causar problemas',
        }
        
        encontrados = []
        for char, desc in caracteres_problematicos.items():
            if char in contenido:
                count = contenido.count(char)
                encontrados.append(f"   - {desc}: {count} ocurrencia(s)")
        
        if encontrados:
            advertencias.append("⚠️ Caracteres especiales encontrados (pueden causar problemas):")
            advertencias.extend(encontrados)
        else:
            print("✅ No se encontraron caracteres especiales problemáticos")
        
        # Verificar codificación UTF-8
        try:
            contenido.encode('utf-8')
            print("✅ Codificación UTF-8 válida")
        except UnicodeEncodeError as e:
            errores.append(f"❌ Error de codificación UTF-8: {e}")
        
        return errores, advertencias
        
    except Exception as e:
        errores.append(f"❌ Error al leer archivo: {e}")
        return errores, advertencias

def validar_sintaxis_xml(archivo):
    """Valida la sintaxis XML básica"""
    errores = []
    
    try:
        # Intentar parsear el XML
        tree = ET.parse(archivo)
        print("✅ Sintaxis XML válida")
        
        # Verificar que tenga declaración XML
        with open(archivo, 'r', encoding='utf-8') as f:
            primera_linea = f.readline().strip()
            if not primera_linea.startswith('<?xml'):
                advertencias = ["⚠️ No se encontró declaración XML al inicio"]
            else:
                print("✅ Declaración XML encontrada")
        
        return errores
        
    except ET.ParseError as e:
        errores.append(f"❌ Error de sintaxis XML: {e}")
        return errores
    except Exception as e:
        errores.append(f"❌ Error al validar sintaxis: {e}")
        return errores

def validar_elementos_requeridos(root):
    """Valida que existan elementos requeridos para draw.io"""
    errores = []
    advertencias = []
    
    # Verificar elementos esenciales
    elementos_requeridos = {
        'mxfile': root,
        'diagram': root.find('.//diagram'),
        'mxGraphModel': root.find('.//mxGraphModel'),
        'root': root.find('.//mxGraphModel/root'),
        'mxCell': root.findall('.//mxCell'),
    }
    
    print("\n🔍 Verificando elementos requeridos:")
    for nombre, elemento in elementos_requeridos.items():
        if elemento is None or (isinstance(elemento, list) and len(elemento) == 0):
            errores.append(f"❌ Elemento requerido '{nombre}' no encontrado")
        else:
            if isinstance(elemento, list):
                print(f"✅ {nombre}: {len(elemento)} encontrado(s)")
            else:
                print(f"✅ {nombre}: encontrado")
    
    return errores, advertencias

def validar_geometrias(root):
    """Valida que las geometrías sean válidas"""
    errores = []
    advertencias = []
    
    geometrias = root.findall('.//mxGeometry')
    print(f"\n📐 Geometrías encontradas: {len(geometrias)}")
    
    geometrias_sin_atributos = 0
    for geom in geometrias:
        if 'x' not in geom.attrib and 'y' not in geom.attrib:
            geometrias_sin_atributos += 1
    
    if geometrias_sin_atributos > 0:
        print(f"   - Geometrías sin coordenadas (relativas): {geometrias_sin_atributos}")
    
    return errores, advertencias

def validar_conexiones(root):
    """Valida que las conexiones (edges) tengan source y target"""
    errores = []
    advertencias = []
    
    edges = [cell for cell in root.findall('.//mxCell') if 'edge' in cell.attrib and cell.attrib.get('edge') == '1']
    
    print(f"\n🔗 Conexiones (edges) encontradas: {len(edges)}")
    
    edges_sin_source = 0
    edges_sin_target = 0
    
    for edge in edges:
        if 'source' not in edge.attrib:
            edges_sin_source += 1
        if 'target' not in edge.attrib:
            edges_sin_target += 1
    
    if edges_sin_source > 0:
        advertencias.append(f"⚠️ {edges_sin_source} edge(s) sin atributo 'source'")
    if edges_sin_target > 0:
        advertencias.append(f"⚠️ {edges_sin_target} edge(s) sin atributo 'target'")
    
    if edges_sin_source == 0 and edges_sin_target == 0:
        print("✅ Todas las conexiones tienen source y target")
    
    return errores, advertencias

def main():
    """Función principal"""
    print("=" * 70)
    print("VALIDADOR DE COMPATIBILIDAD DRAW.IO")
    print("=" * 70)
    
    # Archivo por defecto
    archivo_default = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    else:
        archivo = archivo_default
    
    archivo_path = Path(archivo)
    
    if not archivo_path.exists():
        print(f"\n❌ Error: El archivo no existe: {archivo}")
        print(f"\nUso: python validar_diagrama_drawio.py [archivo.xml]")
        sys.exit(1)
    
    print(f"\n📄 Archivo: {archivo_path}")
    print(f"📂 Tamaño: {archivo_path.stat().st_size} bytes")
    print("=" * 70)
    
    # Realizar todas las validaciones
    todos_errores = []
    todas_advertencias = []
    
    # 1. Validar sintaxis XML
    print("\n[1/7] Validando sintaxis XML...")
    errores = validar_sintaxis_xml(archivo)
    todos_errores.extend(errores)
    
    # 2. Validar estructura
    print("\n[2/7] Validando estructura XML...")
    errores, advertencias, root = validar_xml_estructura(archivo)
    todos_errores.extend(errores)
    todas_advertencias.extend(advertencias)
    
    if root is None:
        print("\n❌ No se puede continuar la validación debido a errores críticos")
        sys.exit(1)
    
    # 3. Validar elementos requeridos
    print("\n[3/7] Validando elementos requeridos...")
    errores, advertencias = validar_elementos_requeridos(root)
    todos_errores.extend(errores)
    todas_advertencias.extend(advertencias)
    
    # 4. Validar atributos mxCell
    print("\n[4/7] Validando atributos mxCell...")
    errores, advertencias = validar_atributos_mxcell(root)
    todos_errores.extend(errores)
    todas_advertencias.extend(advertencias)
    
    # 5. Validar geometrías
    print("\n[5/7] Validando geometrías...")
    errores, advertencias = validar_geometrias(root)
    todos_errores.extend(errores)
    todas_advertencias.extend(advertencias)
    
    # 6. Validar conexiones
    print("\n[6/7] Validando conexiones...")
    errores, advertencias = validar_conexiones(root)
    todos_errores.extend(errores)
    todas_advertencias.extend(advertencias)
    
    # 7. Validar caracteres especiales
    print("\n[7/7] Validando caracteres especiales...")
    errores, advertencias = validar_caracteres_especiales(archivo)
    todos_errores.extend(errores)
    todas_advertencias.extend(advertencias)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 70)
    
    if len(todos_errores) == 0:
        print("\n✅ El archivo es compatible con draw.io")
        print("   No se encontraron errores críticos")
    else:
        print(f"\n❌ Se encontraron {len(todos_errores)} error(es) crítico(s):")
        for error in todos_errores:
            print(f"   {error}")
    
    if len(todas_advertencias) > 0:
        print(f"\n⚠️ Se encontraron {len(todas_advertencias)} advertencia(s):")
        for advertencia in todas_advertencias:
            print(f"   {advertencia}")
    
    print("\n" + "=" * 70)
    
    # Código de salida
    if len(todos_errores) > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()

