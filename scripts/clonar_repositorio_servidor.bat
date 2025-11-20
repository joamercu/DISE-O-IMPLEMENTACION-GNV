@echo off
REM ============================================
REM Script para clonar el repositorio en el servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   CLONAR REPOSITORIO EN EL SERVIDOR
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
if "%BRANCH%"=="" (
    echo ERROR: BRANCH no esta configurado.
    pause
    exit /b 1
)

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo Ruta: %SERVIDOR_RUTA%
echo Branch: %BRANCH%
echo.

REM Obtener URL del repositorio remoto
echo Obteniendo URL del repositorio remoto...
cd /d "%~dp0.."
for /f "tokens=*" %%i in ('git remote get-url origin 2^>nul') do set REPO_URL=%%i

if "!REPO_URL!"=="" (
    echo ERROR: No se encontro el repositorio remoto 'origin'
    echo.
    echo Por favor, configure el repositorio remoto primero:
    echo   git remote add origin [URL_DEL_REPO]
    echo.
    echo O ingrese la URL del repositorio manualmente:
    set /p REPO_URL="URL del repositorio Git: "
    if "!REPO_URL!"=="" (
        echo ERROR: URL del repositorio requerida.
        pause
        exit /b 1
    )
)

echo Repositorio: !REPO_URL!
echo.

REM Verificar si el directorio ya existe en el servidor
echo Verificando si el directorio ya existe en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "test -d %SERVIDOR_RUTA%" >nul 2>&1
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "test -d %SERVIDOR_RUTA%" >nul 2>&1
)

if not errorlevel 1 (
    echo ADVERTENCIA: El directorio %SERVIDOR_RUTA% ya existe en el servidor.
    echo.
    
    REM Verificar si ya es un repositorio git
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status > /dev/null 2>&1"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status > /dev/null 2>&1"
    )
    
    if not errorlevel 1 (
        echo El directorio ya es un repositorio git.
        echo.
        echo Use el script: scripts\inicializar_repositorio_servidor.bat
        echo O ejecute: scripts\deploy_app.bat (actualizara el repositorio existente)
        echo.
        pause
        exit /b 0
    )
    
    echo El directorio existe pero NO es un repositorio git.
    echo.
    set /p SOBRESCRIBIR="Desea eliminarlo y clonar nuevamente? (S/N): "
    if /i not "!SOBRESCRIBIR!"=="S" (
        echo Cancelado.
        echo.
        echo Use el script: scripts\inicializar_repositorio_servidor.bat
        echo para inicializar git en el directorio existente.
        pause
        exit /b 0
    )
    echo Eliminando directorio existente...
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "rm -rf %SERVIDOR_RUTA%"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "rm -rf %SERVIDOR_RUTA%"
    )
    if errorlevel 1 (
        echo ERROR: No se pudo eliminar el directorio existente.
        pause
        exit /b 1
    )
)

REM Crear directorio padre si no existe
echo Creando directorio padre si no existe...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "mkdir -p $(dirname %SERVIDOR_RUTA%)"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "mkdir -p $(dirname %SERVIDOR_RUTA%)"
)

REM Verificar si git está instalado en el servidor
echo Verificando que git este instalado en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "which git > /dev/null 2>&1"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "which git > /dev/null 2>&1"
)
if errorlevel 1 (
    echo ERROR: Git no esta instalado en el servidor.
    echo.
    echo Instale git en el servidor:
    echo   ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP%
    echo   sudo apt update
    echo   sudo apt install git -y
    echo.
    pause
    exit /b 1
)

REM Clonar el repositorio
echo.
echo Clonando repositorio en el servidor...
echo Repositorio: !REPO_URL!
echo Branch: %BRANCH%
echo Ruta: %SERVIDOR_RUTA%
echo.
echo Esto puede tardar unos minutos...
echo.

if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "git clone -b %BRANCH% !REPO_URL! %SERVIDOR_RUTA%"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "git clone -b %BRANCH% !REPO_URL! %SERVIDOR_RUTA%"
)

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo clonar el repositorio.
    echo.
    echo Posibles causas:
    echo   1. El servidor no tiene acceso al repositorio (verifique credenciales SSH)
    echo   2. El branch %BRANCH% no existe en el repositorio
    echo   3. El servidor no tiene git instalado
    echo   4. Problemas de red o permisos
    echo.
    echo Puede intentar clonar manualmente:
    echo   ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP%
    echo   git clone -b %BRANCH% !REPO_URL! %SERVIDOR_RUTA%
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   REPOSITORIO CLONADO EXITOSAMENTE
echo ============================================
echo.
echo El repositorio ha sido clonado en: %SERVIDOR_RUTA%
echo Branch: %BRANCH%
echo.
echo Ahora puede ejecutar:
echo   scripts\deploy_app.bat
echo.
pause

