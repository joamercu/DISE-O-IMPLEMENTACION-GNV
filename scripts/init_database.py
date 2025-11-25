"""
Script de inicialización de la base de datos PostgreSQL
Crea la base de datos, usuario y tablas necesarias de forma segura
NO genera conflictos con bases de datos existentes
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from database import init_database


def get_postgres_credentials():
    """Obtener credenciales para conectarse como superusuario postgres"""
    # Intentar usar variables de entorno específicas para postgres
    postgres_user = os.getenv('POSTGRES_USER', 'postgres')
    postgres_password = os.getenv('POSTGRES_PASSWORD', DB_PASSWORD)
    
    # Si el usuario configurado es diferente a gnv_user, intentar usarlo
    if DB_USER != 'gnv_user' and DB_USER != 'postgres':
        # Intentar primero con el usuario configurado
        return DB_USER, DB_PASSWORD
    
    return postgres_user, postgres_password


def check_user_exists(cursor, username):
    """Verificar si un usuario existe en PostgreSQL"""
    try:
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            (username,)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"⚠️  Error al verificar usuario: {str(e)}")
        return False


def check_database_exists(cursor, dbname):
    """Verificar si una base de datos existe"""
    try:
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (dbname,)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"⚠️  Error al verificar base de datos: {str(e)}")
        return False


def create_database_and_user():
    """Crear base de datos y usuario si no existen (seguro, sin conflictos)"""
    
    print("=" * 70)
    print("🔧 INICIALIZACIÓN SEGURA DE BASE DE DATOS POSTGRESQL")
    print("=" * 70)
    print()
    print("Este script NO modificará bases de datos existentes.")
    print("Solo creará lo que no existe.")
    print()
    
    # Obtener credenciales para conectarse como superusuario
    admin_user, admin_password = get_postgres_credentials()
    
    # Conectar a PostgreSQL (base de datos por defecto)
    try:
        print(f"📡 Conectando a PostgreSQL en {DB_HOST}:{DB_PORT}...")
        print(f"   Usuario admin: {admin_user}")
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database='postgres',  # Conectar a la BD por defecto
            user=admin_user,
            password=admin_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print(f"✅ Conectado exitosamente a PostgreSQL")
        print()
        
        # ============================================
        # 1. Verificar/Crear Usuario
        # ============================================
        print("=" * 70)
        print("👤 PASO 1: Verificando/Creando Usuario")
        print("=" * 70)
        
        user_exists = check_user_exists(cursor, DB_USER)
        
        if user_exists:
            print(f"✅ El usuario '{DB_USER}' ya existe. No se modificará.")
        else:
            if not DB_PASSWORD:
                print(f"⚠️  No se puede crear el usuario '{DB_USER}': DB_PASSWORD no está configurado.")
                print(f"   Configure DB_PASSWORD en el archivo .env")
                print()
                print("   Continuando sin crear el usuario...")
                print("   (Puede que el usuario ya exista con otra contraseña)")
            else:
                try:
                    print(f"📦 Creando usuario '{DB_USER}'...")
                    # Usar parámetros seguros para evitar inyección SQL
                    cursor.execute(
                        sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                            sql.Identifier(DB_USER)
                        ),
                        (DB_PASSWORD,)
                    )
                    print(f"✅ Usuario '{DB_USER}' creado exitosamente.")
                except psycopg2.errors.DuplicateObject:
                    print(f"ℹ️  El usuario '{DB_USER}' ya existe (creado por otro proceso).")
                except Exception as e:
                    print(f"⚠️  No se pudo crear el usuario: {str(e)}")
                    print(f"   Continuando... (puede que ya exista)")
        
        print()
        
        # ============================================
        # 2. Verificar/Crear Base de Datos
        # ============================================
        print("=" * 70)
        print("💾 PASO 2: Verificando/Creando Base de Datos")
        print("=" * 70)
        
        db_exists = check_database_exists(cursor, DB_NAME)
        
        if db_exists:
            print(f"✅ La base de datos '{DB_NAME}' ya existe. No se modificará.")
            print(f"   Los datos existentes están seguros.")
        else:
            try:
                print(f"📦 Creando base de datos '{DB_NAME}'...")
                # Usar parámetros seguros
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(DB_NAME)
                    )
                )
                print(f"✅ Base de datos '{DB_NAME}' creada exitosamente.")
            except psycopg2.errors.DuplicateDatabase:
                print(f"ℹ️  La base de datos '{DB_NAME}' ya existe (creada por otro proceso).")
            except Exception as e:
                print(f"⚠️  Error al crear base de datos: {str(e)}")
                cursor.close()
                conn.close()
                return False
        
        print()
        
        # ============================================
        # 3. Asignar Permisos
        # ============================================
        print("=" * 70)
        print("🔐 PASO 3: Asignando Permisos")
        print("=" * 70)
        
        try:
            # Dar permisos al usuario sobre la base de datos
            print(f"🔑 Otorgando permisos a '{DB_USER}' sobre '{DB_NAME}'...")
            
            # Conectar a la base de datos específica para otorgar permisos
            conn_db = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=admin_user,
                password=admin_password
            )
            conn_db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor_db = conn_db.cursor()
            
            # Otorgar todos los privilegios
            cursor_db.execute(
                sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                    sql.Identifier(DB_NAME),
                    sql.Identifier(DB_USER)
                )
            )
            
            # Otorgar permisos en el esquema público
            cursor_db.execute("GRANT ALL ON SCHEMA public TO {}".format(DB_USER))
            cursor_db.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}".format(DB_USER))
            
            print(f"✅ Permisos otorgados exitosamente.")
            
            cursor_db.close()
            conn_db.close()
            
        except Exception as e:
            print(f"⚠️  Advertencia al otorgar permisos: {str(e)}")
            print(f"   Continuando... (puede que los permisos ya estén configurados)")
        
        cursor.close()
        conn.close()
        
        print()
        
        # ============================================
        # 4. Crear Tablas
        # ============================================
        print("=" * 70)
        print("📋 PASO 4: Creando/Verificando Tablas")
        print("=" * 70)
        print()
        print("📋 Inicializando tablas en la base de datos...")
        print("   (Las tablas existentes NO se modificarán)")
        
        if init_database():
            print("✅ Tablas verificadas/creadas exitosamente.")
            print("   (create_all solo crea tablas que no existen)")
        else:
            print("❌ Error al inicializar las tablas.")
            print("   Verifique las credenciales y permisos del usuario.")
            return False
        
        print()
        print("=" * 70)
        print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print()
        print("📊 Resumen:")
        print(f"   ✅ Usuario: {DB_USER} (verificado/creado)")
        print(f"   ✅ Base de datos: {DB_NAME} (verificada/creada)")
        print(f"   ✅ Tablas: Inicializadas (solo se crearon las faltantes)")
        print()
        print("💡 Próximos pasos:")
        print("   1. Verifique que el archivo .env tenga las credenciales correctas")
        print("   2. Ejecute la prueba: python test_database_connection.py")
        print("   3. Inicie la aplicación: scripts/iniciar_app.bat")
        print()
        
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"❌ Error de conexión: {error_msg}")
        print()
        print("🔍 Diagnóstico:")
        print(f"   - Host: {DB_HOST}")
        print(f"   - Puerto: {DB_PORT}")
        print(f"   - Usuario admin intentado: {admin_user}")
        print()
        print("💡 Soluciones:")
        print("   1. Verifique que PostgreSQL esté ejecutándose")
        print("   2. Configure POSTGRES_USER y POSTGRES_PASSWORD en .env")
        print("      (o use las credenciales del superusuario postgres)")
        print("   3. Verifique que el usuario tenga permisos de superusuario")
        print()
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        print()
        print("Detalles técnicos:")
        traceback.print_exc()
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

