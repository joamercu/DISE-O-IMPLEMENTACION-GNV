"""
Script para convertir archivos draw.io XML a PDF
"""
import os
import sys
import subprocess
from pathlib import Path

def convertir_drawio_a_pdf(xml_file, output_pdf=None):
    """
    Convierte un archivo draw.io XML a PDF
    
    Args:
        xml_file: Ruta al archivo XML de draw.io
        output_pdf: Ruta de salida del PDF (opcional)
    
    Returns:
        Ruta del archivo PDF generado
    """
    xml_path = Path(xml_file)
    
    if not xml_path.exists():
        raise FileNotFoundError(f"El archivo {xml_file} no existe")
    
    # Determinar nombre del archivo de salida
    if output_pdf is None:
        output_pdf = xml_path.with_suffix('.pdf')
    else:
        output_pdf = Path(output_pdf)
    
    print(f"Convirtiendo {xml_path.name} a PDF...")
    
    # Método 1: Intentar usar draw.io CLI si está disponible
    try:
        # Verificar si drawio está instalado
        result = subprocess.run(['drawio', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✓ Usando draw.io CLI...")
            cmd = [
                'drawio',
                '--export',
                '--format', 'pdf',
                '--output', str(output_pdf),
                str(xml_path)
            ]
            subprocess.run(cmd, check=True)
            print(f"✓ PDF generado exitosamente: {output_pdf}")
            return str(output_pdf)
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Método 2: Usar la API web de draw.io (requiere conexión a internet)
    try:
        print("Intentando usar la API web de draw.io...")
        import urllib.request
        import urllib.parse
        import base64
        
        # Leer el contenido del XML
        with open(xml_path, 'rb') as f:
            xml_content = f.read()
        
        # Codificar en base64
        xml_b64 = base64.b64encode(xml_content).decode('utf-8')
        
        # URL de la API de exportación de draw.io
        # Nota: Esta es una aproximación, la API real puede variar
        print("⚠️ La conversión mediante API web requiere configuración adicional.")
        print("   Por favor, use una de las siguientes opciones:")
        print("   1. Instalar draw.io desktop: https://github.com/jgraph/drawio-desktop/releases")
        print("   2. Abrir el archivo en https://app.diagrams.net y exportar manualmente a PDF")
        print("   3. Usar la herramienta de línea de comandos drawio")
        
        raise Exception("No se pudo convertir automáticamente. Use las opciones sugeridas.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python convertir_drawio_a_pdf.py <archivo.xml> [archivo_salida.pdf]")
        print("\nEjemplo:")
        print("  python convertir_drawio_a_pdf.py diagrama.drawio.xml")
        print("  python convertir_drawio_a_pdf.py diagrama.drawio.xml salida.pdf")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        pdf_path = convertir_drawio_a_pdf(xml_file, output_pdf)
        print(f"\n✅ Conversión completada: {pdf_path}")
    except Exception as e:
        print(f"\n❌ Error durante la conversión: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

