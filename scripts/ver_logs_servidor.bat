@echo off
REM ============================================
REM Script para ver logs del servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   VER LOGS DEL SERVIDOR
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

REM Limpiar espacios en blanco de las variables
set "SERVIDOR_IP=%SERVIDOR_IP: =%"
set "SERVIDOR_USUARIO=%SERVIDOR_USUARIO: =%"
set "SERVIDOR_RUTA=%SERVIDOR_RUTA: =%"
set "BRANCH=%BRANCH: =%"
set "SSH_KEY=%SSH_KEY: =%"
set "LOGS_DIR=%LOGS_DIR: =%"

REM Validar variables
if "%SERVIDOR_IP%"=="" (
    echo ERROR: SERVIDOR_IP no esta configurado.
    echo Ejecute primero: config_servidor.bat
    pause
    exit /b 1
)
if "%SERVIDOR_USUARIO%"=="" (
    echo ERROR: SERVIDOR_USUARIO no esta configurado.
    echo Ejecute primero: config_servidor.bat
    pause
    exit /b 1
)
if "%SERVIDOR_RUTA%"=="" (
    echo ERROR: SERVIDOR_RUTA no esta configurado.
    echo Ejecute primero: config_servidor.bat
    pause
    exit /b 1
)

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo.
echo Seleccione el tipo de log a ver:
echo   1. Logs de Streamlit (aplicacion)
echo   2. Logs de API
echo   3. Logs del sistema (systemd)
echo   4. Ver todos los logs
echo   5. Seguir logs en tiempo real (tail -f)
echo   6. Ver ultimos 50 lineas de Streamlit
echo   7. Ver ultimos 50 lineas de API
echo   8. Ver procesos corriendo
echo.
set /p OPCION="Opcion (1-8): "

if "%OPCION%"=="1" (
    echo.
    echo ===== LOGS DE STREAMLIT =====
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 100 %SERVIDOR_RUTA%/logs/streamlit.log 2>/dev/null || echo 'No se encontraron logs de Streamlit'"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 100 %SERVIDOR_RUTA%/logs/streamlit.log 2>/dev/null || echo 'No se encontraron logs de Streamlit'"
    )
)

if "%OPCION%"=="2" (
    echo.
    echo ===== LOGS DE API =====
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 100 %SERVIDOR_RUTA%/logs/api.log 2>/dev/null || echo 'No se encontraron logs de API'"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 100 %SERVIDOR_RUTA%/logs/api.log 2>/dev/null || echo 'No se encontraron logs de API'"
    )
)

if "%OPCION%"=="3" (
    echo.
    echo ===== LOGS DE SYSTEMD =====
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "journalctl -u gnv-streamlit -n 50 --no-pager 2>/dev/null; echo ''; journalctl -u gnv-api -n 50 --no-pager 2>/dev/null"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "journalctl -u gnv-streamlit -n 50 --no-pager 2>/dev/null; echo ''; journalctl -u gnv-api -n 50 --no-pager 2>/dev/null"
    )
)

if "%OPCION%"=="4" (
    echo.
    echo ===== TODOS LOS LOGS =====
    echo.
    echo --- Streamlit ---
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 50 %SERVIDOR_RUTA%/logs/streamlit.log 2>/dev/null || echo 'No hay logs de Streamlit'"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 50 %SERVIDOR_RUTA%/logs/streamlit.log 2>/dev/null || echo 'No hay logs de Streamlit'"
    )
    echo.
    echo --- API ---
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 50 %SERVIDOR_RUTA%/logs/api.log 2>/dev/null || echo 'No hay logs de API'"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 50 %SERVIDOR_RUTA%/logs/api.log 2>/dev/null || echo 'No hay logs de API'"
    )
)

if "%OPCION%"=="5" (
    echo.
    echo ===== SIGUIENDO LOGS EN TIEMPO REAL =====
    echo Presione Ctrl+C para salir
    echo.
    set /p TIPO_LOG="Que log seguir? (streamlit/api): "
    if /i "!TIPO_LOG!"=="streamlit" (
        if exist "%SSH_KEY%" (
            ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -f %SERVIDOR_RUTA%/logs/streamlit.log"
        ) else (
            ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -f %SERVIDOR_RUTA%/logs/streamlit.log"
        )
    ) else if /i "!TIPO_LOG!"=="api" (
        if exist "%SSH_KEY%" (
            ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -f %SERVIDOR_RUTA%/logs/api.log"
        ) else (
            ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -f %SERVIDOR_RUTA%/logs/api.log"
        )
    ) else (
        echo Opcion invalida.
    )
)

if "%OPCION%"=="6" (
    echo.
    echo ===== ULTIMAS 50 LINEAS DE STREAMLIT =====
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 50 %SERVIDOR_RUTA%/logs/streamlit.log 2>/dev/null || echo 'No se encontraron logs'"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 50 %SERVIDOR_RUTA%/logs/streamlit.log 2>/dev/null || echo 'No se encontraron logs'"
    )
)

if "%OPCION%"=="7" (
    echo.
    echo ===== ULTIMAS 50 LINEAS DE API =====
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 50 %SERVIDOR_RUTA%/logs/api.log 2>/dev/null || echo 'No se encontraron logs'"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "tail -n 50 %SERVIDOR_RUTA%/logs/api.log 2>/dev/null || echo 'No se encontraron logs'"
    )
)

if "%OPCION%"=="8" (
    echo.
    echo ===== PROCESOS CORRIENDO =====
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "ps aux | grep -E '(streamlit|uvicorn|api_endpoint)' | grep -v grep"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "ps aux | grep -E '(streamlit|uvicorn|api_endpoint)' | grep -v grep"
    )
    echo.
    echo ===== PUERTOS EN USO =====
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "netstat -tlnp | grep -E '(8501|8000)'"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "netstat -tlnp | grep -E '(8501|8000)'"
    )
)

if "%OPCION%"=="" (
    echo Opcion invalida.
)

echo.
pause

