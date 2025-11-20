@echo off
REM ============================================
REM Script para inicializar o limpiar el repositorio en el servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   INICIALIZAR REPOSITORIO EN EL SERVIDOR
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

REM Verificar qué hay en el directorio
echo Verificando contenido del directorio...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "test -d %SERVIDOR_RUTA% && ls -la %SERVIDOR_RUTA% | head -10 || echo 'Directorio no existe'"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "test -d %SERVIDOR_RUTA% && ls -la %SERVIDOR_RUTA% | head -10 || echo 'Directorio no existe'"
)

echo.
echo Seleccione una opcion:
echo   1. Verificar si ya es un repositorio git y actualizarlo
echo   2. Eliminar el directorio y clonar desde cero
echo   3. Inicializar git en el directorio existente
echo   4. Cancelar
echo.
set /p OPCION="Opcion (1-4): "

if "%OPCION%"=="1" (
    echo.
    echo Verificando si es un repositorio git...
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status > /dev/null 2>&1"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status > /dev/null 2>&1"
    )
    
    if not errorlevel 1 (
        echo El directorio ya es un repositorio git.
        echo Actualizando...
        if exist "%SSH_KEY%" (
            ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git fetch origin && git checkout %BRANCH% && git pull origin %BRANCH%"
        ) else (
            ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git fetch origin && git checkout %BRANCH% && git pull origin %BRANCH%"
        )
        if not errorlevel 1 (
            echo.
            echo Repositorio actualizado exitosamente.
        ) else (
            echo.
            echo ERROR: No se pudo actualizar el repositorio.
        )
    ) else (
        echo El directorio NO es un repositorio git.
        echo Use la opcion 2 o 3.
    )
)

if "%OPCION%"=="2" (
    echo.
    echo ADVERTENCIA: Esto eliminara todo el contenido del directorio %SERVIDOR_RUTA%
    set /p CONFIRMAR="Esta seguro? (S/N): "
    if /i not "!CONFIRMAR!"=="S" (
        echo Cancelado.
        pause
        exit /b 0
    )
    
    echo Eliminando directorio...
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "rm -rf %SERVIDOR_RUTA%"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "rm -rf %SERVIDOR_RUTA%"
    )
    
    if errorlevel 1 (
        echo ERROR: No se pudo eliminar el directorio.
        pause
        exit /b 1
    )
    
    echo Directorio eliminado.
    echo.
    echo Ahora puede ejecutar:
    echo   scripts\clonar_repositorio_servidor.bat
    echo.
)

if "%OPCION%"=="3" (
    echo.
    echo Inicializando git en el directorio existente...
    
    REM Obtener URL del repositorio
    cd /d "%~dp0.."
    for /f "tokens=*" %%i in ('git remote get-url origin 2^>nul') do set REPO_URL=%%i
    
    if "!REPO_URL!"=="" (
        set /p REPO_URL="URL del repositorio Git: "
        if "!REPO_URL!"=="" (
            echo ERROR: URL del repositorio requerida.
            pause
            exit /b 1
        )
    )
    
    echo Repositorio: !REPO_URL!
    echo.
    
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git init && git remote add origin !REPO_URL! && git fetch origin && git checkout -b %BRANCH% origin/%BRANCH% 2>/dev/null || git checkout %BRANCH%"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git init && git remote add origin !REPO_URL! && git fetch origin && git checkout -b %BRANCH% origin/%BRANCH% 2>/dev/null || git checkout %BRANCH%"
    )
    
    if not errorlevel 1 (
        echo.
        echo Repositorio inicializado exitosamente.
    ) else (
        echo.
        echo ERROR: No se pudo inicializar el repositorio.
    )
)

if "%OPCION%"=="4" (
    echo Cancelado.
    pause
    exit /b 0
)

echo.
pause

