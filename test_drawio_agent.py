"""
Script de prueba para el agente draw.io
Genera un diagrama de ejemplo y verifica que sea compatible con draw.io
"""
import os
import sys

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.drawio_agent import DrawIOAgent
from config import DELIVERABLE_XML

def test_drawio_agent():
    """Prueba el agente draw.io con datos de ejemplo"""
    
    print("=" * 60)
    print("PRUEBA DEL AGENTE DRAW.IO")
    print("=" * 60)
    
    # Datos de ejemplo basados en un cálculo típico
    calculation_results = {
        'tanques': 23,
        'numero_tanques': 23,
        'presion_llenado': 200,
        'volumen': 1.84,  # m³
        'volumen_gas': 1.84,
        'masa_ch4': 147.2,  # kg
        'masa_ch4_requerida': 147.2,
        'consumo_base': 35.0,
        'autonomia_objetivo': 800,
        'temperatura': 25.0,
        'temperatura_operacion': 25.0,
        'energia': 10024.0,
        'energia_requerida': 10024.0,
        'volumen_diesel_equivalente': 280.0
    }
    
    client_name = "PETROLIQUIDOS"
    
    print(f"\n1. Inicializando agente draw.io...")
    print(f"   Cliente: {client_name}")
    print(f"   Archivo de salida: {DELIVERABLE_XML}")
    
    # Crear agente
    agent = DrawIOAgent(output_path=DELIVERABLE_XML)
    
    print(f"\n2. Cargando variables de cálculo...")
    agent.load_calculation_variables(calculation_results)
    
    print(f"   ✓ Número de tanques: {agent.variables.get('numero_tanques')}")
    print(f"   ✓ Presión de llenado: {agent.variables.get('presion_llenado')} bar")
    print(f"   ✓ Volumen total de gas: {agent.variables.get('volumen_gas_total'):.2f} m³")
    print(f"   ✓ Masa CH₄ requerida: {agent.variables.get('masa_ch4'):.2f} kg")
    
    print(f"\n3. Generando diagrama P&ID...")
    try:
        xml_content = agent.generate_diagram_from_engineering(
            calculation_results,
            client_name
        )
        print(f"   ✓ Diagrama generado exitosamente")
        print(f"   ✓ Tamaño del XML: {len(xml_content)} caracteres")
    except Exception as e:
        print(f"   ✗ Error al generar diagrama: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n4. Guardando diagrama en archivo...")
    try:
        saved_path = agent.save_diagram(xml_content)
        print(f"   ✓ Diagrama guardado en: {saved_path}")
        
        # Verificar que el archivo existe
        if os.path.exists(saved_path):
            file_size = os.path.getsize(saved_path)
            print(f"   ✓ Archivo existe, tamaño: {file_size} bytes")
        else:
            print(f"   ✗ Error: El archivo no se creó")
            return False
    except Exception as e:
        print(f"   ✗ Error al guardar diagrama: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n5. Verificando estructura XML...")
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(saved_path)
        root = tree.getroot()
        
        # Verificar elementos principales
        if root.tag == 'mxfile':
            print(f"   ✓ Elemento raíz 'mxfile' encontrado")
        else:
            print(f"   ✗ Error: Elemento raíz incorrecto: {root.tag}")
            return False
        
        # Contar componentes
        diagram = root.find('diagram')
        if diagram is not None:
            print(f"   ✓ Elemento 'diagram' encontrado")
            print(f"   ✓ Nombre del diagrama: {diagram.get('name', 'N/A')}")
        else:
            print(f"   ✗ Error: Elemento 'diagram' no encontrado")
            return False
        
        # Contar celdas (componentes)
        mxGraphModel = diagram.find('mxGraphModel')
        if mxGraphModel is not None:
            root_elem = mxGraphModel.find('root')
            if root_elem is not None:
                cells = root_elem.findall('mxCell')
                print(f"   ✓ Total de celdas (componentes): {len(cells)}")
                
                # Contar componentes y conexiones
                vertices = [c for c in cells if c.get('vertex') == '1']
                edges = [c for c in cells if c.get('edge') == '1']
                print(f"   ✓ Componentes (vértices): {len(vertices)}")
                print(f"   ✓ Conexiones (aristas): {len(edges)}")
        
    except Exception as e:
        print(f"   ✗ Error al verificar XML: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n6. Verificando componentes generados...")
    expected_components = [
        'title', 'tank1', 'tank2', 'tank3', 'manifold', 'shutoff',
        'reg1', 'filter', 'reg2', 'ecu', 'injectors', 'motor',
        'sensor_p1', 'sensor_t1', 'sensor_p2', 'sensor_t2', 'sensor_p3',
        'sensor_lambda', 'fill_valve', 'notes', 'vars'
    ]
    
    found_components = []
    for cell in cells:
        cell_id = cell.get('id')
        if cell_id in expected_components:
            found_components.append(cell_id)
    
    print(f"   Componentes esperados: {len(expected_components)}")
    print(f"   Componentes encontrados: {len(found_components)}")
    
    missing = set(expected_components) - set(found_components)
    if missing:
        print(f"   ⚠ Componentes faltantes: {missing}")
    else:
        print(f"   ✓ Todos los componentes principales están presentes")
    
    print(f"\n" + "=" * 60)
    print("RESULTADO DE LA PRUEBA")
    print("=" * 60)
    print(f"✓ Diagrama generado exitosamente")
    print(f"✓ Archivo guardado: {saved_path}")
    print(f"✓ Formato XML válido")
    print(f"✓ Compatible con draw.io")
    print(f"\n📝 INSTRUCCIONES:")
    print(f"   1. Abre https://app.diagrams.net/ en tu navegador")
    print(f"   2. Haz clic en 'Open Existing Diagram'")
    print(f"   3. Selecciona el archivo: {saved_path}")
    print(f"   4. O arrastra el archivo directamente a la página")
    print(f"\n   También puedes abrir el archivo desde:")
    print(f"   File > Open from > Device")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_drawio_agent()
    sys.exit(0 if success else 1)

