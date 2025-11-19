"""
Ejemplo de uso de la API de Datos de Salida
"""

import requests
import json
from datetime import datetime

# URL base de la API
BASE_URL = "http://localhost:8000"

def ejemplo_obtener_datos_completos():
    """Ejemplo: Obtener todos los datos de salida"""
    print("=" * 60)
    print("Ejemplo 1: Obtener todos los datos de salida")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/datos-salida")
        response.raise_for_status()
        
        datos = response.json()
        
        print(f"\n✅ Datos obtenidos exitosamente")
        print(f"Timestamp: {datos['timestamp']}")
        print(f"Cliente: {datos['cliente']}")
        print(f"Carpeta destino: {datos['carpeta_destino']}")
        print(f"Archivos procesados: {datos['archivos_procesados']}")
        print(f"\nResumen por categoría:")
        resumen = datos['datos']['resumen']['archivos_por_categoria']
        for categoria, cantidad in resumen.items():
            print(f"  - {categoria}: {cantidad} archivos")
        
        return datos
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor API.")
        print("   Asegúrate de que el servidor esté ejecutándose:")
        print("   python -m uvicorn src.api_endpoint:app --reload --host 0.0.0.0 --port 8000")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def ejemplo_obtener_resumen():
    """Ejemplo: Obtener resumen de datos (sin contenido de archivos)"""
    print("\n" + "=" * 60)
    print("Ejemplo 2: Obtener resumen de datos")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/datos-salida/resumen")
        response.raise_for_status()
        
        resumen = response.json()
        
        print(f"\n✅ Resumen obtenido exitosamente")
        print(f"Timestamp: {resumen['timestamp']}")
        print(f"Total de archivos: {resumen['resumen']['total_archivos']}")
        print(f"\nArchivos por categoría:")
        for categoria, cantidad in resumen['resumen']['archivos_por_categoria'].items():
            print(f"  - {categoria}: {cantidad} archivos")
        
        print(f"\nAlgunos archivos de outputs:")
        for archivo in resumen['archivos']['outputs'][:3]:
            tamaño_kb = archivo['tamaño_bytes'] / 1024
            print(f"  - {archivo['nombre']} ({tamaño_kb:.2f} KB)")
        
        return resumen
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def ejemplo_crear_carpeta():
    """Ejemplo: Crear carpeta con todos los archivos"""
    print("\n" + "=" * 60)
    print("Ejemplo 3: Crear carpeta 'cliente 1 - petroliquidos'")
    print("=" * 60)
    
    try:
        response = requests.post(f"{BASE_URL}/datos-salida/crear-carpeta")
        response.raise_for_status()
        
        resultado = response.json()
        
        print(f"\n✅ Carpeta creada exitosamente")
        print(f"Carpeta: {resultado['carpeta']}")
        print(f"Ruta completa: {resultado['ruta_completa']}")
        print(f"Archivos copiados: {resultado['archivos_copiados']}")
        print(f"\nEstructura:")
        for categoria, cantidad in resultado['estructura'].items():
            print(f"  - {categoria}/: {cantidad} archivos")
        
        return resultado
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def ejemplo_guardar_datos_json():
    """Ejemplo: Guardar los datos obtenidos en un archivo JSON"""
    print("\n" + "=" * 60)
    print("Ejemplo 4: Guardar datos en archivo JSON")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/datos-salida")
        response.raise_for_status()
        
        datos = response.json()
        
        # Crear nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"datos_salida_export_{timestamp}.json"
        
        # Guardar sin el contenido base64 para reducir tamaño
        datos_ligeros = {
            'timestamp': datos['timestamp'],
            'cliente': datos['cliente'],
            'carpeta_destino': datos['carpeta_destino'],
            'archivos_procesados': datos['archivos_procesados'],
            'resumen': datos['datos']['resumen'],
            'archivos': {
                'outputs': [
                    {
                        'nombre': a['nombre'],
                        'tamaño_bytes': a['tamaño_bytes'],
                        'fecha_modificacion': a['fecha_modificacion'],
                        'tipo_mime': a['tipo_mime']
                    }
                    for a in datos['datos']['outputs'].get('archivos', [])
                ],
                'data': [
                    {
                        'nombre': a['nombre'],
                        'tamaño_bytes': a['tamaño_bytes'],
                        'fecha_modificacion': a['fecha_modificacion'],
                        'tipo_mime': a['tipo_mime']
                    }
                    for a in datos['datos']['data'].get('archivos', [])
                ],
                'docs': [
                    {
                        'nombre': a['nombre'],
                        'tamaño_bytes': a['tamaño_bytes'],
                        'fecha_modificacion': a['fecha_modificacion'],
                        'tipo_mime': a['tipo_mime']
                    }
                    for a in datos['datos']['docs'].get('archivos', [])
                ],
                'assets': [
                    {
                        'nombre': a['nombre'],
                        'tamaño_bytes': a['tamaño_bytes'],
                        'fecha_modificacion': a['fecha_modificacion'],
                        'tipo_mime': a['tipo_mime']
                    }
                    for a in datos['datos']['assets'].get('archivos', [])
                ]
            },
            'manifest': datos['datos'].get('manifest')
        }
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos_ligeros, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Datos guardados en: {nombre_archivo}")
        return nombre_archivo
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("EJEMPLOS DE USO - API DE DATOS DE SALIDA")
    print("=" * 60)
    print("\nAsegúrate de que el servidor API esté ejecutándose:")
    print("  scripts\\iniciar_api.bat")
    print("  o")
    print("  python -m uvicorn src.api_endpoint:app --reload --host 0.0.0.0 --port 8000")
    print("\n" + "=" * 60)
    
    # Ejecutar ejemplos
    ejemplo_obtener_datos_completos()
    ejemplo_obtener_resumen()
    ejemplo_crear_carpeta()
    ejemplo_guardar_datos_json()
    
    print("\n" + "=" * 60)
    print("Ejemplos completados")
    print("=" * 60)

