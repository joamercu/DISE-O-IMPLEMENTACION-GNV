@echo off
REM ============================================
REM Script para diagnosticar error 502 Bad Gateway
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   DIAGNOSTICO ERROR 502 BAD GATEWAY
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

REM Verificar si Streamlit está corriendo
echo ===== VERIFICANDO STREAMLIT =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null && echo '✓ Streamlit esta corriendo' || echo '✗ Streamlit NO esta corriendo'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null && echo '✓ Streamlit esta corriendo' || echo '✗ Streamlit NO esta corriendo'"
)
echo.

REM Verificar puerto 8501
echo ===== VERIFICANDO PUERTO 8501 =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "netstat -tlnp 2>/dev/null | grep ':8501' || ss -tlnp 2>/dev/null | grep ':8501' || echo '✗ Puerto 8501 NO esta en uso'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "netstat -tlnp 2>/dev/null | grep ':8501' || ss -tlnp 2>/dev/null | grep ':8501' || echo '✗ Puerto 8501 NO esta en uso'"
)
echo.

REM Probar conexión local al puerto 8501
echo ===== PROBANDO CONEXION LOCAL =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "curl -s -o /dev/null -w 'HTTP Status: %%{http_code}\n' http://127.0.0.1:8501 || echo '✗ No se puede conectar a http://127.0.0.1:8501'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "curl -s -o /dev/null -w 'HTTP Status: %%{http_code}\n' http://127.0.0.1:8501 || echo '✗ No se puede conectar a http://127.0.0.1:8501'"
)
echo.

REM Verificar logs de Streamlit
echo ===== ULTIMAS LINEAS DE LOG STREAMLIT =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "if [ -f %SERVIDOR_RUTA%/logs/streamlit.log ]; then tail -n 20 %SERVIDOR_RUTA%/logs/streamlit.log; else echo 'Log no encontrado en %SERVIDOR_RUTA%/logs/streamlit.log'; fi"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "if [ -f %SERVIDOR_RUTA%/logs/streamlit.log ]; then tail -n 20 %SERVIDOR_RUTA%/logs/streamlit.log; else echo 'Log no encontrado en %SERVIDOR_RUTA%/logs/streamlit.log'; fi"
)
echo.

REM Verificar configuración de nginx
echo ===== VERIFICANDO NGINX =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "systemctl status nginx --no-pager 2>/dev/null | head -n 5 || service nginx status 2>/dev/null | head -n 5"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "systemctl status nginx --no-pager 2>/dev/null | head -n 5 || service nginx status 2>/dev/null | head -n 5"
)
echo.

REM Verificar logs de nginx
echo ===== ERRORES RECIENTES DE NGINX =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo 'No se pudo leer el log de errores'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo 'No se pudo leer el log de errores'"
)
echo.

REM Verificar configuración de nginx para gnv.weldtech.cloud
echo ===== CONFIGURACION NGINX PARA GNV =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "if [ -f /etc/nginx/sites-available/gnv.weldtech.cloud ]; then echo 'Configuracion encontrada:'; grep -E '(listen|server_name|proxy_pass)' /etc/nginx/sites-available/gnv.weldtech.cloud; else echo '✗ Configuracion no encontrada'; fi"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "if [ -f /etc/nginx/sites-available/gnv.weldtech.cloud ]; then echo 'Configuracion encontrada:'; grep -E '(listen|server_name|proxy_pass)' /etc/nginx/sites-available/gnv.weldtech.cloud; else echo '✗ Configuracion no encontrada'; fi"
)
echo.

echo ============================================
echo   RESUMEN
echo ============================================
echo.
echo Si Streamlit NO esta corriendo:
echo   1. Ejecute: scripts\iniciar_app_servidor.bat
echo.
echo Si el puerto 8501 NO esta en uso:
echo   1. Verifique que Streamlit este corriendo
echo   2. Verifique los logs: scripts\ver_logs_servidor.bat
echo.
echo Si nginx tiene errores:
echo   1. Verifique la configuracion: scripts\verificar_nginx.bat
echo   2. Reconfigure nginx: scripts\configurar_nginx.bat
echo.
echo Si accede por HTTPS pero nginx solo tiene HTTP:
echo   1. Necesita configurar HTTPS en nginx
echo   2. O acceda por HTTP: http://gnv.weldtech.cloud
echo.

pause

