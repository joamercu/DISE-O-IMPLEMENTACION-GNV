@echo off
REM ============================================
REM Script para configurar weldtech.cloud
REM Apunta a aplicación de login (NO a Streamlit)
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   CONFIGURAR WELDTECH.CLOUD
echo ============================================
echo.
echo Este script configura weldtech.cloud para
echo apuntar a la aplicacion de login.
echo.
echo IMPORTANTE: Esta configuracion es diferente
echo de gnv.weldtech.cloud que apunta a Streamlit.
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

REM Preguntar puerto de la aplicación de login
echo ============================================
echo   CONFIGURACION DE APLICACION DE LOGIN
echo ============================================
echo.
echo En que puerto esta corriendo la aplicacion de login?
echo (Por defecto: 3000)
set /p LOGIN_PORT="Puerto (Enter para 3000): "
if "%LOGIN_PORT%"=="" set LOGIN_PORT=3000
echo.
echo Puerto configurado: %LOGIN_PORT%
echo.

REM Crear script de configuración en el servidor
echo Creando script de configuracion en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > /tmp/config_weldtech_cloud.sh << 'NGINX_SCRIPT'
#!/bin/bash
set -e

LOGIN_PORT=%LOGIN_PORT%

echo '============================================'
echo '  CONFIGURANDO WELDTECH.CLOUD'
echo '============================================'
echo

# Verificar que se ejecuta como root
if [ \"\$EUID\" -ne 0 ]; then 
    echo \"ERROR: Este script debe ejecutarse como root\"
    echo \"Use: sudo bash \$0\"
    exit 1
fi

# Verificar que nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo \"ERROR: Nginx no esta instalado.\"
    exit 1
fi

# Crear backup
BACKUP_DIR=/etc/nginx/backup_weldtech_\$(date +%%Y%%m%%d_%%H%%M%%S)
mkdir -p \"\$BACKUP_DIR\"
echo \"Creando backup en: \$BACKUP_DIR\"

# Backup de configuraciones existentes
if [ -f /etc/nginx/sites-available/weldtech.cloud ]; then
    cp /etc/nginx/sites-available/weldtech.cloud \"\$BACKUP_DIR/\" 2>/dev/null || true
fi

# Determinar rutas de certificados SSL
# Intentar Let's Encrypt primero
SSL_CERT=\"/etc/letsencrypt/live/weldtech.cloud/fullchain.pem\"
SSL_KEY=\"/etc/letsencrypt/live/weldtech.cloud/privkey.pem\"

if [ ! -f \"\$SSL_CERT\" ]; then
    echo \"⚠ ADVERTENCIA: Certificado Let's Encrypt no encontrado\"
    echo \"  Ruta esperada: \$SSL_CERT\"
    echo \"  Si necesita crear el certificado, ejecute:\"
    echo \"  certbot certonly --nginx -d weldtech.cloud\"
    echo
    echo \"¿Desea continuar sin HTTPS? (s/N)\"
    read -p \"Respuesta: \" CONTINUAR
    if [ \"\$CONTINUAR\" != \"s\" ] && [ \"\$CONTINUAR\" != \"S\" ]; then
        exit 1
    fi
    SSL_CERT=\"\"
    SSL_KEY=\"\"
fi

# Crear configuración
echo 'Creando configuracion para weldtech.cloud...'

# Crear archivo completo con placeholder para el puerto
cat > /tmp/weldtech_nginx_config.txt << 'NGINX_TEMP'
# ============================================
# Configuración Nginx para weldtech.cloud
# Aplicación de login (NO Streamlit)
# ============================================

# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name weldtech.cloud www.weldtech.cloud;
    return 301 https://$server_name$request_uri;
}

# Configuración HTTPS
server {
    listen 443 ssl http2;
    server_name weldtech.cloud www.weldtech.cloud;
    
    # Configuración SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/weldtech.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/weldtech.cloud/privkey.pem;
    
    # Configuración SSL recomendada
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Headers de seguridad
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    
    location / {
        proxy_pass http://127.0.0.1:LOGIN_PORT_PLACEHOLDER;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    location /auth/login {
        proxy_pass http://127.0.0.1:LOGIN_PORT_PLACEHOLDER/auth/login;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_TEMP

# Reemplazar placeholder con puerto real y crear archivo final
sed \"s/LOGIN_PORT_PLACEHOLDER/\$LOGIN_PORT/g\" /tmp/weldtech_nginx_config.txt > /etc/nginx/sites-available/weldtech.cloud
rm /tmp/weldtech_nginx_config.txt

# Habilitar el sitio
ln -sf /etc/nginx/sites-available/weldtech.cloud /etc/nginx/sites-enabled/

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
echo '✓ weldtech.cloud ahora apunta a:'
echo '  - http://127.0.0.1:'\$LOGIN_PORT
echo '  - Aplicacion de login (NO Streamlit)'
echo
NGINX_SCRIPT
chmod +x /tmp/config_weldtech_cloud.sh" >> "%TEMP%\weldtech_config.log" 2>&1
) else (
    echo ERROR: No se pudo crear el script en el servidor.
    pause
    exit /b 1
)

REM Ejecutar el script
echo Ejecutando configuracion...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "sudo LOGIN_PORT=%LOGIN_PORT% bash /tmp/config_weldtech_cloud.sh"
) else (
    ssh -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "sudo LOGIN_PORT=%LOGIN_PORT% bash /tmp/config_weldtech_cloud.sh"
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
echo weldtech.cloud ahora apunta a la aplicacion de login.
echo.
echo IMPORTANTE: Verifique que gnv.weldtech.cloud
echo apunte SOLO a Streamlit (puerto 8501).
echo.

pause

