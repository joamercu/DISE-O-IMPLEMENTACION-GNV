"""
Script mejorado para exportar diagramas Draw.io a PDF
Soporta múltiples métodos de conversión
"""
import os
import sys
import subprocess
import webbrowser
import tempfile
from pathlib import Path
import urllib.parse

def exportar_drawio_a_pdf(xml_file, output_pdf=None, metodo='auto'):
    """
    Exporta un archivo draw.io XML a PDF usando diferentes métodos
    
    Args:
        xml_file: Ruta al archivo XML de draw.io
        output_pdf: Ruta de salida del PDF (opcional)
        metodo: 'auto', 'cli', 'navegador', 'manual'
    
    Returns:
        Ruta del archivo PDF generado o instrucciones
    """
    xml_path = Path(xml_file).resolve()
    
    if not xml_path.exists():
        raise FileNotFoundError(f"El archivo {xml_file} no existe")
    
    # Determinar nombre del archivo de salida
    if output_pdf is None:
        output_pdf = xml_path.with_suffix('.pdf')
    else:
        output_pdf = Path(output_pdf)
    
    print(f"📄 Archivo: {xml_path.name}")
    print(f"📄 Salida: {output_pdf.name}")
    print("-" * 60)
    
    # Método 1: Draw.io CLI (si está instalado)
    if metodo in ['auto', 'cli']:
        try:
            print("🔍 Verificando draw.io CLI...")
            result = subprocess.run(
                ['drawio', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                print("✓ Draw.io CLI encontrado")
                print("🔄 Exportando a PDF...")
                cmd = [
                    'drawio',
                    '--export',
                    '--format', 'pdf',
                    '--output', str(output_pdf),
                    '--border', '10',
                    str(xml_path)
                ]
                subprocess.run(cmd, check=True)
                print(f"✅ PDF generado exitosamente: {output_pdf}")
                return str(output_pdf)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️ Draw.io CLI no está instalado")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al usar CLI: {e}")
            if metodo == 'cli':
                raise
    
    # Método 2: Abrir en navegador con Draw.io online
    if metodo in ['auto', 'navegador']:
        try:
            print("\n🌐 Abriendo en Draw.io online...")
            # Codificar el archivo para pasar como parámetro
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Crear URL para Draw.io con el archivo
            # Draw.io puede abrir archivos desde URL o desde el sistema de archivos
            url = f"https://app.diagrams.net/?mode=file"
            
            print(f"📂 Ruta del archivo: {xml_path}")
            print("\n📋 INSTRUCCIONES:")
            print("   1. El navegador se abrirá con Draw.io")
            print("   2. Ve a: Archivo > Abrir desde > Dispositivo")
            print(f"   3. Selecciona: {xml_path}")
            print("   4. Una vez abierto, ve a: Archivo > Exportar como > PDF")
            print(f"   5. Guarda como: {output_pdf.name}")
            print("\n⏳ Abriendo navegador en 3 segundos...")
            
            import time
            time.sleep(3)
            webbrowser.open(url)
            
            print("\n✅ Navegador abierto. Sigue las instrucciones arriba.")
            return None
            
        except Exception as e:
            print(f"⚠️ Error al abrir navegador: {e}")
            if metodo == 'navegador':
                raise
    
    # Método 3: Instrucciones manuales
    if metodo in ['auto', 'manual']:
        print("\n" + "=" * 60)
        print("📖 INSTRUCCIONES MANUALES PARA EXPORTAR A PDF")
        print("=" * 60)
        print(f"\n1. Abre el archivo en Draw.io:")
        print(f"   {xml_path}")
        print("\n2. Opciones para abrir:")
        print("   a) Abre https://app.diagrams.net en tu navegador")
        print("   b) Ve a: Archivo > Abrir desde > Dispositivo")
        print(f"   c) Selecciona: {xml_path}")
        print("\n3. Para exportar a PDF:")
        print("   a) Ve a: Archivo > Exportar como > PDF")
        print("   b) O usa: Ctrl+Shift+E (Windows) / Cmd+Shift+E (Mac)")
        print(f"   c) Guarda como: {output_pdf.name}")
        print("\n4. Alternativa - Draw.io Desktop:")
        print("   a) Descarga desde: https://github.com/jgraph/drawio-desktop/releases")
        print("   b) Instala la aplicación")
        print("   c) Abre el archivo .xml con Draw.io")
        print("   d) Exporta a PDF desde el menú")
        print("\n5. Alternativa - Línea de comandos:")
        print("   a) Instala draw.io CLI: npm install -g @drawio/cli")
        print(f"   b) Ejecuta: drawio --export --format pdf --output {output_pdf} {xml_path}")
        print("=" * 60)
        return None
    
    return None

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("EXPORTADOR DE DIAGRAMAS DRAW.IO A PDF")
        print("=" * 60)
        print("\nUso:")
        print("  python exportar_diagrama_pdf.py <archivo.xml> [archivo_salida.pdf] [metodo]")
        print("\nMétodos disponibles:")
        print("  auto     - Intenta CLI, luego navegador, luego manual (por defecto)")
        print("  cli      - Solo intenta usar draw.io CLI")
        print("  navegador - Abre en navegador con instrucciones")
        print("  manual   - Solo muestra instrucciones")
        print("\nEjemplos:")
        print("  python exportar_diagrama_pdf.py diagrama.drawio.xml")
        print("  python exportar_diagrama_pdf.py diagrama.drawio.xml salida.pdf")
        print("  python exportar_diagrama_pdf.py diagrama.drawio.xml salida.pdf navegador")
        print("=" * 60)
        sys.exit(1)
    
    xml_file = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    metodo = sys.argv[3] if len(sys.argv) > 3 else 'auto'
    
    try:
        resultado = exportar_drawio_a_pdf(xml_file, output_pdf, metodo)
        if resultado:
            print(f"\n✅ ¡Éxito! PDF generado en: {resultado}")
        else:
            print("\n💡 Sigue las instrucciones mostradas arriba para completar la exportación.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

