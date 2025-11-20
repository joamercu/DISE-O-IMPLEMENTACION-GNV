@echo off
REM ============================================
REM Script completo para solucionar error 502
REM 1. Reinicia Streamlit
REM 2. Configura Nginx
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   SOLUCION COMPLETA ERROR 502
echo ============================================
echo.
echo Este script realizara:
echo   1. Reiniciar Streamlit correctamente
echo   2. Configurar Nginx (con deteccion SSL automatica)
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
if "%SERVIDOR_RUTA%"=="" (
    echo ERROR: SERVIDOR_RUTA no esta configurado.
    pause
    exit /b 1
)

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo.

set /p CONTINUAR="Desea continuar? (S/N): "
if /i not "%CONTINUAR%"=="S" (
    echo Cancelado.
    pause
    exit /b 0
)

echo.
echo ============================================
echo   PASO 1: REINICIAR STREAMLIT
echo ============================================
echo.
call "%~dp0reiniciar_streamlit.bat"
if errorlevel 1 (
    echo ERROR: No se pudo reiniciar Streamlit.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   PASO 2: CONFIGURAR NGINX
echo ============================================
echo.

REM Subir script mejorado de nginx al servidor
echo Subiendo script de configuracion de nginx...
if exist "%SSH_KEY%" (
    scp -i "%SSH_KEY%" "%~dp0config_nginx_servidor.sh" %SERVIDOR_USUARIO%@%SERVIDOR_IP%:/tmp/config_nginx_servidor.sh >nul 2>&1
) else (
    scp "%~dp0config_nginx_servidor.sh" %SERVIDOR_USUARIO%@%SERVIDOR_IP%:/tmp/config_nginx_servidor.sh >nul 2>&1
)

if errorlevel 1 (
    echo   ⚠ No se pudo subir el script, usando metodo alternativo...
    call "%~dp0configurar_nginx.bat"
) else (
    echo   ✓ Script subido correctamente
    echo   Ejecutando configuracion de nginx...
    echo.
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "chmod +x /tmp/config_nginx_servidor.sh && bash /tmp/config_nginx_servidor.sh"
    ) else (
        ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "chmod +x /tmp/config_nginx_servidor.sh && bash /tmp/config_nginx_servidor.sh"
    )
    
    if errorlevel 1 (
        echo   ERROR: La configuracion de nginx fallo.
        echo   Intentando metodo alternativo...
        call "%~dp0configurar_nginx.bat"
    )
)

echo.
echo ============================================
echo   VERIFICACION FINAL
echo ============================================
echo.

REM Verificar Streamlit
echo Verificando Streamlit...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null && netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null && netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null" >nul 2>&1
)

if errorlevel 1 (
    echo   ✗ Streamlit NO esta funcionando correctamente
) else (
    echo   ✓ Streamlit esta corriendo y escuchando en el puerto 8501
)

REM Verificar Nginx
echo Verificando Nginx...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "test -f /etc/nginx/sites-available/gnv.weldtech.cloud && nginx -t > /dev/null 2>&1" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "test -f /etc/nginx/sites-available/gnv.weldtech.cloud && nginx -t > /dev/null 2>&1" >nul 2>&1
)

if errorlevel 1 (
    echo   ✗ Nginx NO esta configurado correctamente
) else (
    echo   ✓ Nginx esta configurado correctamente
)

echo.
echo ============================================
echo   SOLUCION COMPLETADA
echo ============================================
echo.
echo La aplicacion deberia estar disponible en:
echo   - https://gnv.weldtech.cloud
echo   - http://gnv.weldtech.cloud (redirige a HTTPS)
echo.
echo Si aun tiene problemas:
echo   1. Ejecute: scripts\diagnosticar_502.bat
echo   2. Revise los logs: scripts\ver_logs_servidor.bat
echo   3. Verifique certificados SSL en el servidor
echo.

pause

