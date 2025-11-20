@echo off
REM ============================================
REM Script para desplegar la app al servidor Debian
REM desde el branch developer usando SSH
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   DESPLIEGUE APP GNV AL SERVIDOR
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

REM Variables
set FECHA_HORA=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set FECHA_HORA=!FECHA_HORA: =0!
set LOG_FILE=%LOGS_DIR%\deploy_%FECHA_HORA%.log
set ERROR_LOG=%LOGS_DIR%\deploy_error_%FECHA_HORA%.log

REM Validar que las variables estén configuradas
if "%SERVIDOR_IP%"=="" (
    echo ERROR: SERVIDOR_IP no esta configurado en %CONFIG_FILE%
    pause
    exit /b 1
)
if "%SERVIDOR_USUARIO%"=="" (
    echo ERROR: SERVIDOR_USUARIO no esta configurado en %CONFIG_FILE%
    pause
    exit /b 1
)
if "%SERVIDOR_RUTA%"=="" (
    echo ERROR: SERVIDOR_RUTA no esta configurado en %CONFIG_FILE%
    pause
    exit /b 1
)
if "%BRANCH%"=="" (
    echo ERROR: BRANCH no esta configurado en %CONFIG_FILE%
    pause
    exit /b 1
)
if "%LOGS_DIR%"=="" (
    echo ERROR: LOGS_DIR no esta configurado en %CONFIG_FILE%
    pause
    exit /b 1
)

REM Crear directorio de logs si no existe
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo Iniciando despliegue...
echo Fecha: %date% %time%
echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo Ruta: %SERVIDOR_RUTA%
echo Branch: %BRANCH%
echo Log: %LOG_FILE%
echo.

REM Verificar que estamos en un repositorio git
cd /d "%~dp0.."
git status >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encuentra un repositorio Git en este directorio.
    echo. >> "%ERROR_LOG%"
    echo ERROR: No se encuentra un repositorio Git >> "%ERROR_LOG%"
    pause
    exit /b 1
)

REM Verificar que el branch developer existe
git branch --list %BRANCH% >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: El branch %BRANCH% no existe localmente.
    echo Intentando crear/obtener desde remoto...
    git fetch origin %BRANCH% 2>>"%ERROR_LOG%"
    if errorlevel 1 (
        echo ERROR: No se pudo obtener el branch %BRANCH%
        pause
        exit /b 1
    )
)

REM Construir comando SSH
if exist "%SSH_KEY%" (
    set "SSH_CMD=ssh -i \"%SSH_KEY%\""
) else (
    set "SSH_CMD=ssh"
)

REM Verificar conexión SSH
echo Verificando conexion SSH...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "echo 'Conexion exitosa'" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "echo 'Conexion exitosa'" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if errorlevel 1 (
    echo ERROR: No se pudo conectar al servidor.
    echo Verifique:
    echo   1. La clave SSH esta en: %SSH_KEY%
    echo   2. El servidor es accesible: %SERVIDOR_IP%
    echo   3. El usuario tiene permisos: %SERVIDOR_USUARIO%
    echo.
    echo Detalles en: %ERROR_LOG%
    pause
    exit /b 1
)

echo Conexion SSH exitosa.
echo.

REM Crear directorio en el servidor si no existe
echo Creando directorio en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "mkdir -p %SERVIDOR_RUTA%" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "mkdir -p %SERVIDOR_RUTA%" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if errorlevel 1 (
    echo ERROR: No se pudo crear el directorio en el servidor.
    pause
    exit /b 1
)

REM Verificar si existe repositorio git en el servidor
echo Verificando repositorio en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status > /dev/null 2>&1" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status > /dev/null 2>&1" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if errorlevel 1 (
    echo El repositorio no existe en el servidor.
    echo Necesita clonar el repositorio primero.
    echo.
    echo Opcion 1 - Automatico (recomendado):
    echo   Ejecute: scripts\clonar_repositorio_servidor.bat
    echo.
    echo Opcion 2 - Manual:
    echo   Conectese al servidor y ejecute:
    echo     ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP%
    echo     git clone -b %BRANCH% [URL_DEL_REPO] %SERVIDOR_RUTA%
    echo.
    echo Despues de clonar, ejecute este script nuevamente.
    pause
    exit /b 1
)

REM Obtener URL del repositorio remoto
echo Obteniendo URL del repositorio...
for /f "tokens=*" %%i in ('git remote get-url origin 2^>nul') do set REPO_URL=%%i
if "!REPO_URL!"=="" (
    echo ERROR: No se encontro el repositorio remoto 'origin'
    echo Configure el repositorio remoto primero.
    pause
    exit /b 1
)

echo Repositorio: !REPO_URL!
echo.

REM Hacer pull del branch developer en el servidor
echo Actualizando codigo en el servidor (branch: %BRANCH%)...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git fetch origin && git checkout %BRANCH% && git pull origin %BRANCH%" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git fetch origin && git checkout %BRANCH% && git pull origin %BRANCH%" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if errorlevel 1 (
    echo ERROR: No se pudo actualizar el codigo en el servidor.
    echo Verifique los logs: %ERROR_LOG%
    pause
    exit /b 1
)

echo Codigo actualizado exitosamente.
echo.

REM Instalar/actualizar dependencias en el servidor
echo Instalando dependencias en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && pip3 install -r requirements.txt" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && pip3 install -r requirements.txt" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)
if errorlevel 1 (
    echo ADVERTENCIA: Hubo problemas instalando dependencias.
    echo Verifique los logs: %ERROR_LOG%
    echo Continuando...
)

echo Dependencias instaladas.
echo.

REM Crear directorio de logs en el servidor
echo Creando directorio de logs en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "mkdir -p %SERVIDOR_RUTA%/logs" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "mkdir -p %SERVIDOR_RUTA%/logs" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
)

REM Obtener commit actual
echo Obteniendo informacion del commit...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:'%%H|%%an|%%ae|%%ad|%%s' --date=iso" > "%LOGS_DIR%\last_commit.txt" 2>>"%ERROR_LOG%"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:'%%H|%%an|%%ae|%%ad|%%s' --date=iso" > "%LOGS_DIR%\last_commit.txt" 2>>"%ERROR_LOG%"
)

echo.
echo ============================================
echo   DESPLIEGUE COMPLETADO
echo ============================================
echo.
echo Log completo: %LOG_FILE%
echo Errores: %ERROR_LOG%
echo.
echo Para iniciar la aplicacion en el servidor, ejecute:
echo   iniciar_app_servidor.bat
echo.

pause

