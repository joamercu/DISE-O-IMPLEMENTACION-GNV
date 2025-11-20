"""
Script para probar la apertura del diagrama en draw.io
Intenta abrir el archivo y verificar que sea válido
"""
import subprocess
import sys
import os
from pathlib import Path
import platform
import webbrowser
import urllib.parse

def test_abrir_en_navegador(archivo):
    """Intenta abrir el archivo en draw.io online"""
    print("\n🌐 Probando apertura en draw.io online...")
    
    archivo_path = Path(archivo).resolve()
    
    if not archivo_path.exists():
        print(f"❌ El archivo no existe: {archivo_path}")
        return False
    
    # Leer el contenido del archivo
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar que el contenido sea válido
        if len(contenido) == 0:
            print("❌ El archivo está vacío")
            return False
        
        if '<mxfile' not in contenido:
            print("❌ El archivo no contiene el elemento mxfile")
            return False
        
        if '<diagram' not in contenido:
            print("❌ El archivo no contiene ningún diagrama")
            return False
        
        print(f"✅ Archivo válido: {len(contenido)} caracteres")
        
        # Intentar abrir en draw.io online
        print("\n📋 Para abrir el archivo en draw.io online:")
        print("   1. Ve a: https://app.diagrams.net/")
        print("   2. Selecciona: Archivo > Abrir desde > Dispositivo")
        print(f"   3. Selecciona: {archivo_path}")
        
        # Codificar el contenido en base64 para URL
        import base64
        contenido_b64 = base64.b64encode(contenido.encode('utf-8')).decode('utf-8')
        
        # Crear URL de draw.io con el contenido
        url = f"https://app.diagrams.net/?mode=file#U{urllib.parse.quote(contenido_b64)}"
        
        print(f"\n🔗 URL directa (con contenido):")
        print(f"   {url[:100]}...")
        
        respuesta = input("\n¿Deseas abrir el archivo en draw.io online ahora? (s/n): ").strip().lower()
        if respuesta == 's':
            webbrowser.open(url)
            print("✅ Abriendo en navegador...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return False

def test_abrir_con_drawio_desktop(archivo):
    """Intenta abrir el archivo con draw.io desktop si está instalado"""
    print("\n🖥️  Probando apertura con draw.io desktop...")
    
    sistema = platform.system()
    posibles_rutas = []
    
    if sistema == "Windows":
        posibles_rutas = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "draw.io", "draw.io.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "draw.io", "draw.io.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "draw.io", "draw.io.exe"),
            r"C:\Program Files\draw.io\draw.io.exe",
            r"C:\Program Files (x86)\draw.io\draw.io.exe",
        ]
    elif sistema == "Darwin":  # macOS
        posibles_rutas = [
            "/Applications/draw.io.app/Contents/MacOS/draw.io",
            os.path.expanduser("~/Applications/draw.io.app/Contents/MacOS/draw.io"),
        ]
    else:  # Linux
        posibles_rutas = [
            "/usr/bin/drawio",
            "/usr/local/bin/drawio",
            os.path.expanduser("~/bin/drawio"),
        ]
    
    drawio_exe = None
    for ruta in posibles_rutas:
        if ruta and os.path.exists(ruta):
            drawio_exe = ruta
            break
    
    if drawio_exe:
        print(f"✅ Draw.io Desktop encontrado: {drawio_exe}")
        archivo_path = Path(archivo).resolve()
        
        respuesta = input(f"\n¿Deseas abrir el archivo con draw.io desktop? (s/n): ").strip().lower()
        if respuesta == 's':
            try:
                subprocess.Popen([drawio_exe, str(archivo_path)])
                print("✅ Abriendo con draw.io desktop...")
                return True
            except Exception as e:
                print(f"❌ Error al abrir: {e}")
                return False
    else:
        print("⚠️ Draw.io Desktop no encontrado")
        print("   Puedes descargarlo desde: https://github.com/jgraph/drawio-desktop/releases")
        return False

def main():
    """Función principal"""
    print("=" * 70)
    print("TEST DE APERTURA DE DIAGRAMA DRAW.IO")
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
        print(f"\nUso: python test_abrir_diagrama.py [archivo.xml]")
        sys.exit(1)
    
    print(f"\n📄 Archivo: {archivo_path}")
    print("=" * 70)
    
    # Test 1: Abrir en navegador
    test_abrir_en_navegador(archivo)
    
    # Test 2: Abrir con desktop
    test_abrir_con_drawio_desktop(archivo)
    
    print("\n" + "=" * 70)
    print("✅ Test completado")
    print("=" * 70)

if __name__ == "__main__":
    main()

