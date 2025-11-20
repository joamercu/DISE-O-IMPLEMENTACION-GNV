@echo off
REM ============================================
REM Script para ver el estado del servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   ESTADO DEL SERVIDOR
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
echo Ruta: %SERVIDOR_RUTA%
echo.

echo ===== PROCESOS CORRIENDO =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "ps aux | grep -E '(streamlit|uvicorn|api_endpoint)' | grep -v grep || echo 'No hay procesos corriendo'"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "ps aux | grep -E '(streamlit|uvicorn|api_endpoint)' | grep -v grep || echo 'No hay procesos corriendo'"
)
echo.

echo ===== PUERTOS EN USO =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "netstat -tlnp 2>/dev/null | grep -E '(8501|8000)' || echo 'Puertos no en uso'"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "netstat -tlnp 2>/dev/null | grep -E '(8501|8000)' || echo 'Puertos no en uso'"
)
echo.

echo ===== ULTIMO COMMIT DESPLEGADO =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:'Commit: %%H%%nAutor: %%an (%%ae)%%nFecha: %%ad%%nMensaje: %%s' --date=iso 2>/dev/null || echo 'No se pudo obtener informacion del commit'"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:'Commit: %%H%%nAutor: %%an (%%ae)%%nFecha: %%ad%%nMensaje: %%s' --date=iso 2>/dev/null || echo 'No se pudo obtener informacion del commit'"
)
echo.

echo ===== BRANCH ACTUAL =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git branch --show-current 2>/dev/null || echo 'No se pudo obtener el branch'"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git branch --show-current 2>/dev/null || echo 'No se pudo obtener el branch'"
)
echo.

echo ===== ESPACIO EN DISCO =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "df -h %SERVIDOR_RUTA% | tail -1"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "df -h %SERVIDOR_RUTA% | tail -1"
)
echo.

echo ===== MEMORIA DISPONIBLE =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "free -h | grep Mem"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "free -h | grep Mem"
)
echo.

echo ===== ARCHIVOS DE PID =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "ls -lh %SERVIDOR_RUTA%/logs/*.pid 2>/dev/null || echo 'No hay archivos PID'"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "ls -lh %SERVIDOR_RUTA%/logs/*.pid 2>/dev/null || echo 'No hay archivos PID'"
)
echo.

echo ===== TAMAÑO DE LOGS =====
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "du -sh %SERVIDOR_RUTA%/logs/* 2>/dev/null || echo 'No hay logs'"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "du -sh %SERVIDOR_RUTA%/logs/* 2>/dev/null || echo 'No hay logs'"
)
echo.

pause

