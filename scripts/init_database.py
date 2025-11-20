"""
Script de inicialización de la base de datos PostgreSQL
Crea la base de datos, usuario y tablas necesarias
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from database import init_database


def create_database_and_user():
    """Crear base de datos y usuario si no existen"""
    
    print("=" * 60)
    print("Inicialización de Base de Datos PostgreSQL")
    print("=" * 60)
    print()
    
    # Conectar a PostgreSQL (base de datos por defecto)
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database='postgres',  # Conectar a la BD por defecto
            user=DB_USER if DB_USER != 'gnv_user' else 'postgres',  # Usar postgres si no está configurado
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print(f"✅ Conectado a PostgreSQL en {DB_HOST}:{DB_PORT}")
        
        # Verificar si la base de datos existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        
        if cursor.fetchone():
            print(f"ℹ️  La base de datos '{DB_NAME}' ya existe.")
        else:
            # Crear base de datos
            print(f"📦 Creando base de datos '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"✅ Base de datos '{DB_NAME}' creada exitosamente.")
        
        cursor.close()
        conn.close()
        
        # Crear tablas
        print()
        print("📋 Creando tablas...")
        if init_database():
            print("✅ Tablas creadas exitosamente.")
        else:
            print("❌ Error al crear las tablas.")
            return False
        
        print()
        print("=" * 60)
        print("✅ Inicialización completada exitosamente!")
        print("=" * 60)
        print()
        print("Próximos pasos:")
        print("1. Configure las variables de entorno en el archivo .env")
        print("2. Inicie la aplicación con: scripts/iniciar_app.bat")
        print()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión: {str(e)}")
        print()
        print("Verifique:")
        print(f"  - PostgreSQL está ejecutándose en {DB_HOST}:{DB_PORT}")
        print(f"  - Las credenciales en .env son correctas")
        print(f"  - El usuario tiene permisos para crear bases de datos")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False


if __name__ == "__main__":
    if not DB_PASSWORD:
        print("⚠️  ADVERTENCIA: DB_PASSWORD no está configurado.")
        print("   Configure las variables de entorno en el archivo .env")
        print()
        respuesta = input("¿Desea continuar de todos modos? (s/n): ")
        if respuesta.lower() != 's':
            sys.exit(1)
    
    success = create_database_and_user()
    sys.exit(0 if success else 1)

