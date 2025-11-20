"""
Script para generar PDF directamente desde diagrama Draw.io
Intenta múltiples métodos automáticamente hasta encontrar uno que funcione
"""
import os
import sys
import subprocess
import time
from pathlib import Path
import platform

def encontrar_drawio_desktop():
    """Busca Draw.io Desktop en ubicaciones comunes"""
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
    
    for ruta in posibles_rutas:
        if ruta and os.path.exists(ruta):
            return ruta
    return None

def generar_pdf_diagrama(xml_file, output_pdf=None):
    """
    Genera PDF desde archivo Draw.io XML
    
    Args:
        xml_file: Ruta al archivo XML
        output_pdf: Ruta de salida del PDF (opcional)
    
    Returns:
        Ruta del PDF generado o None si falla
    """
    xml_path = Path(xml_file).resolve()
    
    if not xml_path.exists():
        raise FileNotFoundError(f"El archivo no existe: {xml_file}")
    
    if output_pdf is None:
        output_pdf = xml_path.with_suffix('.pdf')
    else:
        output_pdf = Path(output_pdf)
    
    # Mostrar ubicación completa del PDF
    pdf_ruta_completa = output_pdf.resolve()
    
    print("=" * 70)
    print("GENERADOR DE PDF DESDE DIAGRAMA DRAW.IO")
    print("=" * 70)
    print(f"📄 Archivo origen: {xml_path}")
    print(f"📄 Archivo destino: {pdf_ruta_completa}")
    print(f"📂 Carpeta: {pdf_ruta_completa.parent}")
    print("-" * 70)
    
    # Método 1: Draw.io CLI (npm package)
    print("\n[1/4] Intentando Draw.io CLI (npm)...")
    try:
        result = subprocess.run(
            ['drawio', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("   ✓ Draw.io CLI encontrado")
            print("   🔄 Exportando a PDF...")
            cmd = [
                'drawio',
                '--export',
                '--format', 'pdf',
                '--output', str(output_pdf),
                '--border', '10',
                '--transparent', 'false',
                str(xml_path)
            ]
            subprocess.run(cmd, check=True, timeout=30)
            if output_pdf.exists():
                print(f"   ✅ PDF generado exitosamente: {output_pdf}")
                return str(output_pdf)
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"   ⚠️ No disponible: {type(e).__name__}")
    
    # Método 2: Draw.io Desktop
    print("\n[2/4] Intentando Draw.io Desktop...")
    drawio_exe = encontrar_drawio_desktop()
    if drawio_exe:
        print(f"   ✓ Draw.io Desktop encontrado: {drawio_exe}")
        print("   🔄 Exportando a PDF...")
        try:
            # Draw.io Desktop puede exportar desde línea de comandos
            cmd = [
                drawio_exe,
                '--export',
                '--format', 'pdf',
                '--output', str(output_pdf),
                '--border', '10',
                str(xml_path)
            ]
            subprocess.run(cmd, check=True, timeout=30)
            if output_pdf.exists():
                print(f"   ✅ PDF generado exitosamente: {output_pdf}")
                return str(output_pdf)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            print(f"   ⚠️ Error al exportar: {type(e).__name__}")
            # Intentar método alternativo: abrir y esperar exportación manual
            print("   💡 Abriendo Draw.io Desktop para exportación manual...")
            try:
                subprocess.Popen([drawio_exe, str(xml_path)])
                print("   📋 INSTRUCCIONES:")
                print("      1. En Draw.io Desktop, presiona Ctrl+Shift+E")
                print(f"      2. Guarda como: {output_pdf.name}")
                print(f"      3. Ubicación: {output_pdf.parent}")
                return None
            except Exception as e2:
                print(f"   ❌ Error: {e2}")
    else:
        print("   ⚠️ Draw.io Desktop no encontrado")
    
    # Método 3: Usar Python con librerías de renderizado (si están disponibles)
    print("\n[3/4] Intentando conversión con Python...")
    try:
        # Intentar usar reportlab o similar para renderizar SVG/XML
        # Esto requiere convertir primero a SVG, lo cual es complejo
        print("   ⚠️ Conversión directa no disponible sin librerías adicionales")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # Método 4: Instrucciones para instalación
    print("\n[4/4] Métodos alternativos:")
    print("=" * 70)
    print(f"\n📍 UBICACIÓN DONDE SE GUARDARÁ EL PDF:")
    print(f"   {pdf_ruta_completa}")
    print("=" * 70)
    print("\n📖 OPCIONES PARA GENERAR EL PDF:")
    print("\n1. INSTALAR DRAW.IO CLI (Recomendado):")
    print("   npm install -g @drawio/cli")
    print("   Luego ejecuta este script nuevamente")
    print("\n2. USAR DRAW.IO DESKTOP:")
    print("   Descarga desde: https://github.com/jgraph/drawio-desktop/releases")
    print("   Instala y ejecuta este script nuevamente")
    print("\n3. EXPORTACIÓN MANUAL:")
    print(f"   a) Abre: {xml_path}")
    print("   b) En Draw.io online (https://app.diagrams.net):")
    print("      - Archivo > Abrir desde > Dispositivo")
    print("      - Selecciona el archivo XML")
    print("      - Archivo > Exportar como > PDF")
    print(f"      - Guarda en: {pdf_ruta_completa.parent}")
    print(f"      - Nombre: {output_pdf.name}")
    print("\n4. USAR DRAW.IO DESKTOP (si está instalado):")
    print(f"   a) Abre: {xml_path} con Draw.io Desktop")
    print("   b) Presiona: Ctrl+Shift+E")
    print(f"   c) Guarda en: {pdf_ruta_completa.parent}")
    print(f"   d) Nombre: {output_pdf.name}")
    print("=" * 70)
    
    # Abrir la carpeta de destino
    print(f"\n📂 Abriendo carpeta de destino...")
    try:
        if platform.system() == "Windows":
            os.startfile(str(pdf_ruta_completa.parent))
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(pdf_ruta_completa.parent)])
        else:
            subprocess.run(["xdg-open", str(pdf_ruta_completa.parent)])
    except Exception as e:
        print(f"   ⚠️ No se pudo abrir la carpeta: {e}")
    
    return None

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("GENERADOR DE PDF DESDE DIAGRAMA DRAW.IO")
        print("=" * 70)
        print("\nUso:")
        print("  python generar_pdf_diagrama.py <archivo.xml> [archivo_salida.pdf]")
        print("\nEjemplos:")
        print("  python generar_pdf_diagrama.py diagrama.drawio.xml")
        print("  python generar_pdf_diagrama.py diagrama.drawio.xml salida.pdf")
        print("\nArchivo por defecto:")
        default_file = r"c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19.drawio.xml"
        if os.path.exists(default_file):
            print(f"  python generar_pdf_diagrama.py \"{default_file}\"")
        print("=" * 70)
        sys.exit(1)
    
    xml_file = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        resultado = generar_pdf_diagrama(xml_file, output_pdf)
        if resultado:
            print("\n" + "=" * 70)
            print("✅ ¡ÉXITO! PDF generado correctamente")
            print("=" * 70)
            print(f"📄 Archivo: {resultado}")
            print(f"📂 Ubicación: {Path(resultado).parent}")
            print("\n¿Deseas abrir el archivo? (s/n): ", end="")
            try:
                respuesta = input().strip().lower()
                if respuesta == 's':
                    if platform.system() == "Windows":
                        os.startfile(resultado)
                    elif platform.system() == "Darwin":
                        subprocess.run(["open", resultado])
                    else:
                        subprocess.run(["xdg-open", resultado])
            except:
                pass
        else:
            print("\n⚠️ No se pudo generar el PDF automáticamente.")
            print("   Revisa las opciones mostradas arriba.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

