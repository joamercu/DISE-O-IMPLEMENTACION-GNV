"""
Sistema de Autenticación y Gestión de Usuarios
Módulo de seguridad para la aplicación de cálculos GNV
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Optional

# Base de datos de usuarios (en producción debería ser una BD real)
# Formato: {username: {password_hash, role, created_at}}
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_DB_FILE = os.path.join(DATA_DIR, "users_db.json")

def hash_password(password: str) -> str:
    """Genera un hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users_db() -> Dict:
    """Carga la base de datos de usuarios desde archivo JSON"""
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users_db(users_db: Dict):
    """Guarda la base de datos de usuarios en archivo JSON"""
    with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_db, f, indent=2, ensure_ascii=False)

def init_default_users():
    """Inicializa usuarios por defecto si no existen"""
    users_db = load_users_db()
    
    # Usuario administrador por defecto
    if 'admin' not in users_db:
        users_db['admin'] = {
            'password_hash': hash_password('admin123'),  # Cambiar en producción
            'role': 'Administrador',
            'created_at': datetime.now().isoformat()
        }
    
    # Usuario cliente de ejemplo
    if 'cliente' not in users_db:
        users_db['cliente'] = {
            'password_hash': hash_password('cliente123'),  # Cambiar en producción
            'role': 'Cliente',
            'created_at': datetime.now().isoformat()
        }
    
    save_users_db(users_db)
    return users_db

def verify_user(username: str, password: str) -> Optional[Dict]:
    """Verifica las credenciales del usuario"""
    users_db = load_users_db()
    
    if username not in users_db:
        return None
    
    user = users_db[username]
    password_hash = hash_password(password)
    
    if user['password_hash'] == password_hash:
        return {
            'username': username,
            'role': user['role'],
            'created_at': user.get('created_at', '')
        }
    
    return None

def create_user(username: str, password: str, role: str) -> bool:
    """Crea un nuevo usuario (solo administradores)"""
    users_db = load_users_db()
    
    if username in users_db:
        return False  # Usuario ya existe
    
    users_db[username] = {
        'password_hash': hash_password(password),
        'role': role,
        'created_at': datetime.now().isoformat()
    }
    
    save_users_db(users_db)
    return True

def get_user_role(username: str) -> Optional[str]:
    """Obtiene el rol de un usuario"""
    users_db = load_users_db()
    if username in users_db:
        return users_db[username].get('role')
    return None

# Inicializar usuarios por defecto al importar el módulo
init_default_users()

