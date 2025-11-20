# 🚀 Guía de Despliegue al Servidor Debian

Esta guía explica cómo usar los scripts para desplegar la aplicación GNV al servidor Debian desde el branch `developer`.

## 📋 Requisitos Previos

1. **Clave SSH**: Necesitas una clave SSH para conectarte al servidor
   - Coloca tu clave privada en: `scripts/../ssh_key` (o edita la ruta en `config_servidor.bat`)
   - O configura SSH para usar tu clave por defecto

2. **Acceso al servidor**: Debes tener acceso SSH al servidor `72.61.10.156`

3. **Repositorio Git**: El proyecto debe estar en un repositorio Git con el branch `developer`

## 🔧 Configuración Inicial

### 1. Configurar Variables del Servidor

**IMPORTANTE**: Debes ejecutar esto PRIMERO antes de cualquier otro script:
```batch
scripts\config_servidor.bat
```

Este script crea el archivo `deploy_config.txt` con todas las variables necesarias.

**Si tienes problemas con rutas que contienen espacios**, el script ahora las maneja correctamente.

Este script crea el archivo `deploy_config.txt` con las siguientes variables:
- `SERVIDOR_IP`: IP del servidor (72.61.10.156)
- `SERVIDOR_USUARIO`: Usuario SSH (por defecto: root)
- `SERVIDOR_RUTA`: Ruta donde se desplegará la app (/var/www/gnv-app)
- `BRANCH`: Branch a desplegar (developer)
- `SSH_KEY`: Ruta a la clave SSH privada
- `LOGS_DIR`: Directorio donde se guardan los logs locales

**Nota**: Puedes editar `deploy_config.txt` manualmente si necesitas cambiar algún valor.

## 📦 Scripts Disponibles

### 1. `deploy_app.bat` - Desplegar la Aplicación

Este script:
- Verifica la conexión SSH
- Actualiza el código desde el branch `developer`
- Instala/actualiza dependencias en el servidor
- Registra todo en logs con timestamp

**Uso**:
```batch
scripts\deploy_app.bat
```

**Logs generados**:
- `logs_deploy\deploy_YYYYMMDD_HHMMSS.log` - Log completo del despliegue
- `logs_deploy\deploy_error_YYYYMMDD_HHMMSS.log` - Errores
- `logs_deploy\last_commit.txt` - Información del último commit desplegado

### 2. `iniciar_app_servidor.bat` - Iniciar la Aplicación

Inicia la aplicación Streamlit en el servidor en modo background.

**Uso**:
```batch
scripts\iniciar_app_servidor.bat
```

**Características**:
- Verifica si ya está corriendo
- Inicia en background usando `nohup`
- Guarda el PID en `logs/streamlit.pid`
- Los logs se guardan en `logs/streamlit.log` en el servidor

### 3. `iniciar_api_servidor.bat` - Iniciar la API

Inicia la API FastAPI en el servidor en modo background.

**Uso**:
```batch
scripts\iniciar_api_servidor.bat
```

**Características**:
- Similar a `iniciar_app_servidor.bat` pero para la API
- Puerto: 8000
- Logs en `logs/api.log`

### 4. `ver_logs_servidor.bat` - Ver Logs

Muestra los logs del servidor con varias opciones.

**Uso**:
```batch
scripts\ver_logs_servidor.bat
```

**Opciones**:
1. Logs de Streamlit (aplicación)
2. Logs de API
3. Logs del sistema (systemd)
4. Ver todos los logs
5. Seguir logs en tiempo real (tail -f)
6. Ver últimas 50 líneas de Streamlit
7. Ver últimas 50 líneas de API
8. Ver procesos corriendo

### 5. `detener_app_servidor.bat` - Detener Aplicación

Detiene la aplicación y/o API en el servidor.

**Uso**:
```batch
scripts\detener_app_servidor.bat
```

**Opciones**:
1. Solo Streamlit (aplicación)
2. Solo API
3. Ambos

### 6. `estado_servidor.bat` - Ver Estado

Muestra el estado completo del servidor:
- Procesos corriendo
- Puertos en uso
- Último commit desplegado
- Branch actual
- Espacio en disco
- Memoria disponible
- Archivos PID
- Tamaño de logs

**Uso**:
```batch
scripts\estado_servidor.bat
```

### 7. `configurar_nginx.bat` - Configurar Nginx

Configura Nginx para que solo `gnv.weldtech.cloud` apunte a esta aplicación.

**⚠️ IMPORTANTE**: Este script asegura que:
- `gnv.weldtech.cloud` → Aplicación GNV (puerto 8501)
- `api-gnv.weldtech.cloud` → API GNV (puerto 8000)
- `weldtech.cloud` → NO debe apuntar a esta aplicación (debe apuntar a otra)

**Uso**:
```batch
scripts\configurar_nginx.bat
```

**Qué hace**:
- Crea backup de configuración actual
- Crea configuración para `gnv.weldtech.cloud`
- Verifica que no haya configuraciones conflictivas
- Valida la configuración de nginx
- Recarga nginx

### 8. `verificar_nginx.bat` - Verificar Nginx

Verifica la configuración actual de Nginx en el servidor.

**Uso**:
```batch
scripts\verificar_nginx.bat
```

**Muestra**:
- Configuraciones disponibles y habilitadas
- Server names configurados
- Estado de nginx
- Validación de configuración
- Contenido de la configuración GNV

## 🔄 Flujo de Trabajo Típico

### Despliegue Inicial

1. **Configurar servidor** (solo la primera vez):
   ```batch
   scripts\config_servidor.bat
   ```

2. **Clonar repositorio en el servidor** (solo la primera vez):
   Conéctate por SSH y ejecuta:
   ```bash
   git clone -b developer [URL_DEL_REPO] /var/www/gnv-app
   ```

3. **Desplegar**:
   ```batch
   scripts\deploy_app.bat
   ```

4. **Iniciar aplicación**:
   ```batch
   scripts\iniciar_app_servidor.bat
   ```

5. **Iniciar API** (opcional):
   ```batch
   scripts\iniciar_api_servidor.bat
   ```

6. **Configurar Nginx** (importante para dominios):
   ```batch
   scripts\configurar_nginx.bat
   ```
   
   Esto asegura que solo `gnv.weldtech.cloud` apunte a esta aplicación.

### Actualización (Despliegue Incremental)

1. **Desplegar cambios**:
   ```batch
   scripts\deploy_app.bat
   ```

2. **Reiniciar aplicación** (si es necesario):
   ```batch
   scripts\detener_app_servidor.bat
   scripts\iniciar_app_servidor.bat
   ```

### Monitoreo

1. **Ver estado**:
   ```batch
   scripts\estado_servidor.bat
   ```

2. **Ver logs**:
   ```batch
   scripts\ver_logs_servidor.bat
   ```

## 📁 Estructura de Logs

### Logs Locales (en tu máquina Windows)
```
logs_deploy/
├── deploy_YYYYMMDD_HHMMSS.log      # Logs de despliegue
├── deploy_error_YYYYMMDD_HHMMSS.log # Errores de despliegue
├── start_YYYYMMDD_HHMMSS.log        # Logs de inicio
├── start_error_YYYYMMDD_HHMMSS.log  # Errores de inicio
├── stop_YYYYMMDD_HHMMSS.log         # Logs de detención
├── last_commit.txt                  # Último commit desplegado
├── streamlit_pid.txt                # PID de Streamlit
└── api_pid.txt                      # PID de API
```

### Logs en el Servidor
```
/var/www/gnv-app/logs/
├── streamlit.log    # Logs de la aplicación Streamlit
├── streamlit.pid    # PID de Streamlit
├── api.log          # Logs de la API
└── api.pid          # PID de la API
```

## 🔐 Configuración de Clave SSH

### Opción 1: Clave en archivo específico

1. Coloca tu clave privada en: `scripts/../ssh_key`
2. Asegúrate de que tenga permisos correctos (en Linux: `chmod 600`)

### Opción 2: Usar clave por defecto

Si tu clave SSH está en `~/.ssh/id_rsa` (o configurada en `~/.ssh/config`), los scripts la usarán automáticamente.

### Opción 3: Editar configuración

Edita `deploy_config.txt` y cambia la ruta de `SSH_KEY` o déjala vacía para usar la clave por defecto.

## ⚠️ Solución de Problemas

### Error: "El sistema no puede encontrar el archivo" o variables vacías

**Causa**: El archivo de configuración no existe o no se está leyendo correctamente.

**Solución**:
1. Ejecuta primero: `scripts\config_servidor.bat`
2. Verifica la configuración: `scripts\verificar_config.bat`
3. Si el problema persiste, edita manualmente `scripts\deploy_config.txt`

### Error: "No se pudo conectar al servidor"
- Verifica que la IP del servidor sea correcta
- Verifica que la clave SSH sea válida
- Prueba la conexión manualmente: `ssh usuario@72.61.10.156`

### Error: "El repositorio no existe en el servidor"
- Clona el repositorio primero en el servidor
- O verifica que la ruta `SERVIDOR_RUTA` sea correcta

### Error: "No se pudo actualizar el código"
- Verifica que el branch `developer` exista
- Verifica permisos en el servidor
- Revisa los logs de error

### La aplicación no inicia
- Verifica los logs: `ver_logs_servidor.bat`
- Verifica que las dependencias estén instaladas
- Verifica que los puertos 8501 y 8000 estén disponibles

## 📝 Notas Importantes

1. **Primera vez**: Debes clonar el repositorio manualmente en el servidor antes de usar `deploy_app.bat`

2. **Puertos**: Asegúrate de que los puertos 8501 (Streamlit) y 8000 (API) estén abiertos en el firewall

3. **Nginx**: Configura Nginx para que solo `gnv.weldtech.cloud` apunte a esta aplicación:
   - Ejecuta: `scripts\configurar_nginx.bat` (desde Windows)
   - O ejecuta: `bash scripts/config_nginx_servidor.sh` (directamente en el servidor)
   - Verifica: `scripts\verificar_nginx.bat`
   - Ver documentación: `scripts\CONFIGURACION_NGINX.md`

4. **Permisos**: Asegúrate de que el usuario SSH tenga permisos para escribir en `SERVIDOR_RUTA`

5. **Python**: El servidor debe tener Python 3 y pip3 instalados

## 🔗 URLs de Acceso

Después del despliegue, la aplicación estará disponible en:
- **Aplicación**: `http://gnv.weldtech.cloud` o `http://72.61.10.156:8501`
- **API**: `http://api-gnv.weldtech.cloud` o `http://72.61.10.156:8000`
- **Documentación API**: `http://72.61.10.156:8000/docs`

