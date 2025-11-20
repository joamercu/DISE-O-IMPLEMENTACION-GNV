@echo off
REM ============================================
REM Script para configurar Nginx con HTTPS
REM Solo gnv.weldtech.cloud debe apuntar a esta app
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   CONFIGURAR NGINX CON HTTPS PARA GNV
echo ============================================
echo.
echo IMPORTANTE: Este script configura HTTPS
echo Necesitas tener certificados SSL configurados.
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

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo.

REM Preguntar sobre certificados SSL
echo ============================================
echo   CONFIGURACION DE CERTIFICADOS SSL
echo ============================================
echo.
echo Donde estan ubicados los certificados SSL?
echo.
echo 1. Let's Encrypt (recomendado)
echo 2. Certificados personalizados en /etc/ssl/
echo 3. Solo HTTP (sin HTTPS)
echo.
set /p SSL_OPCION="Seleccione opcion (1/2/3): "

if "%SSL_OPCION%"=="3" (
    echo.
    echo Configurando solo HTTP...
    call "%~dp0configurar_nginx.bat"
    exit /b 0
)

REM Crear script de configuración en el servidor
echo.
echo Creando script de configuracion en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > /tmp/config_nginx_https_gnv.sh << 'NGINX_SCRIPT'
#!/bin/bash
set -e

SSL_OPCION=%SSL_OPCION%

echo '============================================'
echo '  CONFIGURANDO NGINX CON HTTPS PARA GNV'
echo '============================================'
echo

# Verificar que nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo 'ERROR: Nginx no esta instalado.'
    exit 1
fi

# Crear backup
BACKUP_DIR=/etc/nginx/backup_gnv_\$(date +%%Y%%m%%d_%%H%%M%%S)
mkdir -p \"\$BACKUP_DIR\"
echo \"Creando backup en: \$BACKUP_DIR\"

# Backup de configuraciones existentes
if [ -f /etc/nginx/sites-available/gnv.weldtech.cloud ]; then
    cp /etc/nginx/sites-available/gnv.weldtech.cloud \"\$BACKUP_DIR/\" 2>/dev/null || true
fi

# Determinar rutas de certificados
if [ \"\$SSL_OPCION\" == \"1\" ]; then
    # Let's Encrypt
    SSL_CERT=\"/etc/letsencrypt/live/gnv.weldtech.cloud/fullchain.pem\"
    SSL_KEY=\"/etc/letsencrypt/live/gnv.weldtech.cloud/privkey.pem\"
    API_SSL_CERT=\"/etc/letsencrypt/live/api-gnv.weldtech.cloud/fullchain.pem\"
    API_SSL_KEY=\"/etc/letsencrypt/live/api-gnv.weldtech.cloud/privkey.pem\"
    
    # Verificar si existen
    if [ ! -f \"\$SSL_CERT\" ]; then
        echo \"ADVERTENCIA: Certificado no encontrado en \$SSL_CERT\"
        echo \"Si usas Let's Encrypt, ejecuta primero:\"
        echo \"  certbot certonly --nginx -d gnv.weldtech.cloud\"
        echo
        read -p \"Continuar de todas formas? (s/N): \" CONTINUAR
        if [ \"\$CONTINUAR\" != \"s\" ] && [ \"\$CONTINUAR\" != \"S\" ]; then
            exit 1
        fi
    fi
else
    # Certificados personalizados
    SSL_CERT=\"/etc/ssl/certs/gnv.weldtech.cloud.crt\"
    SSL_KEY=\"/etc/ssl/private/gnv.weldtech.cloud.key\"
    API_SSL_CERT=\"/etc/ssl/certs/api-gnv.weldtech.cloud.crt\"
    API_SSL_KEY=\"/etc/ssl/private/api-gnv.weldtech.cloud.key\"
fi

# Crear configuración
echo 'Creando configuracion para gnv.weldtech.cloud...'
cat > /etc/nginx/sites-available/gnv.weldtech.cloud << NGINX_CONFIG
# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name gnv.weldtech.cloud;
    return 301 https://\$server_name\$request_uri;
}

# Configuración para la aplicación Streamlit (puerto 8501) - HTTPS
server {
    listen 443 ssl http2;
    server_name gnv.weldtech.cloud;  # SOLO este dominio
    
    # Configuración SSL
    ssl_certificate \$SSL_CERT;
    ssl_certificate_key \$SSL_KEY;
    
    # Configuración SSL recomendada
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
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

# Redirigir HTTP a HTTPS para API
server {
    listen 80;
    server_name api-gnv.weldtech.cloud;
    return 301 https://\$server_name\$request_uri;
}

# Configuración para la API (puerto 8000) - HTTPS
server {
    listen 443 ssl http2;
    server_name api-gnv.weldtech.cloud;  # SOLO este dominio para la API
    
    # Configuración SSL
    ssl_certificate \$API_SSL_CERT;
    ssl_certificate_key \$API_SSL_KEY;
    
    # Configuración SSL recomendada
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
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
ln -sf /etc/nginx/sites-available/gnv.weldtech.cloud /etc/nginx/sites-enabled/

# Verificar configuración
echo 'Verificando configuracion...'
if nginx -t; then
    echo '✓ Configuracion valida'
else
    echo '✗ ERROR: Configuracion invalida'
    exit 1
fi

# Recargar nginx
echo 'Recargando nginx...'
systemctl reload nginx || service nginx reload

echo
echo '============================================'
echo '  CONFIGURACION COMPLETADA'
echo '============================================'
echo
echo '✓ La aplicacion GNV ahora responde a:'
echo '  - https://gnv.weldtech.cloud'
echo '  - https://api-gnv.weldtech.cloud'
echo
echo 'HTTP sera redirigido automaticamente a HTTPS'
echo
NGINX_SCRIPT
chmod +x /tmp/config_nginx_https_gnv.sh" >> "%TEMP%\nginx_config.log" 2>&1
) else (
    echo ERROR: No se pudo crear el script en el servidor.
    pause
    exit /b 1
)

REM Ejecutar el script
echo Ejecutando configuracion...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "SSL_OPCION=%SSL_OPCION% bash /tmp/config_nginx_https_gnv.sh"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "SSL_OPCION=%SSL_OPCION% bash /tmp/config_nginx_https_gnv.sh"
)

if errorlevel 1 (
    echo.
    echo ERROR: La configuracion fallo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   CONFIGURACION COMPLETADA
echo ============================================
echo.
echo La aplicacion GNV ahora responde a:
echo   - https://gnv.weldtech.cloud
echo   - https://api-gnv.weldtech.cloud
echo.
echo HTTP sera redirigido automaticamente a HTTPS
echo.

pause

