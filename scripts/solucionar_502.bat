@echo off
REM ============================================
REM Script para solucionar error 502 Bad Gateway
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   SOLUCIONAR ERROR 502 BAD GATEWAY
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

REM Paso 1: Verificar si Streamlit está corriendo
echo [1/4] Verificando si Streamlit esta corriendo...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null" >nul 2>&1
)

if errorlevel 1 (
    echo   ✗ Streamlit NO esta corriendo
    echo.
    echo   Iniciando Streamlit...
    call "%~dp0iniciar_app_servidor.bat"
    if errorlevel 1 (
        echo   ERROR: No se pudo iniciar Streamlit
        pause
        exit /b 1
    )
    timeout /t 5 >nul
) else (
    echo   ✓ Streamlit esta corriendo
)

echo.

REM Paso 2: Verificar puerto 8501
echo [2/4] Verificando puerto 8501...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null" >nul 2>&1
)

if errorlevel 1 (
    echo   ✗ Puerto 8501 NO esta en uso
    echo   Esto puede indicar que Streamlit no se inicio correctamente
    echo   Revise los logs: scripts\ver_logs_servidor.bat
    pause
    exit /b 1
) else (
    echo   ✓ Puerto 8501 esta en uso
)

echo.

REM Paso 3: Verificar configuración de nginx
echo [3/4] Verificando configuracion de nginx...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "test -f /etc/nginx/sites-available/gnv.weldtech.cloud" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "test -f /etc/nginx/sites-available/gnv.weldtech.cloud" >nul 2>&1
)

if errorlevel 1 (
    echo   ✗ Configuracion de nginx no encontrada
    echo   Configurando nginx...
    call "%~dp0configurar_nginx.bat"
    if errorlevel 1 (
        echo   ERROR: No se pudo configurar nginx
        pause
        exit /b 1
    )
) else (
    echo   ✓ Configuracion de nginx encontrada
)

echo.

REM Paso 4: Verificar si necesita HTTPS
echo [4/4] Verificando configuracion HTTPS...
echo.
echo IMPORTANTE: Si accede por HTTPS (https://gnv.weldtech.cloud)
echo pero nginx solo tiene HTTP configurado, necesita:
echo.
echo   1. Configurar certificados SSL
echo   2. Ejecutar: scripts\configurar_nginx_https.bat
echo.
echo O acceda por HTTP: http://gnv.weldtech.cloud
echo.

REM Verificar si nginx tiene HTTPS configurado
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "grep -q 'listen 443' /etc/nginx/sites-available/gnv.weldtech.cloud 2>/dev/null" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "grep -q 'listen 443' /etc/nginx/sites-available/gnv.weldtech.cloud 2>/dev/null" >nul 2>&1
)

if errorlevel 1 (
    echo   ⚠ Nginx NO tiene HTTPS configurado
    echo   Si necesita HTTPS, ejecute: scripts\configurar_nginx_https.bat
) else (
    echo   ✓ Nginx tiene HTTPS configurado
)

echo.
echo ============================================
echo   DIAGNOSTICO COMPLETADO
echo ============================================
echo.
echo Si el problema persiste:
echo   1. Ejecute: scripts\diagnosticar_502.bat
echo   2. Revise los logs: scripts\ver_logs_servidor.bat
echo   3. Verifique nginx: scripts\verificar_nginx.bat
echo.

pause

