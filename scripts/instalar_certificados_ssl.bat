@echo off
REM ============================================
REM Script para instalar/renovar certificados SSL
REM Usa Let's Encrypt (certbot) para todos los dominios
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   INSTALAR/RENOVAR CERTIFICADOS SSL
echo ============================================
echo.
echo Este script instala o renueva certificados SSL
echo usando Let's Encrypt para todos los dominios.
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

REM Preguntar email para Let's Encrypt
echo ============================================
echo   CONFIGURACION DE LET'S ENCRYPT
echo ============================================
echo.
echo Necesita un email para recibir notificaciones
echo sobre la renovacion de certificados.
set /p CERT_EMAIL="Email (Enter para omitir): "
echo.

REM Crear script de instalación en el servidor
echo Creando script de instalacion en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > /tmp/instalar_certificados.sh << 'CERT_SCRIPT'
#!/bin/bash
set -e

CERT_EMAIL=%CERT_EMAIL%

echo '============================================'
echo '  INSTALANDO/RENOVANDO CERTIFICADOS SSL'
echo '============================================'
echo

# Verificar que se ejecuta como root
if [ \"\$EUID\" -ne 0 ]; then 
    echo \"ERROR: Este script debe ejecutarse como root\"
    echo \"Use: sudo bash \$0\"
    exit 1
fi

# Instalar certbot si no está instalado
if ! command -v certbot &> /dev/null; then
    echo \"Instalando certbot...\"
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
    echo \"✓ Certbot instalado\"
else
    echo \"✓ Certbot ya esta instalado\"
fi

echo
echo \"============================================\"
echo \"  DOMINIOS A CONFIGURAR\"
echo \"============================================\"
echo
echo \"Los siguientes dominios seran configurados:\"
echo \"  1. weldtech.cloud (aplicacion de login)\"
echo \"  2. gnv.weldtech.cloud (aplicacion Streamlit)\"
echo \"  3. api-gnv.weldtech.cloud (API)\"
echo

# Preparar email para certbot
EMAIL_OPT=\"\"
if [ -n \"\$CERT_EMAIL\" ]; then
    EMAIL_OPT=\"--email \$CERT_EMAIL --agree-tos --no-eff-email\"
else
    EMAIL_OPT=\"--register-unsafely-without-email --agree-tos\"
fi

# Instalar certificados para cada dominio
DOMINIOS=(\"weldtech.cloud\" \"gnv.weldtech.cloud\" \"api-gnv.weldtech.cloud\")

for DOMINIO in \"\${DOMINIOS[@]}\"; do
    echo
    echo \"============================================\"
    echo \"  Configurando: \$DOMINIO\"
    echo \"============================================\"
    echo
    
    CERT_PATH=\"/etc/letsencrypt/live/\$DOMINIO/fullchain.pem\"
    
    if [ -f \"\$CERT_PATH\" ]; then
        echo \"✓ Certificado ya existe para \$DOMINIO\"
        echo \"  Verificando fecha de expiracion...\"
        EXPIRY=\$(openssl x509 -in \"\$CERT_PATH\" -noout -enddate 2>/dev/null | cut -d= -f2)
        echo \"  Expira: \$EXPIRY\"
        echo
        echo \"¿Desea renovar este certificado? (s/N)\"
        read -p \"Respuesta: \" RENOVAR
        
        if [ \"\$RENOVAR\" == \"s\" ] || [ \"\$RENOVAR\" == \"S\" ]; then
            echo \"Renovando certificado para \$DOMINIO...\"
            certbot renew --cert-name \$DOMINIO --force-renewal
            echo \"✓ Certificado renovado\"
        else
            echo \"Saltando renovacion de \$DOMINIO\"
        fi
    else
        echo \"Instalando certificado para \$DOMINIO...\"
        echo \"Esto puede tomar unos minutos...\"
        
        # Intentar obtener certificado con nginx
        if certbot certonly --nginx -d \$DOMINIO \$EMAIL_OPT --non-interactive; then
            echo \"✓ Certificado instalado para \$DOMINIO\"
        else
            echo \"⚠ No se pudo instalar automaticamente con nginx\"
            echo \"Intentando metodo standalone...\"
            
            # Detener nginx temporalmente si es necesario
            if systemctl is-active --quiet nginx; then
                echo \"Deteniendo nginx temporalmente...\"
                systemctl stop nginx
                NGINX_STOPPED=true
            fi
            
            if certbot certonly --standalone -d \$DOMINIO \$EMAIL_OPT --non-interactive; then
                echo \"✓ Certificado instalado para \$DOMINIO\"
            else
                echo \"✗ ERROR: No se pudo instalar certificado para \$DOMINIO\"
                echo \"Verifique que el dominio apunte a este servidor.\"
            fi
            
            # Reiniciar nginx si se detuvo
            if [ \"\$NGINX_STOPPED\" == \"true\" ]; then
                echo \"Reiniciando nginx...\"
                systemctl start nginx
            fi
        fi
    fi
done

echo
echo \"============================================\"
echo \"  VERIFICANDO CERTIFICADOS\"
echo \"============================================\"
echo

# Verificar todos los certificados
for DOMINIO in \"\${DOMINIOS[@]}\"; do
    CERT_PATH=\"/etc/letsencrypt/live/\$DOMINIO/fullchain.pem\"
    
    if [ -f \"\$CERT_PATH\" ]; then
        echo \"✓ \$DOMINIO\"
        echo \"  Certificado: \$CERT_PATH\"
        EXPIRY=\$(openssl x509 -in \"\$CERT_PATH\" -noout -enddate 2>/dev/null | cut -d= -f2)
        echo \"  Expira: \$EXPIRY\"
    else
        echo \"✗ \$DOMINIO - Certificado no encontrado\"
    fi
    echo
done

# Configurar renovación automática
echo \"============================================\"
echo \"  CONFIGURANDO RENOVACION AUTOMATICA\"
echo \"============================================\"
echo

# Verificar si ya existe el timer de systemd
if systemctl list-timers | grep -q certbot.timer; then
    echo \"✓ Timer de renovacion automatica ya esta configurado\"
else
    echo \"Configurando renovacion automatica...\"
    systemctl enable certbot.timer
    systemctl start certbot.timer
    echo \"✓ Renovacion automatica configurada\"
fi

# Mostrar estado del timer
echo
echo \"Estado del timer de renovacion:\"
systemctl status certbot.timer --no-pager -l | head -n 10

echo
echo \"============================================\"
echo \"  INSTALACION COMPLETADA\"
echo \"============================================\"
echo
echo \"Los certificados SSL han sido instalados/renovados.\"
echo \"Recuerde actualizar las configuraciones de nginx\"
echo \"para usar estos certificados.\"
echo
CERT_SCRIPT
chmod +x /tmp/instalar_certificados.sh" >> "%TEMP%\instalar_cert.log" 2>&1
) else (
    echo ERROR: No se pudo crear el script en el servidor.
    pause
    exit /b 1
)

REM Ejecutar el script
echo Ejecutando instalacion de certificados...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "sudo CERT_EMAIL=%CERT_EMAIL% bash /tmp/instalar_certificados.sh"
) else (
    ssh -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "sudo CERT_EMAIL=%CERT_EMAIL% bash /tmp/instalar_certificados.sh"
)

if errorlevel 1 (
    echo.
    echo ERROR: La instalacion fallo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   INSTALACION COMPLETADA
echo ============================================
echo.
echo Los certificados SSL han sido instalados/renovados.
echo.
echo IMPORTANTE: Ahora debe ejecutar:
echo   1. configurar_nginx_https.bat (para gnv.weldtech.cloud)
echo   2. configurar_weldtech_cloud.bat (para weldtech.cloud)
echo.

pause

