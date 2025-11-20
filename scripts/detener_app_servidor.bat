@echo off
REM ============================================
REM Script para detener la app en el servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   DETENER APP EN SERVIDOR
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
if "%SERVIDOR_RUTA%"=="" (
    echo ERROR: SERVIDOR_RUTA no esta configurado.
    pause
    exit /b 1
)
if "%LOGS_DIR%"=="" (
    echo ERROR: LOGS_DIR no esta configurado.
    pause
    exit /b 1
)

REM Variables
set FECHA_HORA=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set FECHA_HORA=!FECHA_HORA: =0!
set LOG_FILE=%LOGS_DIR%\stop_%FECHA_HORA%.log

REM Crear directorio de logs si no existe
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo.
echo Seleccione que desea detener:
echo   1. Solo Streamlit (aplicacion)
echo   2. Solo API
echo   3. Ambos
echo.
set /p OPCION="Opcion (1-3): "

if "%OPCION%"=="1" (
    echo.
    echo Deteniendo Streamlit...
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -f 'streamlit.*calculos_combustible_vehicular' && echo 'Streamlit detenido' || echo 'Streamlit no estaba corriendo'" >> "%LOG_FILE%" 2>&1
        if exist "%SERVIDOR_RUTA%/logs/streamlit.pid" (
            ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "rm -f %SERVIDOR_RUTA%/logs/streamlit.pid" >> "%LOG_FILE%" 2>&1
        )
    ) else (
        ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -f 'streamlit.*calculos_combustible_vehicular' && echo 'Streamlit detenido' || echo 'Streamlit no estaba corriendo'" >> "%LOG_FILE%" 2>&1
        if exist "%SERVIDOR_RUTA%/logs/streamlit.pid" (
            ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "rm -f %SERVIDOR_RUTA%/logs/streamlit.pid" >> "%LOG_FILE%" 2>&1
        )
    )
    echo Streamlit detenido.
)

if "%OPCION%"=="2" (
    echo.
    echo Deteniendo API...
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -f 'uvicorn.*api_endpoint' && echo 'API detenida' || echo 'API no estaba corriendo'" >> "%LOG_FILE%" 2>&1
        if exist "%SERVIDOR_RUTA%/logs/api.pid" (
            ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "rm -f %SERVIDOR_RUTA%/logs/api.pid" >> "%LOG_FILE%" 2>&1
        )
    ) else (
        ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -f 'uvicorn.*api_endpoint' && echo 'API detenida' || echo 'API no estaba corriendo'" >> "%LOG_FILE%" 2>&1
        if exist "%SERVIDOR_RUTA%/logs/api.pid" (
            ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "rm -f %SERVIDOR_RUTA%/logs/api.pid" >> "%LOG_FILE%" 2>&1
        )
    )
    echo API detenida.
)

if "%OPCION%"=="3" (
    echo.
    echo Deteniendo Streamlit y API...
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -f 'streamlit.*calculos_combustible_vehicular'; pkill -f 'uvicorn.*api_endpoint'; echo 'Procesos detenidos'" >> "%LOG_FILE%" 2>&1
        ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "rm -f %SERVIDOR_RUTA%/logs/*.pid" >> "%LOG_FILE%" 2>&1
    ) else (
        ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -f 'streamlit.*calculos_combustible_vehicular'; pkill -f 'uvicorn.*api_endpoint'; echo 'Procesos detenidos'" >> "%LOG_FILE%" 2>&1
        ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "rm -f %SERVIDOR_RUTA%/logs/*.pid" >> "%LOG_FILE%" 2>&1
    )
    echo Aplicacion y API detenidas.
)

if "%OPCION%"=="" (
    echo Opcion invalida.
    pause
    exit /b 1
)

echo.
echo Log guardado en: %LOG_FILE%
echo.
pause

