@echo off
REM ============================================
REM Script para configurar Nginx desde SSH
REM Solo gnv.weldtech.cloud debe apuntar a esta app
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   CONFIGURAR NGINX PARA GNV
echo ============================================
echo.

REM Cargar configuración
set CONFIG_FILE=%~dp0deploy_config.txt
if not exist "%CONFIG_FILE%" (
    echo ERROR: Archivo de configuracion no encontrado.
    echo Ejecute primero: config_servidor.bat
    pause
    exit /b 1
)

REM Leer configuración
for /f "usebackq tokens=1,2 delims==" %%a in ("%CONFIG_FILE%") do (
    set "%%a=%%b"
)

REM Validar variables
if "%SERVIDOR_IP%"=="" (
    echo ERROR: SERVIDOR_IP no esta configurado.
    pause
    exit /b 1
)
if "%SERVIDOR_USUARIO%"=="" (
    echo ERROR: SERVIDOR_USUARIO no esta configurado.
    pause
    exit /b 1
)

REM Variables
set FECHA_HORA=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set FECHA_HORA=!FECHA_HORA: =0!
set LOG_FILE=%LOGS_DIR%\nginx_config_%FECHA_HORA%.log
set ERROR_LOG=%LOGS_DIR%\nginx_config_error_%FECHA_HORA%.log

REM Crear directorio de logs si no existe
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo Log: %LOG_FILE%
echo.

REM Verificar conexión SSH
echo Verificando conexion SSH...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "echo 'Conexion OK'" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "echo 'Conexion OK'" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if errorlevel 1 (
    echo ERROR: No se pudo conectar al servidor.
    echo Verifique los logs: %ERROR_LOG%
    pause
    exit /b 1
)

echo Conexion establecida.
echo.

REM Crear script de configuración en el servidor
echo Creando script de configuracion en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > /tmp/config_nginx_gnv.sh << 'NGINX_SCRIPT'
#!/bin/bash
set -e

echo '============================================'
echo '  CONFIGURANDO NGINX PARA GNV'
echo '============================================'
echo

# Verificar que nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo 'ERROR: Nginx no esta instalado.'
    exit 1
fi

# Crear backup de configuración actual
BACKUP_DIR=/etc/nginx/backup_gnv_\$(date +%%Y%%m%%d_%%H%%M%%S)
mkdir -p \"\$BACKUP_DIR\"
echo \"Creando backup en: \$BACKUP_DIR\"

# Backup de configuraciones existentes
if [ -f /etc/nginx/sites-available/gnv.weldtech.cloud ]; then
    cp /etc/nginx/sites-available/gnv.weldtech.cloud \"\$BACKUP_DIR/\" 2>/dev/null || true
fi
if [ -f /etc/nginx/sites-enabled/gnv.weldtech.cloud ]; then
    cp /etc/nginx/sites-enabled/gnv.weldtech.cloud \"\$BACKUP_DIR/\" 2>/dev/null || true
fi

# Crear configuración para gnv.weldtech.cloud
echo 'Creando configuracion para gnv.weldtech.cloud...'
cat > /etc/nginx/sites-available/gnv.weldtech.cloud << 'NGINX_CONFIG'
# ============================================
# Configuración Nginx para aplicación GNV
# Solo debe responder a gnv.weldtech.cloud
# ============================================

# Configuración para la aplicación Streamlit (puerto 8501)
server {
    listen 80;
    server_name gnv.weldtech.cloud;  # SOLO este dominio
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}

# Configuración para la API (puerto 8000)
server {
    listen 80;
    server_name api-gnv.weldtech.cloud;  # SOLO este dominio para la API
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX_CONFIG

# Habilitar el sitio
echo 'Habilitando sitio...'
ln -sf /etc/nginx/sites-available/gnv.weldtech.cloud /etc/nginx/sites-enabled/

# Verificar que NO hay configuración incorrecta para weldtech.cloud
echo
echo 'Verificando configuraciones existentes...'
echo 'Configuraciones que contienen weldtech.cloud:'
grep -r \"server_name.*weldtech.cloud\" /etc/nginx/sites-available/ 2>/dev/null || echo '  (ninguna encontrada)'
echo

# Verificar configuración de nginx
echo 'Verificando configuracion de nginx...'
if nginx -t; then
    echo '✓ Configuracion valida'
else
    echo '✗ ERROR: Configuracion invalida'
    exit 1
fi

# Recargar nginx
echo
echo 'Recargando nginx...'
systemctl reload nginx || service nginx reload

echo
echo '============================================'
echo '  CONFIGURACION COMPLETADA'
echo '============================================'
echo
echo 'La aplicacion GNV ahora solo responde a:'
echo '  - http://gnv.weldtech.cloud'
echo '  - http://api-gnv.weldtech.cloud'
echo
echo 'IMPORTANTE: Verifique que weldtech.cloud'
echo '  apunte a otra aplicacion, NO a esta.'
echo
NGINX_SCRIPT
chmod +x /tmp/config_nginx_gnv.sh" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > /tmp/config_nginx_gnv.sh << 'NGINX_SCRIPT'
#!/bin/bash
set -e

echo '============================================'
echo '  CONFIGURANDO NGINX PARA GNV'
echo '============================================'
echo

# Verificar que nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo 'ERROR: Nginx no esta instalado.'
    exit 1
fi

# Crear backup de configuración actual
BACKUP_DIR=/etc/nginx/backup_gnv_\$(date +%%Y%%m%%d_%%H%%M%%S)
mkdir -p \"\$BACKUP_DIR\"
echo \"Creando backup en: \$BACKUP_DIR\"

# Backup de configuraciones existentes
if [ -f /etc/nginx/sites-available/gnv.weldtech.cloud ]; then
    cp /etc/nginx/sites-available/gnv.weldtech.cloud \"\$BACKUP_DIR/\" 2>/dev/null || true
fi
if [ -f /etc/nginx/sites-enabled/gnv.weldtech.cloud ]; then
    cp /etc/nginx/sites-enabled/gnv.weldtech.cloud \"\$BACKUP_DIR/\" 2>/dev/null || true
fi

# Crear configuración para gnv.weldtech.cloud
echo 'Creando configuracion para gnv.weldtech.cloud...'
cat > /etc/nginx/sites-available/gnv.weldtech.cloud << 'NGINX_CONFIG'
# ============================================
# Configuración Nginx para aplicación GNV
# Solo debe responder a gnv.weldtech.cloud
# ============================================

# Configuración para la aplicación Streamlit (puerto 8501)
server {
    listen 80;
    server_name gnv.weldtech.cloud;  # SOLO este dominio
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}

# Configuración para la API (puerto 8000)
server {
    listen 80;
    server_name api-gnv.weldtech.cloud;  # SOLO este dominio para la API
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX_CONFIG

# Habilitar el sitio
echo 'Habilitando sitio...'
ln -sf /etc/nginx/sites-available/gnv.weldtech.cloud /etc/nginx/sites-enabled/

# Verificar que NO hay configuración incorrecta para weldtech.cloud
echo
echo 'Verificando configuraciones existentes...'
echo 'Configuraciones que contienen weldtech.cloud:'
grep -r \"server_name.*weldtech.cloud\" /etc/nginx/sites-available/ 2>/dev/null || echo '  (ninguna encontrada)'
echo

# Verificar configuración de nginx
echo 'Verificando configuracion de nginx...'
if nginx -t; then
    echo '✓ Configuracion valida'
else
    echo '✗ ERROR: Configuracion invalida'
    exit 1
fi

# Recargar nginx
echo
echo 'Recargando nginx...'
systemctl reload nginx || service nginx reload

echo
echo '============================================'
echo '  CONFIGURACION COMPLETADA'
echo '============================================'
echo
echo 'La aplicacion GNV ahora solo responde a:'
echo '  - http://gnv.weldtech.cloud'
echo '  - http://api-gnv.weldtech.cloud'
echo
echo 'IMPORTANTE: Verifique que weldtech.cloud'
echo '  apunte a otra aplicacion, NO a esta.'
echo
NGINX_SCRIPT
chmod +x /tmp/config_nginx_gnv.sh" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)

REM Ejecutar el script
echo Ejecutando configuracion de nginx en el servidor...
echo.
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash /tmp/config_nginx_gnv.sh" 2>&1 | tee "%LOG_FILE%"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash /tmp/config_nginx_gnv.sh" 2>&1 | tee "%LOG_FILE%"
)

if errorlevel 1 (
    echo.
    echo ERROR: La configuracion fallo.
    echo Verifique los logs: %LOG_FILE%
    pause
    exit /b 1
)

echo.
echo ============================================
echo   CONFIGURACION COMPLETADA
echo ============================================
echo.
echo Log completo: %LOG_FILE%
echo.
echo La aplicacion GNV ahora solo responde a:
echo   - http://gnv.weldtech.cloud
echo   - http://api-gnv.weldtech.cloud
echo.
echo IMPORTANTE: Verifique que weldtech.cloud
echo   apunte a otra aplicacion, NO a esta.
echo.

pause
