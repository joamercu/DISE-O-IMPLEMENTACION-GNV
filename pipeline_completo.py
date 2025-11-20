"""
Pipeline completo híbrido automatizado para layout ortogonal
Opción A - Solución robusta

Uso:
    python pipeline_completo.py [archivo.drawio.xml] [--output archivo_salida.drawio.xml]
"""
import sys
import argparse
from elk_layout_pipeline import DrawIOGraphExtractor
from elk_layout_engine import OrthogonalLayoutEngine
from xml_applicator import XMLApplicator
from validator import DiagramValidator

def main():
    parser = argparse.ArgumentParser(
        description='Pipeline automatizado para layout ortogonal de diagramas P&ID'
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
        help='Archivo de salida (por defecto: input_file con _LAYOUT)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Solo validar, no aplicar layout'
    )
    parser.add_argument(
        '--skip-layout',
        action='store_true',
        help='Saltar cálculo de layout (solo validar y aplicar waypoints)'
    )
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output or input_file.replace('.drawio.xml', '_LAYOUT.drawio.xml')
    
    print("="*70)
    print("PIPELINE AUTOMATIZADO - LAYOUT ORTOGONAL P&ID")
    print("="*70)
    print(f"📁 Archivo de entrada: {input_file}")
    print(f"📁 Archivo de salida: {output_file}")
    print()
    
    # Paso 1: Extraer grafo
    print("PASO 1: EXTRACCIÓN DE GRAFO")
    print("-" * 70)
    extractor = DrawIOGraphExtractor(input_file)
    graph = extractor.extract()
    print()
    
    # Paso 2: Validación inicial
    print("PASO 2: VALIDACIÓN INICIAL")
    print("-" * 70)
    validator = DiagramValidator(input_file)
    is_valid, errors, warnings = validator.validate_all()
    validator.print_report()
    print()
    
    if args.validate_only:
        print("✅ Modo solo validación - Finalizando")
        return
    
    if not is_valid and errors:
        print("❌ Errores críticos encontrados. Corrija antes de continuar.")
        return
    
    # Paso 3: Calcular layout
    if not args.skip_layout:
        print("PASO 3: CÁLCULO DE LAYOUT ORTOGONAL")
        print("-" * 70)
        layout_engine = OrthogonalLayoutEngine(graph)
        layout_results = layout_engine.calculate_layout()
        print()
    else:
        print("PASO 3: SALTADO (--skip-layout)")
        print("-" * 70)
        layout_results = {'nodes': {}, 'edges': {}}
        print()
    
    # Paso 4: Aplicar al XML
    print("PASO 4: APLICACIÓN AL XML")
    print("-" * 70)
    applicator = XMLApplicator(input_file)
    applicator.apply_layout(layout_results)
    applicator.save(output_file)
    print()
    
    # Paso 5: Validación final
    print("PASO 5: VALIDACIÓN FINAL")
    print("-" * 70)
    final_validator = DiagramValidator(output_file)
    is_valid_final, errors_final, warnings_final = final_validator.validate_all()
    final_validator.print_report()
    print()
    
    # Resumen
    print("="*70)
    print("RESUMEN")
    print("="*70)
    print(f"✅ Grafo extraído: {len(graph.nodes)} nodos, {len(graph.edges)} edges")
    if not args.skip_layout:
        print(f"✅ Layout calculado: {len(layout_results['nodes'])} nodos, {len(layout_results['edges'])} edges")
    print(f"✅ Archivo generado: {output_file}")
    print(f"{'✅' if is_valid_final else '⚠️'} Validación final: {'Válido' if is_valid_final else 'Con advertencias'}")
    print("="*70)
    
    if is_valid_final:
        print("\n🎉 Pipeline completado exitosamente!")
        print(f"📂 Abra {output_file} en draw.io para revisión manual fina")
    else:
        print("\n⚠️ Pipeline completado con advertencias")
        print("Revise el reporte de validación antes de usar el diagrama")

if __name__ == '__main__':
    main()

