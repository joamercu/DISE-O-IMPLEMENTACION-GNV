"""
Script para crear nuevos usuarios en el sistema
"""
import sys
import os

# Agregar el directorio src al path para importar auth_system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auth_system import create_user

def main():
    """Crea los usuarios solicitados"""
    
    # Usuario administrador: gabriel.ortiz
    print("Creando usuario administrador: gabriel.ortiz...")
    if create_user('gabriel.ortiz', 'gabriel123', 'Administrador'):
        print("✓ Usuario administrador 'gabriel.ortiz' creado exitosamente")
    else:
        print("✗ Error: El usuario 'gabriel.ortiz' ya existe")
    
    # Usuario cliente: juan.solano
    print("\nCreando usuario cliente: juan.solano...")
    if create_user('juan.solano', 'petroliquidos123', 'Cliente'):
        print("✓ Usuario cliente 'juan.solano' creado exitosamente")
    else:
        print("✗ Error: El usuario 'juan.solano' ya existe")
    
    print("\n✓ Proceso completado")

if __name__ == "__main__":
    main()

