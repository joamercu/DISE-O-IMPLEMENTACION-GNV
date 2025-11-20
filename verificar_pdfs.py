#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar que todos los PDFs en el proyecto sean válidos
Uso: python verificar_pdfs.py
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.pdf_validator import validar_pdfs_en_directorio


def main():
    """Función principal para verificar PDFs"""
    print("=" * 70)
    print("VERIFICACIÓN DE ARCHIVOS PDF EN EL PROYECTO")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    directorios = [
        base_dir / "outputs",
        base_dir / "docs",
        base_dir / "cliente 1 - petroliquidos_20251119_132911" / "outputs"
    ]
    
    todos_los_resultados = {}
    hay_errores = False
    
    for directorio in directorios:
        if directorio.exists():
            print(f"\n📁 Validando PDFs en: {directorio.relative_to(base_dir)}")
            print("-" * 70)
            
            resultados = validar_pdfs_en_directorio(str(directorio), recursivo=True)
            todos_los_resultados[str(directorio)] = resultados
            
            print(f"Total de archivos PDF encontrados: {resultados['total_archivos']}")
            print(f"✅ Archivos válidos: {resultados['archivos_validos']}")
            print(f"❌ Archivos inválidos: {resultados['archivos_invalidos']}")
            print(f"⚠️  Archivos con advertencias: {resultados['archivos_con_warnings']}")
            
            # Mostrar detalles de archivos inválidos
            if resultados['archivos_invalidos'] > 0:
                hay_errores = True
                print("\n❌ ARCHIVOS INVÁLIDOS:")
                for archivo, info in resultados['resultados'].items():
                    if not info.get('is_valid_pdf', False):
                        archivo_path = Path(archivo)
                        print(f"\n  📄 {archivo_path.name}")
                        print(f"     Ruta: {archivo_path.relative_to(base_dir)}")
                        print(f"     Tamaño: {info.get('file_size', 0)} bytes")
                        for error in info.get('errors', []):
                            print(f"     ❌ Error: {error}")
            
            # Mostrar advertencias
            if resultados['archivos_con_warnings'] > 0:
                print("\n⚠️  ARCHIVOS CON ADVERTENCIAS:")
                for archivo, info in resultados['resultados'].items():
                    if info.get('warnings'):
                        archivo_path = Path(archivo)
                        print(f"\n  📄 {archivo_path.name}")
                        for warning in info.get('warnings', []):
                            print(f"     ⚠️  Advertencia: {warning}")
            
            # Mostrar información de archivos válidos
            if resultados['archivos_validos'] > 0:
                print("\n✅ ARCHIVOS VÁLIDOS:")
                for archivo, info in resultados['resultados'].items():
                    if info.get('is_valid_pdf', False):
                        archivo_path = Path(archivo)
                        page_count = info.get('page_count', 0)
                        file_size = info.get('file_size', 0)
                        has_text = info.get('has_text', False)
                        
                        print(f"  📄 {archivo_path.name}")
                        print(f"     Páginas: {page_count} | Tamaño: {file_size:,} bytes | Texto: {'Sí' if has_text else 'No'}")
    
    # Resumen general
    print("\n" + "=" * 70)
    print("RESUMEN GENERAL")
    print("=" * 70)
    total_archivos = sum(r['total_archivos'] for r in todos_los_resultados.values())
    total_validos = sum(r['archivos_validos'] for r in todos_los_resultados.values())
    total_invalidos = sum(r['archivos_invalidos'] for r in todos_los_resultados.values())
    total_warnings = sum(r['archivos_con_warnings'] for r in todos_los_resultados.values())
    
    print(f"Total de PDFs en el proyecto: {total_archivos}")
    print(f"✅ Válidos: {total_validos}")
    print(f"❌ Inválidos: {total_invalidos}")
    print(f"⚠️  Con advertencias: {total_warnings}")
    
    if total_invalidos > 0:
        print(f"\n❌ Se encontraron {total_invalidos} archivo(s) PDF inválido(s).")
        print("   Revise los detalles arriba para más información.")
        return 1
    elif total_warnings > 0:
        print(f"\n⚠️  Todos los PDFs son válidos, pero {total_warnings} tienen advertencias.")
        return 0
    else:
        print("\n✅ Todos los PDFs son válidos y no tienen problemas.")
        return 0


if __name__ == '__main__':
    sys.exit(main())

