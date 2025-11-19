#!/usr/bin/env python3
"""
Script de verificación de vínculos y archivos del proyecto
"""
import os
import sys

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import (
    MANIFEST_FILE, USERS_DB_FILE, REMEMBERED_USER_FILE,
    DELIVERABLE_MD, DELIVERABLE_XLSX, DELIVERABLE_XML,
    DATA_DIR, DOCS_DIR, OUTPUTS_DIR, ASSETS_DIR
)

def verificar_archivo(nombre, ruta, opcional=False):
    """Verifica si un archivo existe"""
    existe = os.path.exists(ruta)
    estado = "✓" if existe else ("⚠️ (opcional)" if opcional else "✗")
    print(f"{estado} {nombre}: {ruta}")
    return existe

print("=" * 60)
print("VERIFICACIÓN DE VÍNCULOS Y ARCHIVOS DEL PROYECTO")
print("=" * 60)
print()

print("📁 DIRECTORIOS:")
print(f"  ✓ DATA_DIR: {DATA_DIR}")
print(f"  ✓ DOCS_DIR: {DOCS_DIR}")
print(f"  ✓ OUTPUTS_DIR: {OUTPUTS_DIR}")
print(f"  ✓ ASSETS_DIR: {ASSETS_DIR}")
print()

print("📄 ARCHIVOS DE DATOS:")
verificar_archivo("MANIFEST_FILE", MANIFEST_FILE)
verificar_archivo("USERS_DB_FILE", USERS_DB_FILE)
verificar_archivo("REMEMBERED_USER_FILE", REMEMBERED_USER_FILE, opcional=True)
print()

print("📄 ARCHIVOS DE ENTREGABLES:")
verificar_archivo("DELIVERABLE_MD", DELIVERABLE_MD)
verificar_archivo("DELIVERABLE_XLSX", DELIVERABLE_XLSX)
verificar_archivo("DELIVERABLE_XML", DELIVERABLE_XML)
print()

print("🔍 VERIFICACIÓN DE IMPORTS:")
try:
    from auth_system import verify_user
    print("  ✓ auth_system importado correctamente")
except ImportError as e:
    print(f"  ✗ Error importando auth_system: {e}")

try:
    from utils.auth_utils import load_remembered_user
    print("  ✓ utils.auth_utils importado correctamente")
except ImportError as e:
    print(f"  ✗ Error importando utils.auth_utils: {e}")

try:
    from utils.manifest_utils import load_manifest
    print("  ✓ utils.manifest_utils importado correctamente")
except ImportError as e:
    print(f"  ✗ Error importando utils.manifest_utils: {e}")

try:
    from utils.calculation_engine import calcular_sistema_gnv
    print("  ✓ utils.calculation_engine importado correctamente")
except ImportError as e:
    print(f"  ✗ Error importando utils.calculation_engine: {e}")

print()
print("=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)

