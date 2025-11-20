@echo off
REM ============================================
REM Script para hacer commit y pull en el servidor
REM Hace commit de cambios locales, push al remoto
REM y pull en el servidor por SSH
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   COMMIT Y PULL EN SERVIDOR
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
set LOG_FILE=%LOGS_DIR%\commit_pull_%FECHA_HORA%.log
set ERROR_LOG=%LOGS_DIR%\commit_pull_error_%FECHA_HORA%.log

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

echo Iniciando proceso de commit y pull...
echo Fecha: %date% %time%
echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo Ruta: %SERVIDOR_RUTA%
echo Branch: %BRANCH%
echo Log: %LOG_FILE%
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0.."

REM Verificar que estamos en un repositorio git
git status >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encuentra un repositorio Git en este directorio.
    echo. >> "%ERROR_LOG%"
    echo ERROR: No se encuentra un repositorio Git >> "%ERROR_LOG%"
    pause
    exit /b 1
)

REM Verificar estado de git
echo Verificando estado del repositorio...
git status --short >nul 2>&1
if errorlevel 1 (
    echo No hay cambios para commitear.
    set HAY_CAMBIOS=0
) else (
    git status --short | findstr /R "." >nul 2>&1
    if errorlevel 1 (
        echo No hay cambios para commitear.
        set HAY_CAMBIOS=0
    ) else (
        set HAY_CAMBIOS=1
    )
)

REM Mostrar cambios pendientes
if !HAY_CAMBIOS!==1 (
    echo.
    echo Cambios pendientes:
    git status --short
    echo.
    
    REM Solicitar mensaje de commit
    set /p COMMIT_MESSAGE="Ingrese el mensaje de commit (o presione Enter para mensaje por defecto): "
    if "!COMMIT_MESSAGE!"=="" (
        set COMMIT_MESSAGE=Actualizacion automatica - %date% %time%
    )
    
    REM Agregar todos los cambios
    echo.
    echo Agregando cambios al staging...
    git add -A >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
    if errorlevel 1 (
        echo ERROR: No se pudieron agregar los cambios.
        echo Verifique los logs: %ERROR_LOG%
        pause
        exit /b 1
    )
    
    REM Hacer commit
    echo Haciendo commit...
    git commit -m "!COMMIT_MESSAGE!" >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
    if errorlevel 1 (
        echo ERROR: No se pudo hacer el commit.
        echo Verifique los logs: %ERROR_LOG%
        pause
        exit /b 1
    )
    
    echo Commit realizado exitosamente.
    echo.
    
    REM Hacer push al remoto
    echo Haciendo push al repositorio remoto (branch: %BRANCH%)...
    git push origin %BRANCH% >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
    if errorlevel 1 (
        echo ERROR: No se pudo hacer push al repositorio remoto.
        echo Verifique los logs: %ERROR_LOG%
        pause
        exit /b 1
    )
    
    echo Push realizado exitosamente.
    echo.
) else (
    echo No hay cambios locales para commitear.
    echo Verificando si hay cambios en el remoto...
    git fetch origin >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
    git status -sb | findstr /C:"ahead" >nul 2>&1
    if not errorlevel 1 (
        echo Hay commits locales que no se han pusheado.
        echo Haciendo push...
        git push origin %BRANCH% >> "%LOG_FILE%" 2>>"%ERROR_LOG%"
        if errorlevel 1 (
            echo ERROR: No se pudo hacer push al repositorio remoto.
            echo Verifique los logs: %ERROR_LOG%
            pause
            exit /b 1
        )
        echo Push realizado exitosamente.
        echo.
    ) else (
        echo No hay cambios para pushear.
        echo.
    )
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

REM Hacer pull en el servidor
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

echo Codigo actualizado exitosamente en el servidor.
echo.

REM Obtener información del commit en el servidor
echo Obteniendo informacion del commit en el servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:'%%H|%%an|%%ae|%%ad|%%s' --date=iso" > "%LOGS_DIR%\last_commit_servidor.txt" 2>>"%ERROR_LOG%"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:'%%H|%%an|%%ae|%%ad|%%s' --date=iso" > "%LOGS_DIR%\last_commit_servidor.txt" 2>>"%ERROR_LOG%"
)

echo.
echo ============================================
echo   PROCESO COMPLETADO
echo ============================================
echo.
echo Log completo: %LOG_FILE%
echo Errores: %ERROR_LOG%
echo.
echo El codigo ha sido actualizado en el servidor.
echo.

pause

