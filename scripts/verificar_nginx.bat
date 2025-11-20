@echo off
REM ============================================
REM Script para verificar configuración de Nginx
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   VERIFICAR CONFIGURACION NGINX
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

REM Verificar configuración
echo ===== CONFIGURACIONES NGINX =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "echo 'Configuraciones disponibles:'; ls -la /etc/nginx/sites-available/ 2>/dev/null | grep -E '(gnv|weldtech)' || echo 'No se encontraron configuraciones'; echo; echo 'Configuraciones habilitadas:'; ls -la /etc/nginx/sites-enabled/ 2>/dev/null | grep -E '(gnv|weldtech)' || echo 'No se encontraron configuraciones habilitadas'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "echo 'Configuraciones disponibles:'; ls -la /etc/nginx/sites-available/ 2>/dev/null | grep -E '(gnv|weldtech)' || echo 'No se encontraron configuraciones'; echo; echo 'Configuraciones habilitadas:'; ls -la /etc/nginx/sites-enabled/ 2>/dev/null | grep -E '(gnv|weldtech)' || echo 'No se encontraron configuraciones habilitadas'"
)
echo.

echo ===== SERVER_NAME CONFIGURADOS =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "grep -r 'server_name.*weldtech.cloud' /etc/nginx/sites-available/ 2>/dev/null || echo 'No se encontraron configuraciones con weldtech.cloud'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "grep -r 'server_name.*weldtech.cloud' /etc/nginx/sites-available/ 2>/dev/null || echo 'No se encontraron configuraciones con weldtech.cloud'"
)
echo.

echo ===== ESTADO DE NGINX =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "systemctl status nginx --no-pager 2>/dev/null | head -n 10 || service nginx status 2>/dev/null | head -n 10 || echo 'No se pudo obtener el estado'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "systemctl status nginx --no-pager 2>/dev/null | head -n 10 || service nginx status 2>/dev/null | head -n 10 || echo 'No se pudo obtener el estado'"
)
echo.

echo ===== VERIFICACION DE CONFIGURACION =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "nginx -t 2>&1"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "nginx -t 2>&1"
)
echo.

echo ===== CONTENIDO DE CONFIGURACION GNV =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "if [ -f /etc/nginx/sites-available/gnv.weldtech.cloud ]; then cat /etc/nginx/sites-available/gnv.weldtech.cloud; else echo 'Archivo no encontrado'; fi"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "if [ -f /etc/nginx/sites-available/gnv.weldtech.cloud ]; then cat /etc/nginx/sites-available/gnv.weldtech.cloud; else echo 'Archivo no encontrado'; fi"
)
echo.

pause
