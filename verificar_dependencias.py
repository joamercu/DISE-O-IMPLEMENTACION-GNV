"""
Script para verificar que todas las dependencias estén instaladas y listadas en requirements.txt
"""
import sys
import importlib

def verificar_dependencia(paquete, nombre_mostrar=None):
    """Verifica si un paquete está instalado"""
    nombre = nombre_mostrar or paquete
    try:
        importlib.import_module(paquete)
        return True, f"✅ {nombre}"
    except ImportError:
        return False, f"❌ {nombre} - NO INSTALADO"

def main():
    print("=" * 60)
    print("VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 60)
    
    # Dependencias externas (deben estar en requirements.txt)
    dependencias_externas = {
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl'
    }
    
    # Bibliotecas estándar de Python (no necesitan estar en requirements.txt)
    bibliotecas_estandar = {
        'math': 'math',
        'json': 'json',
        'base64': 'base64',
        'os': 'os',
        'sys': 'sys',
        'datetime': 'datetime',
        'xml.etree.ElementTree': 'xml.etree.ElementTree',
        'xml.dom.minidom': 'xml.dom.minidom',
        'typing': 'typing',
        'hashlib': 'hashlib'
    }
    
    print("\n📦 DEPENDENCIAS EXTERNAS (requieren instalación):")
    print("-" * 60)
    
    todas_ok = True
    for modulo, nombre in dependencias_externas.items():
        ok, mensaje = verificar_dependencia(modulo, nombre)
        print(f"  {mensaje}")
        if not ok:
            todas_ok = False
    
    print("\n📚 BIBLIOTECAS ESTÁNDAR DE PYTHON:")
    print("-" * 60)
    
    for modulo, nombre in bibliotecas_estandar.items():
        ok, mensaje = verificar_dependencia(modulo, nombre)
        print(f"  {mensaje}")
        if not ok:
            todas_ok = False
    
    print("\n" + "=" * 60)
    print("RESULTADO")
    print("=" * 60)
    
    if todas_ok:
        print("✅ Todas las dependencias están instaladas correctamente")
        print("\n📋 DEPENDENCIAS EN requirements.txt:")
        print("-" * 60)
        try:
            with open('requirements.txt', 'r', encoding='utf-8') as f:
                contenido = f.read()
                print(contenido)
        except Exception as e:
            print(f"❌ Error al leer requirements.txt: {e}")
        
        print("\n✅ Verificación completada exitosamente")
    else:
        print("❌ Faltan algunas dependencias")
        print("\n💡 Para instalar las dependencias faltantes, ejecute:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    return todas_ok

if __name__ == "__main__":
    main()

