@echo off
REM ============================================
REM Script para corregir advertencia de HTTP/2
REM en configuración de Nginx
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   CORRECCION DE ADVERTENCIA HTTP/2 NGINX
echo ============================================
echo.
echo Este script corrige la advertencia sobre
echo la directiva deprecated "listen ... http2"
echo en la configuracion de Nginx.
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

REM Limpiar espacios en blanco de las variables
set "SERVIDOR_IP=%SERVIDOR_IP: =%"
set "SERVIDOR_USUARIO=%SERVIDOR_USUARIO: =%"
set "SSH_KEY=%SSH_KEY: =%"

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

REM Crear script temporal para corregir Nginx
set TEMP_SCRIPT=/tmp/corregir_nginx_http2.sh

echo ============================================
echo   CREANDO SCRIPT DE CORRECCION
echo ============================================
echo.

(
echo #!/bin/bash
echo # Script para corregir advertencia HTTP/2 en Nginx
echo.
echo set -e
echo.
echo NGINX_CONFIG="/etc/nginx/sites-available/gnv-app"
echo BACKUP_FILE="/etc/nginx/sites-available/gnv-app.backup.$(date +%%Y%%m%%d_%%H%%M%%S)"
echo.
echo echo "Corrigiendo configuracion de Nginx..."
echo echo "Archivo: $NGINX_CONFIG"
echo echo "Backup: $BACKUP_FILE"
echo.
echo # Crear backup
echo cp "$NGINX_CONFIG" "$BACKUP_FILE"
echo echo "✓ Backup creado: $BACKUP_FILE"
echo.
echo # Corregir sintaxis HTTP/2
echo # Cambiar "listen 443 ssl http2;" por "listen 443 ssl;" y agregar "http2 on;"
echo sed -i 's/listen 443 ssl http2;/listen 443 ssl;/g' "$NGINX_CONFIG"
echo.
echo # Agregar "http2 on;" después de cada "listen 443 ssl;"
echo # Primero, verificar si ya existe "http2 on;" en el bloque server
echo if ! grep -q "http2 on;" "$NGINX_CONFIG"; then
echo     # Agregar "http2 on;" después de "listen 443 ssl;" en cada bloque server
echo     sed -i '/listen 443 ssl;/a\    http2 on;' "$NGINX_CONFIG"
echo     echo "✓ Directiva http2 on; agregada"
echo else
echo     echo "⚠ http2 on; ya existe en la configuracion"
echo fi
echo.
echo # Verificar sintaxis
echo echo.
echo echo "Verificando sintaxis de Nginx..."
echo if nginx -t; then
echo     echo "✓ Configuracion valida"
echo     echo.
echo     echo "¿Desea aplicar los cambios ahora? (s/n)"
echo     read -r respuesta
echo     if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
echo         systemctl reload nginx
echo         echo "✓ Nginx recargado exitosamente"
echo     else
echo         echo "Cambios guardados pero no aplicados."
echo         echo "Para aplicar: systemctl reload nginx"
echo     fi
echo else
echo     echo "✗ ERROR: Configuracion invalida. Restaurando backup..."
echo     cp "$BACKUP_FILE" "$NGINX_CONFIG"
echo     exit 1
echo fi
) > "%TEMP%\corregir_nginx_http2.sh"

echo Script temporal creado.
echo.

REM Subir script al servidor
echo ============================================
echo   SUBIENDO SCRIPT AL SERVIDOR
echo ============================================
echo.

if exist "%SSH_KEY%" (
    scp -i "%SSH_KEY%" "%TEMP%\corregir_nginx_http2.sh" %SERVIDOR_USUARIO%@%SERVIDOR_IP%:%TEMP_SCRIPT% >nul 2>&1
) else (
    scp "%TEMP%\corregir_nginx_http2.sh" %SERVIDOR_USUARIO%@%SERVIDOR_IP%:%TEMP_SCRIPT% >nul 2>&1
)

if errorlevel 1 (
    echo ERROR: No se pudo subir el script al servidor.
    echo Verifique la conexion SSH.
    del "%TEMP%\corregir_nginx_http2.sh" >nul 2>&1
    pause
    exit /b 1
)

echo Script subido correctamente.
echo.

REM Dar permisos de ejecución
echo Dando permisos de ejecucion...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "chmod +x %TEMP_SCRIPT%" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "chmod +x %TEMP_SCRIPT%" >nul 2>&1
)

echo.
echo ============================================
echo   EJECUTANDO CORRECCION
echo ============================================
echo.

REM Ejecutar script
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash %TEMP_SCRIPT%"
) else (
    ssh -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash %TEMP_SCRIPT%"
)

if errorlevel 1 (
    echo.
    echo ERROR: La correccion fallo.
    del "%TEMP%\corregir_nginx_http2.sh" >nul 2>&1
    pause
    exit /b 1
)

echo.
echo ============================================
echo   LIMPIEZA
echo ============================================
echo.

REM Limpiar archivos temporales
del "%TEMP%\corregir_nginx_http2.sh" >nul 2>&1

if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "rm -f %TEMP_SCRIPT%" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "rm -f %TEMP_SCRIPT%" >nul 2>&1
)

echo.
echo ============================================
echo   CORRECCION COMPLETADA
echo ============================================
echo.
echo La advertencia de HTTP/2 deberia estar
echo corregida. Verifique con:
echo   ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "nginx -t"
echo.
pause

