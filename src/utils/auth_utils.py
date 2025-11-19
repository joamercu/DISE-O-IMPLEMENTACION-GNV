"""
Utilidades de autenticación
"""
import json
import os

# Importar configuración
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REMEMBERED_USER_FILE

def load_remembered_user():
    """Carga el último usuario recordado"""
    remembered_file = REMEMBERED_USER_FILE
    if os.path.exists(remembered_file):
        try:
            with open(remembered_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('username', ''), data.get('role', 'Cliente')
        except:
            return '', 'Cliente'
    return '', 'Cliente'

def save_remembered_user(username, role):
    """Guarda el usuario para recordarlo"""
    remembered_file = REMEMBERED_USER_FILE
    try:
        with open(remembered_file, 'w', encoding='utf-8') as f:
            json.dump({'username': username, 'role': role}, f, indent=2, ensure_ascii=False)
    except:
        pass

def clear_remembered_user():
    """Elimina el usuario recordado"""
    remembered_file = REMEMBERED_USER_FILE
    if os.path.exists(remembered_file):
        try:
            os.remove(remembered_file)
        except:
            pass

