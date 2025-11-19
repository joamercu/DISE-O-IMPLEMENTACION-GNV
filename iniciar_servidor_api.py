"""
Script para iniciar el servidor API
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Establecer PYTHONPATH
os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Iniciando servidor API de Datos de Salida")
    print("=" * 60)
    print("\nEl servidor estará disponible en:")
    print("  - http://localhost:8000")
    print("  - http://localhost:8000/docs (Documentación interactiva)")
    print("  - http://localhost:8000/datos-salida (Endpoint principal)")
    print("\nPresione Ctrl+C para detener el servidor\n")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "src.api_endpoint:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")
        import traceback
        traceback.print_exc()

