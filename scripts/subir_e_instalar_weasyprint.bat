@echo off
REM ============================================
REM Script para subir e instalar WeasyPrint en el servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   Instalación de WeasyPrint en el Servidor
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

REM Limpiar espacios en blanco
set "SERVIDOR_IP=%SERVIDOR_IP: =%"
set "SERVIDOR_USUARIO=%SERVIDOR_USUARIO: =%"
set "SERVIDOR_RUTA=%SERVIDOR_RUTA: =%"
set "SSH_KEY=%SSH_KEY: =%"

REM Validar variables
if "%SERVIDOR_IP%"=="" (
    echo ERROR: SERVIDOR_IP no esta configurado.
    pause
    exit /b 1
)

echo Subiendo script de instalación al servidor...
echo.

REM Subir script al servidor
if exist "%SSH_KEY%" (
    scp -i "%SSH_KEY%" "%~dp0instalar_weasyprint_debian.sh" %SERVIDOR_USUARIO%@%SERVIDOR_IP%:/tmp/instalar_weasyprint_debian.sh
) else (
    scp "%~dp0instalar_weasyprint_debian.sh" %SERVIDOR_USUARIO%@%SERVIDOR_IP%:/tmp/instalar_weasyprint_debian.sh
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
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "chmod +x /tmp/instalar_weasyprint_debian.sh"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "chmod +x /tmp/instalar_weasyprint_debian.sh"
)

echo.
echo ============================================
echo   Ejecutando Instalación
echo ============================================
echo.

REM Ejecutar script de instalación
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash /tmp/instalar_weasyprint_debian.sh"
) else (
    ssh -t %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash /tmp/instalar_weasyprint_debian.sh"
)

if errorlevel 1 (
    echo.
    echo ERROR: La instalacion fallo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Instalación Completada
echo ============================================
echo.

pause

