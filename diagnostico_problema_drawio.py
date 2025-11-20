"""
Script de diagnóstico para identificar el problema específico con draw.io
Compara archivos y verifica diferencias
"""
import sys
from pathlib import Path
import hashlib
import xml.etree.ElementTree as ET

def calcular_hash(archivo):
    """Calcula el hash MD5 de un archivo"""
    hash_md5 = hashlib.md5()
    with open(archivo, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def comparar_archivos(archivo1, archivo2):
    """Compara dos archivos XML de draw.io"""
    print("=" * 70)
    print("DIAGNÓSTICO DE COMPATIBILIDAD DRAW.IO")
    print("=" * 70)
    
    arch1 = Path(archivo1)
    arch2 = Path(archivo2)
    
    if not arch1.exists():
        print(f"❌ Archivo 1 no existe: {archivo1}")
        return
    
    if not arch2.exists():
        print(f"❌ Archivo 2 no existe: {archivo2}")
        return
    
    print(f"\n📄 Archivo 1: {arch1.name}")
    print(f"   Tamaño: {arch1.stat().st_size} bytes")
    print(f"   Hash MD5: {calcular_hash(arch1)}")
    
    print(f"\n📄 Archivo 2: {arch2.name}")
    print(f"   Tamaño: {arch2.stat().st_size} bytes")
    print(f"   Hash MD5: {calcular_hash(arch2)}")
    
    # Comparar hashes
    hash1 = calcular_hash(arch1)
    hash2 = calcular_hash(arch2)
    
    if hash1 == hash2:
        print("\n✅ Los archivos son idénticos (mismo hash)")
    else:
        print("\n⚠️ Los archivos son diferentes")
        
        # Comparar estructura XML
        print("\n🔍 Comparando estructura XML...")
        try:
            tree1 = ET.parse(arch1)
            root1 = tree1.getroot()
            print(f"✅ Archivo 1: XML válido")
            
            cells1 = root1.findall('.//mxCell')
            print(f"   - Elementos mxCell: {len(cells1)}")
            
        except Exception as e:
            print(f"❌ Archivo 1: Error al parsear XML: {e}")
        
        try:
            tree2 = ET.parse(arch2)
            root2 = tree2.getroot()
            print(f"✅ Archivo 2: XML válido")
            
            cells2 = root2.findall('.//mxCell')
            print(f"   - Elementos mxCell: {len(cells2)}")
            
        except Exception as e:
            print(f"❌ Archivo 2: Error al parsear XML: {e}")
    
    # Verificar si el archivo original se puede abrir
    print("\n" + "=" * 70)
    print("RECOMENDACIONES:")
    print("=" * 70)
    print("\n1. Si el archivo ORIGINAL se abre correctamente:")
    print("   → El problema puede ser con caracteres especiales o codificación")
    print("   → Intenta usar el archivo original directamente")
    
    print("\n2. Si NINGÚN archivo se abre:")
    print("   → Puede ser un problema del navegador o de la plataforma")
    print("   → Prueba en modo incógnito")
    print("   → Limpia la caché del navegador")
    print("   → Prueba con otro navegador")
    
    print("\n3. Si aparece un error específico:")
    print("   → Anota el mensaje de error exacto")
    print("   → Verifica la consola del navegador (F12)")
    
    print("\n4. Alternativas:")
    print("   → Usa draw.io Desktop en lugar de la versión web")
    print("   → Descarga desde: https://github.com/jgraph/drawio-desktop/releases")
    
    print("\n" + "=" * 70)

def main():
    archivo_original = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19.drawio.xml"
    archivo_fixed = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19_FIXED.drawio.xml"
    
    if len(sys.argv) > 1:
        archivo_fixed = sys.argv[1]
    
    comparar_archivos(archivo_original, archivo_fixed)

if __name__ == "__main__":
    main()

