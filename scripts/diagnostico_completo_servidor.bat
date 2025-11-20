@echo off
REM ============================================
REM Script para ejecutar diagnóstico completo
REM del servidor Debian
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   DIAGNOSTICO COMPLETO DEL SERVIDOR
echo ============================================
echo.
echo Este script analiza todos los elementos del
echo servidor: certificados SSL, configuraciones,
echo servicios, procesos, y mas.
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

REM Crear directorio local para recibir archivos
set LOCAL_OUTPUT_DIR=%~dp0..\diagnostico_servidor
if not exist "%LOCAL_OUTPUT_DIR%" mkdir "%LOCAL_OUTPUT_DIR%"

echo ============================================
echo   SUBIENDO SCRIPT DE DIAGNOSTICO
echo ============================================
echo.

REM Subir script de diagnóstico al servidor
if exist "%SSH_KEY%" (
    scp -i "%SSH_KEY%" "%~dp0diagnostico_completo_servidor.sh" %SERVIDOR_USUARIO%@%SERVIDOR_IP%:/tmp/diagnostico_completo_servidor.sh >nul 2>&1
) else (
    scp "%~dp0diagnostico_completo_servidor.sh" %SERVIDOR_USUARIO%@%SERVIDOR_IP%:/tmp/diagnostico_completo_servidor.sh >nul 2>&1
)

if errorlevel 1 (
    echo ERROR: No se pudo subir el script al servidor.
    echo Verifique la conexion SSH.
    pause
    exit /b 1
)

echo Script subido correctamente.
echo.

REM Dar permisos de ejecución
echo Dando permisos de ejecucion...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "chmod +x /tmp/diagnostico_completo_servidor.sh" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "chmod +x /tmp/diagnostico_completo_servidor.sh" >nul 2>&1
)

echo.
echo ============================================
echo   EJECUTANDO DIAGNOSTICO
echo ============================================
echo.
echo Esto puede tardar varios minutos...
echo.

REM Ejecutar script de diagnóstico
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash /tmp/diagnostico_completo_servidor.sh"
) else (
    ssh -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash /tmp/diagnostico_completo_servidor.sh"
)

if errorlevel 1 (
    echo.
    echo ERROR: El diagnostico fallo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   DESCARGANDO ARCHIVOS GENERADOS
echo ============================================
echo.

REM Obtener la ruta del directorio de salida del servidor
echo Obteniendo ubicacion de archivos generados...
if exist "%SSH_KEY%" (
    for /f "delims=" %%i in ('ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "ls -td /tmp/diagnostico_servidor_* 2>/dev/null | head -1"') do set REMOTE_OUTPUT_DIR=%%i
) else (
    for /f "delims=" %%i in ('ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "ls -td /tmp/diagnostico_servidor_* 2>/dev/null | head -1"') do set REMOTE_OUTPUT_DIR=%%i
)

if "%REMOTE_OUTPUT_DIR%"=="" (
    echo ERROR: No se pudo encontrar el directorio de salida.
    echo Los archivos pueden estar en /tmp/diagnostico_servidor_*
    pause
    exit /b 1
)

echo Directorio remoto: %REMOTE_OUTPUT_DIR%
echo.

REM Descargar archivos
echo Descargando archivos...
if exist "%SSH_KEY%" (
    scp -i "%SSH_KEY%" -r %SERVIDOR_USUARIO%@%SERVIDOR_IP%:%REMOTE_OUTPUT_DIR% "%LOCAL_OUTPUT_DIR%\" >nul 2>&1
) else (
    scp -r %SERVIDOR_USUARIO%@%SERVIDOR_IP%:%REMOTE_OUTPUT_DIR% "%LOCAL_OUTPUT_DIR%\" >nul 2>&1
)

if errorlevel 1 (
    echo ADVERTENCIA: No se pudieron descargar todos los archivos.
    echo Puede descargarlos manualmente con:
    echo   scp -r %SERVIDOR_USUARIO%@%SERVIDOR_IP%:%REMOTE_OUTPUT_DIR% "%LOCAL_OUTPUT_DIR%"
) else (
    echo Archivos descargados correctamente.
)

echo.
echo ============================================
echo   DIAGNOSTICO COMPLETADO
echo ============================================
echo.
echo Archivos guardados en:
echo   %LOCAL_OUTPUT_DIR%
echo.
echo Para ver el reporte completo:
echo   type "%LOCAL_OUTPUT_DIR%\reporte_completo.txt"
echo.
echo O abra el archivo en un editor de texto.
echo.

REM Intentar abrir el directorio
if exist "%LOCAL_OUTPUT_DIR%" (
    echo Abriendo directorio...
    start "" "%LOCAL_OUTPUT_DIR%"
)

pause

