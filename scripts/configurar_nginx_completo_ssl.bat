@echo off
REM ============================================
REM Script completo para configurar nginx con SSL
REM Configura ambos dominios correctamente
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   CONFIGURACION COMPLETA NGINX CON SSL
echo ============================================
echo.
echo Este script configura nginx para:
echo   - weldtech.cloud (aplicacion de login)
echo   - gnv.weldtech.cloud (aplicacion Streamlit)
echo   - api-gnv.weldtech.cloud (API)
echo.
echo Todos con HTTPS usando Let's Encrypt.
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

REM Crear script de configuración completo en el servidor
echo Creando script de configuracion completa en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > /tmp/config_nginx_completo_ssl.sh << 'NGINX_SCRIPT'
#!/bin/bash
set -e

LOGIN_PORT=%LOGIN_PORT%

echo '============================================'
echo '  CONFIGURANDO NGINX COMPLETO CON SSL'
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
BACKUP_DIR=/etc/nginx/backup_completo_\$(date +%%Y%%m%%d_%%H%%M%%S)
mkdir -p \"\$BACKUP_DIR\"
echo \"Creando backup en: \$BACKUP_DIR\"

# Backup de todas las configuraciones
cp -r /etc/nginx/sites-available/* \"\$BACKUP_DIR/\" 2>/dev/null || true
cp -r /etc/nginx/sites-enabled/* \"\$BACKUP_DIR/\" 2>/dev/null || true

echo
echo \"============================================\"
echo \"  1. CONFIGURANDO WELDTECH.CLOUD\"
echo \"============================================\"
echo

# Configuración para weldtech.cloud
cat > /etc/nginx/sites-available/weldtech.cloud << 'WELDTECH_CONFIG'
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
WELDTECH_CONFIG

# Reemplazar placeholder con puerto real
sed -i \"s/LOGIN_PORT_PLACEHOLDER/\$LOGIN_PORT/g\" /etc/nginx/sites-available/weldtech.cloud

echo \"  ✓ Configuracion creada para weldtech.cloud\"

echo
echo \"============================================\"
echo \"  2. CONFIGURANDO GNV.WELDTECH.CLOUD\"
echo \"============================================\"
echo

# Configuración para gnv.weldtech.cloud
cat > /etc/nginx/sites-available/gnv.weldtech.cloud << 'GNV_CONFIG'
# ============================================
# Configuración Nginx para aplicación GNV
# Solo debe responder a gnv.weldtech.cloud
# ============================================

# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name gnv.weldtech.cloud;
    return 301 https://$server_name$request_uri;
}

# Configuración para la aplicación Streamlit (puerto 8501) - HTTPS
server {
    listen 443 ssl http2;
    server_name gnv.weldtech.cloud;  # SOLO este dominio
    
    # Configuración SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/gnv.weldtech.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gnv.weldtech.cloud/privkey.pem;
    
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
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}

# Redirigir HTTP a HTTPS para API
server {
    listen 80;
    server_name api-gnv.weldtech.cloud;
    return 301 https://$server_name$request_uri;
}

# Configuración para la API (puerto 8000) - HTTPS
server {
    listen 443 ssl http2;
    server_name api-gnv.weldtech.cloud;  # SOLO este dominio para la API
    
    # Configuración SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api-gnv.weldtech.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api-gnv.weldtech.cloud/privkey.pem;
    
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
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
GNV_CONFIG

echo \"  ✓ Configuracion creada para gnv.weldtech.cloud\"

# Habilitar los sitios
echo
echo \"Habilitando sitios...\"
ln -sf /etc/nginx/sites-available/weldtech.cloud /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/gnv.weldtech.cloud /etc/nginx/sites-enabled/
echo \"  ✓ Sitios habilitados\"

# Verificar configuración
echo
echo \"Verificando configuracion...\"
if nginx -t; then
    echo \"  ✓ Configuracion valida\"
else
    echo \"  ✗ ERROR: Configuracion invalida\"
    echo
    echo \"Revise los errores arriba.\"
    exit 1
fi

# Recargar nginx
echo
echo \"Recargando nginx...\"
systemctl reload nginx || service nginx reload
echo \"  ✓ Nginx recargado\"

echo
echo \"============================================\"
echo \"  CONFIGURACION COMPLETADA\"
echo \"============================================\"
echo
echo \"✓ Configuraciones creadas:\"
echo \"  - weldtech.cloud -> http://127.0.0.1:\$LOGIN_PORT (login)\"
echo \"  - gnv.weldtech.cloud -> http://127.0.0.1:8501 (Streamlit)\"
echo \"  - api-gnv.weldtech.cloud -> http://127.0.0.1:8000 (API)\"
echo
echo \"✓ Todos los dominios usan HTTPS con Let's Encrypt\"
echo \"✓ HTTP se redirige automaticamente a HTTPS\"
echo
echo \"Backup guardado en: \$BACKUP_DIR\"
echo
NGINX_SCRIPT
chmod +x /tmp/config_nginx_completo_ssl.sh" >> "%TEMP%\nginx_completo.log" 2>&1
) else (
    echo ERROR: No se pudo crear el script en el servidor.
    pause
    exit /b 1
)

REM Ejecutar el script
echo Ejecutando configuracion completa...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "sudo LOGIN_PORT=%LOGIN_PORT% bash /tmp/config_nginx_completo_ssl.sh"
) else (
    ssh -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "sudo LOGIN_PORT=%LOGIN_PORT% bash /tmp/config_nginx_completo_ssl.sh"
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
echo Todos los dominios han sido configurados correctamente.
echo.
echo IMPORTANTE: Verifique que los certificados SSL
echo esten instalados antes de usar estos dominios.
echo.

pause

