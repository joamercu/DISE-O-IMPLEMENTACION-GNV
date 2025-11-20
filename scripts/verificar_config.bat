@echo off
REM ============================================
REM Script para verificar la configuración
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   VERIFICACION DE CONFIGURACION
echo ============================================
echo.

set CONFIG_FILE=%~dp0deploy_config.txt

if not exist "%CONFIG_FILE%" (
    echo ERROR: Archivo de configuracion no encontrado: %CONFIG_FILE%
    echo.
    echo Ejecute primero: scripts\config_servidor.bat
    echo.
    pause
    exit /b 1
)

echo Archivo de configuracion encontrado: %CONFIG_FILE%
echo.
echo Contenido del archivo:
echo ============================================
type "%CONFIG_FILE%"
echo ============================================
echo.

REM Leer configuración
for /f "usebackq tokens=1,2 delims==" %%a in ("%CONFIG_FILE%") do (
    set "%%a=%%b"
)

echo Variables leidas:
echo ============================================
echo SERVIDOR_IP: [%SERVIDOR_IP%]
echo SERVIDOR_USUARIO: [%SERVIDOR_USUARIO%]
echo SERVIDOR_RUTA: [%SERVIDOR_RUTA%]
echo BRANCH: [%BRANCH%]
echo SSH_KEY: [%SSH_KEY%]
echo LOGS_DIR: [%LOGS_DIR%]
echo ============================================
echo.

REM Validar variables
set ERRORES=0

if "%SERVIDOR_IP%"=="" (
    echo ERROR: SERVIDOR_IP esta vacio
    set /a ERRORES+=1
)

if "%SERVIDOR_USUARIO%"=="" (
    echo ERROR: SERVIDOR_USUARIO esta vacio
    set /a ERRORES+=1
)

if "%SERVIDOR_RUTA%"=="" (
    echo ERROR: SERVIDOR_RUTA esta vacio
    set /a ERRORES+=1
)

if "%BRANCH%"=="" (
    echo ERROR: BRANCH esta vacio
    set /a ERRORES+=1
)

if "%LOGS_DIR%"=="" (
    echo ERROR: LOGS_DIR esta vacio
    set /a ERRORES+=1
)

REM Verificar archivos y directorios
echo.
echo Verificando archivos y directorios:
echo ============================================

if exist "%SSH_KEY%" (
    echo [OK] Clave SSH encontrada: %SSH_KEY%
) else (
    echo [ADVERTENCIA] Clave SSH no encontrada: %SSH_KEY%
    echo   Esto es normal si aun no has generado la clave.
)

if exist "%LOGS_DIR%" (
    echo [OK] Directorio de logs existe: %LOGS_DIR%
) else (
    echo [ADVERTENCIA] Directorio de logs no existe: %LOGS_DIR%
    echo   Se creara automaticamente cuando sea necesario.
)

echo ============================================
echo.

if %ERRORES% GTR 0 (
    echo.
    echo Se encontraron %ERRORES% error(es) en la configuracion.
    echo.
    echo Solucion:
    echo   1. Ejecute: scripts\config_servidor.bat
    echo   2. O edite manualmente: %CONFIG_FILE%
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ============================================
    echo   CONFIGURACION VALIDA
    echo ============================================
    echo.
    echo Todas las variables estan configuradas correctamente.
    echo Puede proceder con el despliegue.
    echo.
)

pause

