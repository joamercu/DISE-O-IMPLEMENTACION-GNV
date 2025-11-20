@echo off
REM ============================================
REM Script para iniciar la API en el servidor Debian
REM usando SSH
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   INICIAR API EN SERVIDOR
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
set LOG_FILE=%LOGS_DIR%\start_api_%FECHA_HORA%.log
set ERROR_LOG=%LOGS_DIR%\start_api_error_%FECHA_HORA%.log

REM Crear directorio de logs si no existe
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo Ruta: %SERVIDOR_RUTA%
echo Log: %LOG_FILE%
echo.

REM Verificar si la API ya está corriendo
echo Verificando si la API ya esta corriendo...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'uvicorn.*api_endpoint' > /dev/null" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'uvicorn.*api_endpoint' > /dev/null" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if not errorlevel 1 (
    echo ADVERTENCIA: La API parece estar corriendo.
    echo.
    set /p DETENER="Desea detenerla primero? (S/N): "
    if /i "!DETENER!"=="S" (
        echo Deteniendo API...
        if exist "%SSH_KEY%" (
            ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -f 'uvicorn.*api_endpoint'" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
        ) else (
            ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -f 'uvicorn.*api_endpoint'" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
        )
        timeout /t 2 >nul
    ) else (
        echo Cancelado.
        pause
        exit /b 0
    )
)

REM Verificar que el archivo existe en el servidor
echo Verificando archivos en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "test -f %SERVIDOR_RUTA%/src/api_endpoint.py" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "test -f %SERVIDOR_RUTA%/src/api_endpoint.py" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if errorlevel 1 (
    echo ERROR: El archivo no existe en el servidor.
    echo Ejecute primero: deploy_app.bat
    pause
    exit /b 1
)

REM Iniciar la API en background usando nohup
echo Iniciando API FastAPI en el servidor...
echo Esto puede tardar unos segundos...
echo.

REM Crear script de inicio en el servidor
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > %SERVIDOR_RUTA%/start_api.sh << 'EOF'
#!/bin/bash
cd %SERVIDOR_RUTA%
export PYTHONPATH=%SERVIDOR_RUTA%
nohup python3 -m uvicorn src.api_endpoint:app --host 0.0.0.0 --port 8000 --log-level info > %SERVIDOR_RUTA%/logs/api.log 2>&1 &
echo \$! > %SERVIDOR_RUTA%/logs/api.pid
echo 'API iniciada con PID: '\$(cat %SERVIDOR_RUTA%/logs/api.pid)
EOF
chmod +x %SERVIDOR_RUTA%/start_api.sh" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > %SERVIDOR_RUTA%/start_api.sh << 'EOF'
#!/bin/bash
cd %SERVIDOR_RUTA%
export PYTHONPATH=%SERVIDOR_RUTA%
nohup python3 -m uvicorn src.api_endpoint:app --host 0.0.0.0 --port 8000 --log-level info > %SERVIDOR_RUTA%/logs/api.log 2>&1 &
echo \$! > %SERVIDOR_RUTA%/logs/api.pid
echo 'API iniciada con PID: '\$(cat %SERVIDOR_RUTA%/logs/api.pid)
EOF
chmod +x %SERVIDOR_RUTA%/start_api.sh" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)

REM Ejecutar el script
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash %SERVIDOR_RUTA%/start_api.sh" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash %SERVIDOR_RUTA%/start_api.sh" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if errorlevel 1 (
    echo ERROR: No se pudo iniciar la API.
    echo Verifique los logs: %ERROR_LOG%
    pause
    exit /b 1
)

REM Esperar un momento y verificar que está corriendo
timeout /t 3 >nul
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'uvicorn.*api_endpoint' > /dev/null" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'uvicorn.*api_endpoint' > /dev/null" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if errorlevel 1 (
    echo ERROR: La API no se inicio correctamente.
    echo Verifique los logs del servidor.
    pause
    exit /b 1
)

REM Obtener PID
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat %SERVIDOR_RUTA%/logs/api.pid 2>/dev/null || pgrep -f 'uvicorn.*api_endpoint'" > "%LOGS_DIR%\api_pid.txt" 2>>"%ERROR_LOG%"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat %SERVIDOR_RUTA%/logs/api.pid 2>/dev/null || pgrep -f 'uvicorn.*api_endpoint'" > "%LOGS_DIR%\api_pid.txt" 2>>"%ERROR_LOG%"
)

echo.
echo ============================================
echo   API INICIADA
echo ============================================
echo.
echo La API esta corriendo en:
echo   - http://%SERVIDOR_IP%:8000
echo   - http://api-gnv.weldtech.cloud
echo   - http://%SERVIDOR_IP%:8000/docs (Documentacion)
echo.
echo Log completo: %LOG_FILE%
echo PID guardado en: %LOGS_DIR%\api_pid.txt
echo.
echo Para ver los logs en tiempo real, ejecute:
echo   ver_logs_servidor.bat
echo.

pause

