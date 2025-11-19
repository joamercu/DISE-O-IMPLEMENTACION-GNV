# 🚀 Guía de Instalación - Aplicación GNV

## Requisitos Previos

### Sistema Operativo
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, etc.)
- ✅ macOS

### Software Requerido
- **Python 3.8 o superior**
  - Descargar desde: https://www.python.org/downloads/
  - Verificar instalación: `python --version`

## Instalación Paso a Paso

### Opción 1: Instalación Automática (Windows)

1. **Descargar o clonar el proyecto**
   ```bash
   # Si tiene Git
   git clone [url-del-repositorio]
   ```

2. **Ejecutar script de instalación**
   - Doble clic en: `scripts/instalar_dependencias.bat`
   - O desde terminal:
     ```bash
     scripts\instalar_dependencias.bat
     ```

3. **Iniciar la aplicación**
   - Doble clic en: `scripts/iniciar_app.bat`

### Opción 2: Instalación Manual

1. **Navegar al directorio del proyecto**
   ```bash
   cd "D:\19-11-25-DISEÑO E IMPLEMENTACION GNV"
   ```

2. **Crear entorno virtual (Recomendado)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verificar instalación**
   ```bash
   python -c "import streamlit; import pandas; print('OK')"
   ```

5. **Iniciar la aplicación**
   ```bash
   cd src
   streamlit run calculos_combustible_vehicular.py
   ```

## Estructura de Directorios Requerida

Asegúrese de que existan los siguientes directorios:

```
proyecto/
├── src/                    # ✅ Debe existir
│   ├── calculos_combustible_vehicular.py
│   ├── auth_system.py
│   ├── config.py
│   └── utils/
├── data/                   # ✅ Crear si no existe
│   ├── PETROLIQUIDOS_GNV_manifest_v1.json
│   └── users_db.json (se crea automáticamente)
└── docs/                   # ✅ Opcional
```

### Crear Directorios Faltantes

**Windows:**
```bash
mkdir data
mkdir docs
```

**Linux/macOS:**
```bash
mkdir -p data docs
```

## Verificación de Instalación

### 1. Verificar Python
```bash
python --version
# Debe mostrar: Python 3.8.x o superior
```

### 2. Verificar Dependencias
```bash
pip list | findstr streamlit
pip list | findstr pandas
```

### 3. Verificar Archivos
```bash
# Windows
dir src\calculos_combustible_vehicular.py
dir src\config.py
dir data\PETROLIQUIDOS_GNV_manifest_v1.json
```

## Configuración Inicial

### Archivos de Datos

El sistema crea automáticamente:
- `data/users_db.json` - Base de datos de usuarios
- `data/remembered_user.json` - Usuario recordado (opcional)

### Usuarios por Defecto

Al iniciar por primera vez, se crean automáticamente:

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`
- ⚠️ **IMPORTANTE:** Cambiar en producción

**Cliente:**
- Usuario: `cliente`
- Contraseña: `cliente123`
- ⚠️ **IMPORTANTE:** Cambiar en producción

## Solución de Problemas

### Error: "Python no está instalado"
**Solución:**
1. Instalar Python desde https://www.python.org/
2. Asegurarse de marcar "Add Python to PATH" durante la instalación
3. Reiniciar terminal/consola

### Error: "Streamlit no está instalado"
**Solución:**
```bash
pip install streamlit>=1.28.0
```

### Error: "No se encuentra el archivo manifest"
**Solución:**
1. Verificar que `data/PETROLIQUIDOS_GNV_manifest_v1.json` existe
2. Si no existe, crear el directorio `data/`
3. Copiar el archivo manifest a `data/`

### Error: "ModuleNotFoundError"
**Solución:**
```bash
# Asegurarse de estar en el directorio correcto
cd src
# Reinstalar dependencias
pip install -r ../requirements.txt
```

### La aplicación no se abre en el navegador
**Solución:**
1. Abrir manualmente: http://localhost:8501
2. Verificar que el puerto 8501 no esté en uso
3. Cambiar puerto: `streamlit run calculos_combustible_vehicular.py --server.port 8502`

## Actualización

### Actualizar Dependencias
```bash
pip install --upgrade -r requirements.txt
```

### Actualizar Código
```bash
# Si usa Git
git pull origin main
```

## Desinstalación

### Eliminar Dependencias
```bash
pip uninstall streamlit pandas
```

### Eliminar Datos
```bash
# Eliminar archivos de datos (opcional)
rm -rf data/users_db.json
rm -rf data/remembered_user.json
```

## Configuración Avanzada

### Cambiar Puerto
Editar `src/calculos_combustible_vehicular.py` o usar:
```bash
streamlit run calculos_combustible_vehicular.py --server.port 8502
```

### Modo Headless (sin navegador)
```bash
streamlit run calculos_combustible_vehicular.py --server.headless true
```

### Configuración de Streamlit
Crear `.streamlit/config.toml`:
```toml
[server]
port = 8501
headless = false

[browser]
gatherUsageStats = false
```

## Requisitos del Sistema

### Mínimos
- RAM: 2 GB
- Disco: 100 MB libres
- CPU: Cualquier procesador moderno

### Recomendados
- RAM: 4 GB o más
- Disco: 500 MB libres
- CPU: Procesador multi-core

## Soporte

Para problemas de instalación:
1. Revisar esta guía
2. Verificar logs de errores
3. Contactar al equipo de desarrollo

---

*Guía actualizada: 2024-12-19*

