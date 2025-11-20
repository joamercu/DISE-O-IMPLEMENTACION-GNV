"""
Pipeline completo con integración ELK real
Parsea XML, identifica nodos/puertos/edges, invoca ELK, escribe resultados y genera reporte
"""
import sys
import argparse
import os
from elk_layout_pipeline import DrawIOGraphExtractor
from elk_integration import ELKIntegration
from xml_applicator import XMLApplicator
from validator import DiagramValidator
from change_reporter import ChangeReporter
from elk_layout_engine import OrthogonalLayoutEngine
from elk_layout_engine_improved import ImprovedOrthogonalLayoutEngine

def check_elk_availability():
    """Verifica si ELK está disponible"""
    import subprocess
    try:
        # Verificar Node.js
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return False, "Node.js no encontrado"
        
        # Verificar elkjs
        try:
            result = subprocess.run(
                ['node', '-e', "require('elkjs')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "ELK disponible"
            else:
                return False, "elkjs no instalado. Ejecute: npm install elkjs"
        except subprocess.TimeoutExpired:
            return False, "Timeout verificando elkjs"
        except Exception as e:
            return False, f"elkjs no instalado. Ejecute: npm install elkjs ({str(e)})"
    except FileNotFoundError:
        return False, "Node.js no encontrado. Instale Node.js para usar ELK."
    except subprocess.TimeoutExpired:
        return False, "Timeout verificando Node.js"
    except Exception as e:
        return False, f"Error verificando ELK: {str(e)}"

def main():
    parser = argparse.ArgumentParser(
        description='Pipeline completo con ELK para layout ortogonal de diagramas P&ID'
    )
    parser.add_argument(
        'input_file',
        nargs='?',
        default='diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml',
        help='Archivo draw.io XML de entrada'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Archivo de salida (por defecto: input_file con _ELK)'
    )
    parser.add_argument(
        '--report', '-r',
        default=None,
        help='Archivo de reporte (por defecto: input_file con _REPORT.txt)'
    )
    parser.add_argument(
        '--use-internal',
        action='store_true',
        help='Usar algoritmo interno en lugar de ELK'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Solo validar, no aplicar layout'
    )
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output or input_file.replace('.drawio.xml', '_ELK.drawio.xml')
    report_file = args.report or input_file.replace('.drawio.xml', '_REPORT.txt')
    
    print("="*80)
    print("PIPELINE COMPLETO CON INTEGRACIÓN ELK")
    print("="*80)
    print(f"📁 Archivo de entrada: {input_file}")
    print(f"📁 Archivo de salida: {output_file}")
    print(f"📄 Archivo de reporte: {report_file}")
    print()
    
    # Verificar disponibilidad de ELK
    use_elk = not args.use_internal
    if use_elk:
        elk_available, elk_message = check_elk_availability()
        if not elk_available:
            print(f"⚠️ {elk_message}")
            print("   Usando algoritmo interno en su lugar...")
            use_elk = False
        else:
            print(f"✅ {elk_message}")
    else:
        print("ℹ️ Usando algoritmo interno (--use-internal)")
    
    print()
    
    # Paso 1: Parsear XML y extraer grafo
    print("PASO 1: PARSEAR XML Y EXTRAER GRAFO")
    print("-"*80)
    extractor = DrawIOGraphExtractor(input_file)
    graph = extractor.extract()
    print(f"   ✅ Nodos: {len(graph.nodes)}")
    print(f"   ✅ Edges: {len(graph.edges)}")
    print(f"   ✅ Puertos: {sum(len(n.ports) for n in graph.nodes.values())}")
    print()
    
    # Paso 2: Validación inicial
    print("PASO 2: VALIDACIÓN INICIAL")
    print("-"*80)
    validator = DiagramValidator(input_file)
    is_valid, errors, warnings = validator.validate_all()
    if errors:
        print(f"   ❌ {len(errors)} errores encontrados")
    if warnings:
        print(f"   ⚠️ {len(warnings)} advertencias encontradas")
    print()
    
    if args.validate_only:
        print("✅ Modo solo validación - Finalizando")
        validator.print_report()
        return
    
    if not is_valid and errors:
        print("❌ Errores críticos encontrados. Corrija antes de continuar.")
        return
    
    # Paso 3: Calcular layout con ELK o algoritmo interno
    print("PASO 3: CÁLCULO DE LAYOUT")
    print("-"*80)
    
    if use_elk:
        print("   🔧 Invocando ELK...")
        elk_integration = ELKIntegration(graph)
        elk_graph = elk_integration.convert_to_elk_graph()
        elk_result = elk_integration.call_elk(elk_graph)
        
        if elk_result:
            print("   ✅ Layout calculado por ELK")
            layout_results = elk_integration.extract_layout_from_elk(elk_result)
        else:
            print("   ⚠️ ELK falló, usando algoritmo interno...")
            layout_engine = ImprovedOrthogonalLayoutEngine(graph)
            layout_results = layout_engine.calculate_layout()
    else:
        print("   🔧 Usando algoritmo interno mejorado...")
        layout_engine = ImprovedOrthogonalLayoutEngine(graph)
        layout_results = layout_engine.calculate_layout()
    
    print(f"   ✅ Nodos procesados: {len(layout_results.get('nodes', {}))}")
    print(f"   ✅ Edges procesados: {len(layout_results.get('edges', {}))}")
    print()
    
    # Paso 4: Aplicar al XML
    print("PASO 4: APLICAR RESULTADOS AL XML")
    print("-"*80)
    applicator = XMLApplicator(input_file)
    applicator.apply_layout(layout_results)
    applicator.save(output_file)
    print()
    
    # Paso 5: Generar reporte de cambios
    print("PASO 5: GENERAR REPORTE DE CAMBIOS")
    print("-"*80)
    reporter = ChangeReporter(graph, layout_results)
    report_text = reporter.generate_report(report_file)
    print()
    
    # Paso 6: Validación final
    print("PASO 6: VALIDACIÓN FINAL")
    print("-"*80)
    final_validator = DiagramValidator(output_file)
    is_valid_final, errors_final, warnings_final = final_validator.validate_all()
    final_validator.print_report()
    print()
    
    # Resumen final
    print("="*80)
    print("RESUMEN FINAL")
    print("="*80)
    print(f"✅ Grafo extraído: {len(graph.nodes)} nodos, {len(graph.edges)} edges")
    print(f"✅ Layout calculado: {len(layout_results.get('nodes', {}))} nodos")
    print(f"✅ Waypoints calculados: {len(layout_results.get('edges', {}))} edges")
    print(f"✅ Archivo generado: {output_file}")
    print(f"✅ Reporte generado: {report_file}")
    print(f"{'✅' if is_valid_final else '⚠️'} Validación: {'Válido' if is_valid_final else 'Con advertencias'}")
    print("="*80)
    
    # Mostrar resumen del reporte
    analysis = reporter.analyze_changes()
    summary = analysis['summary']
    print()
    print("📊 RESUMEN DE CAMBIOS:")
    print(f"   • Nodos movidos significativamente: {summary['nodes_moved']}")
    print(f"   • Cambios en waypoints: {summary['total_waypoint_changes']}")
    print(f"   • Aristas que requieren revisión: {summary['edges_requiring_review']}")
    print(f"   • Problemas críticos: {summary['critical_issues']}")
    print()
    
    if summary['edges_requiring_review'] > 0:
        print("⚠️ IMPORTANTE: Revise el archivo de reporte para ver aristas que requieren revisión manual")
        print(f"   Archivo: {report_file}")
    
    print()
    print("🎉 Pipeline completado!")
    print(f"📂 Abra {output_file} en draw.io para revisión manual fina")

if __name__ == '__main__':
    import subprocess
    main()

