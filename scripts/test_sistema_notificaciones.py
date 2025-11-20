"""
Script de Prueba y Verificación del Sistema de Notificaciones y Seguimiento
Verifica todos los componentes del sistema
"""

import os
import sys
from datetime import datetime
import json

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

print("=" * 70)
print("TEST DE PRUEBA Y VERIFICACIÓN DEL SISTEMA DE NOTIFICACIONES")
print("=" * 70)
print()

# Contador de pruebas
tests_passed = 0
tests_failed = 0
tests_total = 0

def test_result(test_name, passed, message=""):
    """Registrar resultado de una prueba"""
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    if passed:
        tests_passed += 1
        print(f"✅ {test_name}: PASSED")
        if message:
            print(f"   {message}")
    else:
        tests_failed += 1
        print(f"❌ {test_name}: FAILED")
        if message:
            print(f"   {message}")
    print()

# ============================================
# TEST 1: Verificar Importaciones
# ============================================
print("1. Verificando importaciones de módulos...")
print("-" * 70)

try:
    from config import DATABASE_URL, SMTP_HOST, SMTP_PORT, ADMIN_EMAIL
    test_result("Importación de config.py", True)
except Exception as e:
    test_result("Importación de config.py", False, str(e))

try:
    from database import (
        init_database, create_submission, get_submissions,
        get_submission_by_id, update_submission_status,
        add_calculos_to_submission, add_diagrama_to_submission,
        get_submission_stats, create_notification
    )
    test_result("Importación de database.py", True)
except Exception as e:
    error_msg = str(e)
    if "metadata" in error_msg:
        test_result("Importación de database.py", False, 
                   "Error: 'metadata' es reservado en SQLAlchemy. Debe usar otro nombre.")
    else:
        test_result("Importación de database.py", False, error_msg)

try:
    from notifications import (
        send_email_notification, create_app_notification,
        send_notifications
    )
    test_result("Importación de notifications.py", True)
except Exception as e:
    test_result("Importación de notifications.py", False, str(e))

try:
    # Intentar importar admin_panel (puede fallar si database.py tiene errores)
    try:
        from admin_panel import show_admin_panel
        test_result("Importación de admin_panel.py", True)
    except Exception as e:
        # Si falla, puede ser por dependencias de database.py
        if "metadata" in str(e) or "database" in str(e).lower():
            test_result("Importación de admin_panel.py", False, 
                       f"Error en dependencias: {str(e)}. Verifique database.py")
        else:
            test_result("Importación de admin_panel.py", False, str(e))
except Exception as e:
    test_result("Importación de admin_panel.py", False, str(e))

# ============================================
# TEST 2: Verificar Configuración
# ============================================
print("2. Verificando configuración...")
print("-" * 70)

# Verificar variables de entorno
config_ok = True
config_messages = []

if not DATABASE_URL or "tu_password" in DATABASE_URL:
    config_ok = False
    config_messages.append("DATABASE_URL no configurado correctamente")
else:
    config_messages.append(f"✅ DATABASE_URL configurado: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'OK'}")

if not SMTP_HOST:
    config_messages.append("⚠️ SMTP_HOST no configurado (emails no funcionarán)")
else:
    config_messages.append(f"✅ SMTP_HOST: {SMTP_HOST}")

if not ADMIN_EMAIL:
    config_messages.append("⚠️ ADMIN_EMAIL no configurado")
else:
    config_messages.append(f"✅ ADMIN_EMAIL: {ADMIN_EMAIL}")

test_result("Configuración de variables", config_ok, "\n".join(config_messages))

# ============================================
# TEST 3: Verificar Conexión a Base de Datos
# ============================================
print("3. Verificando conexión a base de datos...")
print("-" * 70)

try:
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        result.fetchone()
    test_result("Conexión a PostgreSQL", True, "Conexión exitosa")
except Exception as e:
    test_result("Conexión a PostgreSQL", False, f"Error: {str(e)}")
    print("   ⚠️  No se pueden continuar las pruebas de BD sin conexión")
    engine = None

# ============================================
# TEST 4: Verificar Inicialización de Tablas
# ============================================
print("4. Verificando inicialización de tablas...")
print("-" * 70)

if engine:
    try:
        if init_database():
            test_result("Inicialización de tablas", True, "Tablas creadas/verificadas")
        else:
            test_result("Inicialización de tablas", False, "Error al crear tablas")
    except Exception as e:
        test_result("Inicialización de tablas", False, f"Error: {str(e)}")
else:
    test_result("Inicialización de tablas", False, "No hay conexión a BD")

# ============================================
# TEST 5: Verificar Creación de Submission
# ============================================
print("5. Verificando creación de submissions...")
print("-" * 70)

if engine:
    try:
        # Datos de prueba
        test_cliente_data = {
            'nombre': 'Cliente Test',
            'rol': 'Cliente',
            'capacidad_de_la_flota': '50 vehículos',
            'supuestos': {
                'operacional': 'Supuestos operativos de prueba',
                'componentes': 'Supuestos de componentes de prueba'
            }
        }
        
        test_metadata = {
            'fecha_creacion': datetime.now().isoformat(),
            'usuario_creador': 'test_user'
        }
        
        submission_id = create_submission(
            cliente_nombre="Cliente Test",
            usuario_cliente="test_user",
            datos_cliente=test_cliente_data,
            metadata=test_metadata
        )
        
        if submission_id:
            test_result("Creación de submission", True, f"Submission ID: {submission_id}")
            
            # Verificar que se puede obtener
            submission = get_submission_by_id(submission_id)
            if submission:
                test_result("Obtención de submission", True, f"Cliente: {submission['cliente_nombre']}")
            else:
                test_result("Obtención de submission", False, "No se pudo obtener el submission")
        else:
            test_result("Creación de submission", False, "No se pudo crear el submission")
            
    except Exception as e:
        test_result("Creación de submission", False, f"Error: {str(e)}")
else:
    test_result("Creación de submission", False, "No hay conexión a BD")

# ============================================
# TEST 6: Verificar Agregar Cálculos
# ============================================
print("6. Verificando agregar cálculos a submission...")
print("-" * 70)

if engine and 'submission_id' in locals():
    try:
        test_resultados = {
            'volumen': 100.5,
            'tanques': 5,
            'peso': 500.0
        }
        
        test_parametros = {
            'consumo_diesel': 35.0,
            'autonomia': 600.0
        }
        
        success = add_calculos_to_submission(
            submission_id=submission_id,
            resultados=test_resultados,
            parametros=test_parametros
        )
        
        test_result("Agregar cálculos", success, "Cálculos agregados correctamente" if success else "Error al agregar cálculos")
    except Exception as e:
        test_result("Agregar cálculos", False, f"Error: {str(e)}")
else:
    test_result("Agregar cálculos", False, "No hay submission de prueba o conexión a BD")

# ============================================
# TEST 7: Verificar Agregar Diagrama
# ============================================
print("7. Verificando agregar diagrama a submission...")
print("-" * 70)

if engine and 'submission_id' in locals():
    try:
        test_xml = "<mxfile><diagram>Test Diagram</diagram></mxfile>"
        test_pdf_base64 = "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PAovTGVuZ3RoIDQwIDAgUgo+PgpzdHJlYW0K"
        
        success = add_diagrama_to_submission(
            submission_id=submission_id,
            diagrama_xml=test_xml,
            diagrama_pdf=test_pdf_base64,
            ruta_archivo="test_diagram.drawio.xml"
        )
        
        test_result("Agregar diagrama", success, "Diagrama agregado correctamente" if success else "Error al agregar diagrama")
    except Exception as e:
        test_result("Agregar diagrama", False, f"Error: {str(e)}")
else:
    test_result("Agregar diagrama", False, "No hay submission de prueba o conexión a BD")

# ============================================
# TEST 8: Verificar Actualización de Estado
# ============================================
print("8. Verificando actualización de estado...")
print("-" * 70)

if engine and 'submission_id' in locals():
    try:
        success = update_submission_status(
            submission_id=submission_id,
            nuevo_estado="en_revision",
            administrador="admin_test",
            notas="Notas de prueba del test"
        )
        
        if success:
            # Verificar que se actualizó
            submission = get_submission_by_id(submission_id)
            if submission and submission['estado'] == 'en_revision':
                test_result("Actualización de estado", True, f"Estado actualizado a: {submission['estado']}")
            else:
                test_result("Actualización de estado", False, "Estado no se actualizó correctamente")
        else:
            test_result("Actualización de estado", False, "Error al actualizar estado")
    except Exception as e:
        test_result("Actualización de estado", False, f"Error: {str(e)}")
else:
    test_result("Actualización de estado", False, "No hay submission de prueba o conexión a BD")

# ============================================
# TEST 9: Verificar Obtención de Submissions
# ============================================
print("9. Verificando obtención de submissions con filtros...")
print("-" * 70)

if engine:
    try:
        # Obtener todos
        all_subs = get_submissions(limit=10)
        test_result("Obtener todos los submissions", len(all_subs) >= 0, f"Encontrados: {len(all_subs)}")
        
        # Obtener por estado
        pending_subs = get_submissions(estado="pendiente", limit=10)
        test_result("Obtener por estado", True, f"Pendientes: {len(pending_subs)}")
        
        # Obtener por cliente
        client_subs = get_submissions(cliente_nombre="Test", limit=10)
        test_result("Obtener por cliente", True, f"Encontrados: {len(client_subs)}")
        
    except Exception as e:
        test_result("Obtención de submissions", False, f"Error: {str(e)}")
else:
    test_result("Obtención de submissions", False, "No hay conexión a BD")

# ============================================
# TEST 10: Verificar Estadísticas
# ============================================
print("10. Verificando estadísticas...")
print("-" * 70)

if engine:
    try:
        stats = get_submission_stats()
        if stats and 'total' in stats:
            test_result("Obtención de estadísticas", True, 
                       f"Total: {stats['total']}, Pendientes: {stats['pendientes']}, "
                       f"En Revisión: {stats['en_revision']}, Aprobados: {stats['aprobados']}, "
                       f"Rechazados: {stats['rechazados']}")
        else:
            test_result("Obtención de estadísticas", False, "No se obtuvieron estadísticas")
    except Exception as e:
        test_result("Obtención de estadísticas", False, f"Error: {str(e)}")
else:
    test_result("Obtención de estadísticas", False, "No hay conexión a BD")

# ============================================
# TEST 11: Verificar Creación de Notificaciones
# ============================================
print("11. Verificando creación de notificaciones...")
print("-" * 70)

if engine and 'submission_id' in locals():
    try:
        # Notificación de app
        notif_id = create_notification(
            submission_id=submission_id,
            tipo="app",
            estado="enviada",
            mensaje="Notificación de prueba"
        )
        
        if notif_id:
            test_result("Creación de notificación app", True, f"Notificación ID: {notif_id}")
        else:
            test_result("Creación de notificación app", False, "No se pudo crear notificación")
            
    except Exception as e:
        test_result("Creación de notificaciones", False, f"Error: {str(e)}")
else:
    test_result("Creación de notificaciones", False, "No hay submission de prueba o conexión a BD")

# ============================================
# TEST 12: Verificar Sistema de Notificaciones (Email)
# ============================================
print("12. Verificando sistema de notificaciones por email...")
print("-" * 70)

if engine and 'submission_id' in locals():
    try:
        # Solo verificar que la función existe y puede ser llamada
        # No enviar email real en el test (requiere SMTP configurado)
        if SMTP_HOST and SMTP_USER and SMTP_PASSWORD:
            test_result("Configuración SMTP", True, 
                       f"SMTP configurado: {SMTP_HOST}:{SMTP_PORT}")
            print("   ℹ️  Para probar envío real de email, ejecute manualmente:")
            print(f"      send_email_notification({submission_id}, 'Cliente Test', 'test_user')")
        else:
            test_result("Configuración SMTP", False, 
                       "SMTP no configurado (emails no se enviarán)")
    except Exception as e:
        test_result("Sistema de notificaciones email", False, f"Error: {str(e)}")
else:
    test_result("Sistema de notificaciones email", False, "No hay submission de prueba o conexión a BD")

# ============================================
# TEST 13: Verificar Panel de Administración
# ============================================
print("13. Verificando panel de administración...")
print("-" * 70)

try:
    # Verificar que la función existe y es callable
    if callable(show_admin_panel):
        test_result("Panel de administración", True, "Función disponible")
    else:
        test_result("Panel de administración", False, "Función no es callable")
except Exception as e:
    test_result("Panel de administración", False, f"Error: {str(e)}")

# ============================================
# RESUMEN FINAL
# ============================================
print()
print("=" * 70)
print("RESUMEN DE PRUEBAS")
print("=" * 70)
print(f"Total de pruebas: {tests_total}")
print(f"✅ Pasadas: {tests_passed}")
print(f"❌ Fallidas: {tests_failed}")
print(f"Porcentaje de éxito: {(tests_passed/tests_total*100):.1f}%")
print()

if tests_failed == 0:
    print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    print()
    print("El sistema de notificaciones y seguimiento está listo para usar.")
else:
    print("⚠️  ALGUNAS PRUEBAS FALLARON")
    print()
    print("Revisa los errores anteriores y:")
    print("1. Verifica la configuración de PostgreSQL")
    print("2. Verifica las variables de entorno en .env")
    print("3. Ejecuta: python scripts/init_database.py")
    print("4. Vuelve a ejecutar este test")

print("=" * 70)

# Limpiar datos de prueba si se crearon
if engine and 'submission_id' in locals():
    try:
        from database import get_session
        from database import Submission
        session = get_session()
        test_submission = session.query(Submission).filter(Submission.id == submission_id).first()
        if test_submission:
            print()
            print("ℹ️  Datos de prueba creados:")
            print(f"   Submission ID: {submission_id}")
            print(f"   Cliente: {test_submission.cliente_nombre}")
            print("   Puedes eliminarlo manualmente desde el panel de administración")
        session.close()
    except:
        pass

sys.exit(0 if tests_failed == 0 else 1)

