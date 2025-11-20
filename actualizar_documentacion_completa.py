"""
Script para actualizar toda la documentación con los cambios del ingeniero
"""
import os
import re
from pathlib import Path

# Cambios a realizar
CAMBIOS = {
    # Tanques
    r'24\s*tanques': '18 tanques',
    r'24\s*unidades': '18 unidades',
    r'Número de tanques:\s*24': 'Número de tanques: 18',
    r'(\d+)\s*tanques más.*Total:\s*24': r'\1 tanques más)\nTotal: 18',
    r'Total:\s*24\s*tanques': 'Total: 18 tanques',
    
    # Autonomía
    r'Autonomía objetivo:\s*800\s*km': 'Autonomía objetivo: 600 km',
    r'Autonomía deseada:\s*800\.0\s*km': 'Autonomía deseada: 600.0 km',
    r'Autonomía:\s*800\s*km': 'Autonomía: 600 km',
    r'Autonomía:\s*600-800\s*km': 'Autonomía: 600 km',
    
    # Información de empresa
    r'CLIENTE\s*:\s*PETROLIQUIDOS': 'CLIENTE: PETROLIQUIDOS
DESARROLLO: WELDTECH SOLUTION
VERSION: PROPUESTA TECNICA
REVISION: 0 (PROPUESTA PREELIMINAR)\nDESARROLLO: WELDTECH SOLUTION\nVERSION: PROPUESTA TECNICA\nREVISION: 0 (PROPUESTA PREELIMINAR)',
}

def actualizar_archivo(archivo_path: Path):
    """Actualiza un archivo con los cambios"""
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        contenido_original = contenido
        
        # Aplicar cambios
        for patron, reemplazo in CAMBIOS.items():
            contenido = re.sub(patron, reemplazo, contenido, flags=re.IGNORECASE)
        
        # Solo escribir si hubo cambios
        if contenido != contenido_original:
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
            return True
        return False
    except Exception as e:
        print(f"   ⚠️ Error procesando {archivo_path.name}: {e}")
        return False

def main():
    print("="*80)
    print("ACTUALIZACIÓN COMPLETA DE DOCUMENTACIÓN")
    print("="*80)
    print()
    
    # Directorios a procesar
    directorios = [
        Path('docs'),
        Path('.'),
    ]
    
    # Extensiones a procesar
    extensiones = ['.md', '.txt', '.py', '.json']
    
    archivos_actualizados = 0
    archivos_procesados = 0
    
    for directorio in directorios:
        if not directorio.exists():
            continue
        
        print(f"📁 Procesando directorio: {directorio}")
        
        for archivo_path in directorio.rglob('*'):
            if archivo_path.is_file() and archivo_path.suffix in extensiones:
                # Excluir algunos archivos
                if 'backup' in archivo_path.name.lower() or 'old' in archivo_path.name.lower():
                    continue
                
                archivos_procesados += 1
                if actualizar_archivo(archivo_path):
                    archivos_actualizados += 1
                    print(f"   ✅ Actualizado: {archivo_path.name}")
    
    print()
    print("="*80)
    print("RESUMEN")
    print("="*80)
    print(f"📄 Archivos procesados: {archivos_procesados}")
    print(f"✅ Archivos actualizados: {archivos_actualizados}")
    print()
    print("Cambios aplicados:")
    print("  • 18 tanques → 18 tanques")
    print("  • Autonomía 800 km → 600 km")
    print("  • Información de empresa agregada")
    print("="*80)

if __name__ == '__main__':
    main()

