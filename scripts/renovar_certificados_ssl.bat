@echo off
REM ============================================
REM Script para renovar certificados SSL
REM Usa Let's Encrypt (certbot) para renovar
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   RENOVAR CERTIFICADOS SSL
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

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo.

REM Crear script de renovación en el servidor
echo Creando script de renovacion en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > /tmp/renovar_certificados.sh << 'RENOVAR_SCRIPT'
#!/bin/bash
set -e

echo '============================================'
echo '  RENOVANDO CERTIFICADOS SSL'
echo '============================================'
echo

# Verificar que se ejecuta como root
if [ \"\$EUID\" -ne 0 ]; then 
    echo \"ERROR: Este script debe ejecutarse como root\"
    echo \"Use: sudo bash \$0\"
    exit 1
fi

# Verificar que certbot está instalado
if ! command -v certbot &> /dev/null; then
    echo \"ERROR: Certbot no esta instalado.\"
    echo \"Instalando certbot...\"
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

echo \"Verificando certificados existentes...\"
echo

# Listar certificados existentes
certbot certificates

echo
echo \"============================================\"
echo \"  RENOVANDO CERTIFICADOS\"
echo \"============================================\"
echo

# Renovar todos los certificados
echo \"Renovando todos los certificados...\"
certbot renew --dry-run

if [ \$? -eq 0 ]; then
    echo
    echo \"✓ Prueba de renovacion exitosa\"
    echo
    echo \"¿Desea renovar los certificados ahora? (s/N)\"
    read -p \"Respuesta: \" RENOVAR
    
    if [ \"\$RENOVAR\" == \"s\" ] || [ \"\$RENOVAR\" == \"S\" ]; then
        echo
        echo \"Renovando certificados...\"
        certbot renew --force-renewal
        
        if [ \$? -eq 0 ]; then
            echo
            echo \"✓ Certificados renovados exitosamente\"
            echo
            echo \"Recargando nginx...\"
            systemctl reload nginx || service nginx reload
            echo \"✓ Nginx recargado\"
        else
            echo
            echo \"✗ ERROR: No se pudieron renovar los certificados\"
            exit 1
        fi
    else
        echo
        echo \"Renovacion cancelada. Los certificados no fueron renovados.\"
    fi
else
    echo
    echo \"✗ ERROR: La prueba de renovacion fallo\"
    echo \"Verifique la configuracion de los certificados.\"
    exit 1
fi

echo
echo \"============================================\"
echo \"  VERIFICANDO CERTIFICADOS\"
echo \"============================================\"
echo

# Verificar certificados específicos
DOMINIOS=(\"weldtech.cloud\" \"gnv.weldtech.cloud\" \"api-gnv.weldtech.cloud\")

for DOMINIO in \"\${DOMINIOS[@]}\"; do
    echo \"Verificando certificado para \$DOMINIO...\"
    CERT_PATH=\"/etc/letsencrypt/live/\$DOMINIO/fullchain.pem\"
    
    if [ -f \"\$CERT_PATH\" ]; then
        echo \"  ✓ Certificado encontrado: \$CERT_PATH\"
        echo \"  Fecha de expiracion:\"
        openssl x509 -in \"\$CERT_PATH\" -noout -enddate 2>/dev/null || echo \"    (no se pudo leer)\"
    else
        echo \"  ⚠ Certificado no encontrado: \$CERT_PATH\"
        echo \"    Si necesita crear este certificado, ejecute:\"
        echo \"    certbot certonly --nginx -d \$DOMINIO\"
    fi
    echo
done

echo \"============================================\"
echo \"  RENOVACION COMPLETADA\"
echo \"============================================\"
echo
RENOVAR_SCRIPT
chmod +x /tmp/renovar_certificados.sh" >> "%TEMP%\renovar_cert.log" 2>&1
) else (
    echo ERROR: No se pudo crear el script en el servidor.
    pause
    exit /b 1
)

REM Ejecutar el script
echo Ejecutando renovacion de certificados...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "sudo bash /tmp/renovar_certificados.sh"
) else (
    ssh -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "sudo bash /tmp/renovar_certificados.sh"
)

if errorlevel 1 (
    echo.
    echo ERROR: La renovacion fallo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   RENOVACION COMPLETADA
echo ============================================
echo.
echo Los certificados SSL han sido renovados.
echo.

pause

