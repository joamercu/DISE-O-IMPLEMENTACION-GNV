@echo off
REM ============================================
REM Script para comparar commits entre local y servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   COMPARAR COMMITS LOCAL vs SERVIDOR
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
echo Ruta servidor: %SERVIDOR_RUTA%
echo Branch: %BRANCH%
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0.."

REM Verificar que estamos en un repositorio git
git status >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encuentra un repositorio Git en este directorio.
    pause
    exit /b 1
)

REM Actualizar referencias remotas
echo [1] Actualizando referencias remotas...
git fetch origin --quiet
if errorlevel 1 (
    echo ERROR: No se pudo actualizar las referencias remotas.
    pause
    exit /b 1
)
echo   OK: Referencias actualizadas
echo.

REM Obtener commit actual local
echo [2] Commit actual LOCAL (HEAD):
for /f "tokens=*" %%i in ('git log -1 --pretty=format:"%%H" 2^>nul') do set LOCAL_HASH=%%i
if "!LOCAL_HASH!"=="" (
    echo   ERROR: No se pudo obtener el commit local
) else (
    echo   Hash: !LOCAL_HASH!
    for /f "tokens=*" %%i in ('git log -1 --pretty=format:"%%an" 2^>nul') do echo   Autor: %%i
    for /f "tokens=*" %%i in ('git log -1 --pretty=format:"%%ad" --date=iso 2^>nul') do echo   Fecha: %%i
    for /f "tokens=*" %%i in ('git log -1 --pretty=format:"%%s" 2^>nul') do echo   Mensaje: %%i
)
echo.

REM Obtener commit actual en origin/developer
echo [3] Commit actual en ORIGIN/DEVELOPER:
for /f "tokens=*" %%i in ('git log -1 --pretty=format:"%%H" origin/%BRANCH% 2^>nul') do set ORIGIN_HASH=%%i
if "!ORIGIN_HASH!"=="" (
    echo   ERROR: No se encontro origin/%BRANCH%
    set ORIGIN_HASH=unknown
) else (
    echo   Hash: !ORIGIN_HASH!
    for /f "tokens=*" %%i in ('git log -1 --pretty=format:"%%an" origin/%BRANCH% 2^>nul') do echo   Autor: %%i
    for /f "tokens=*" %%i in ('git log -1 --pretty=format:"%%ad" --date=iso origin/%BRANCH% 2^>nul') do echo   Fecha: %%i
    for /f "tokens=*" %%i in ('git log -1 --pretty=format:"%%s" origin/%BRANCH% 2^>nul') do echo   Mensaje: %%i
)
echo.

REM Verificar conexión SSH
echo [4] Verificando conexion SSH al servidor...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "echo 'Conexion exitosa'" >nul 2>&1
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "echo 'Conexion exitosa'" >nul 2>&1
)
if errorlevel 1 (
    echo   ERROR: No se pudo conectar al servidor.
    echo   Verifique la conexion SSH.
    pause
    exit /b 1
)
echo   OK: Conexion SSH exitosa
echo.

REM Obtener commit actual en el servidor
echo [5] Commit actual en el SERVIDOR:
if exist "%SSH_KEY%" (
    for /f "tokens=*" %%i in ('ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git fetch origin --quiet 2^>nul && git log -1 --pretty=format:%%H HEAD 2^>nul"') do set SERVIDOR_HASH=%%i
) else (
    for /f "tokens=*" %%i in ('ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git fetch origin --quiet 2^>nul && git log -1 --pretty=format:%%H HEAD 2^>nul"') do set SERVIDOR_HASH=%%i
)

if "!SERVIDOR_HASH!"=="" (
    echo   ERROR: No se pudo obtener el commit del servidor.
    set SERVIDOR_HASH=unknown
) else (
    echo   Hash: !SERVIDOR_HASH!
    if exist "%SSH_KEY%" (
        for /f "tokens=*" %%i in ('ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:%%an HEAD 2^>nul"') do echo   Autor: %%i
        for /f "tokens=*" %%i in ('ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:%%ad --date=iso HEAD 2^>nul"') do echo   Fecha: %%i
        for /f "tokens=*" %%i in ('ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:%%s HEAD 2^>nul"') do echo   Mensaje: %%i
    ) else (
        for /f "tokens=*" %%i in ('ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:%%an HEAD 2^>nul"') do echo   Autor: %%i
        for /f "tokens=*" %%i in ('ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:%%ad --date=iso HEAD 2^>nul"') do echo   Fecha: %%i
        for /f "tokens=*" %%i in ('ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:%%s HEAD 2^>nul"') do echo   Mensaje: %%i
    )
)
echo.

REM Comparar commits
echo ============================================
echo   COMPARACION DE COMMITS
echo ============================================
echo.

REM Commits locales que no están en origin/developer
echo [A] COMMITS LOCALES que NO estan en ORIGIN/DEVELOPER:
echo    (Commits que necesitan ser pusheados)
echo.
git log origin/%BRANCH%..HEAD --oneline
if errorlevel 1 (
    echo    (ninguno)
) else (
    set /a LOCAL_AHEAD=0
    for /f %%i in ('git rev-list --count origin/%BRANCH%..HEAD 2^>nul') do set LOCAL_AHEAD=%%i
    if "!LOCAL_AHEAD!"=="" set LOCAL_AHEAD=0
    if !LOCAL_AHEAD! GTR 0 (
        echo.
        echo    Total: !LOCAL_AHEAD! commit(s) pendiente(s) de push
    )
)
echo.

REM Commits en origin/developer que no están en local
echo [B] COMMITS en ORIGIN/DEVELOPER que NO estan en LOCAL:
echo    (Commits que necesitan ser traidos con pull)
echo.
git log HEAD..origin/%BRANCH% --oneline
if errorlevel 1 (
    echo    (ninguno)
) else (
    set /a REMOTE_AHEAD=0
    for /f %%i in ('git rev-list --count HEAD..origin/%BRANCH% 2^>nul') do set REMOTE_AHEAD=%%i
    if "!REMOTE_AHEAD!"=="" set REMOTE_AHEAD=0
    if !REMOTE_AHEAD! GTR 0 (
        echo.
        echo    Total: !REMOTE_AHEAD! commit(s) pendiente(s) de pull
    )
)
echo.

REM Comparar servidor con origin/developer
echo [C] COMMITS en ORIGIN/DEVELOPER que NO estan en el SERVIDOR:
echo    (Commits que el servidor necesita actualizar)
echo.
if "!SERVIDOR_HASH!"=="" (
    echo    ERROR: No se pudo obtener el hash del servidor
) else (
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log HEAD..origin/%BRANCH% --oneline 2^>nul"
    ) else (
        ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log HEAD..origin/%BRANCH% --oneline 2^>nul"
    )
    if errorlevel 1 (
        echo    (ninguno o error al verificar)
    )
)
echo.

REM Comparar servidor con local
echo [D] COMMITS LOCALES que NO estan en el SERVIDOR:
echo    (Commits que necesitan ser pusheados y luego actualizados en el servidor)
echo.
if "!SERVIDOR_HASH!"=="" (
    echo    ERROR: No se pudo obtener el hash del servidor
) else if "!SERVIDOR_HASH!"=="unknown" (
    echo    ERROR: No se pudo obtener el hash del servidor
) else (
    REM Verificar si el commit local está en el servidor
    if "!LOCAL_HASH!"=="!SERVIDOR_HASH!" (
        echo    El servidor ya tiene el commit local actual
    ) else (
        REM Verificar si el commit local está en el historial del servidor
        if exist "%SSH_KEY%" (
            ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log --oneline | grep \"!LOCAL_HASH:~0,7!\" > /dev/null 2>&1"
        ) else (
            ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log --oneline | grep \"!LOCAL_HASH:~0,7!\" > /dev/null 2>&1"
        )
        if errorlevel 1 (
            echo    Los siguientes commits locales NO estan en el servidor:
            git log !SERVIDOR_HASH!..!LOCAL_HASH! --oneline 2>nul
            if errorlevel 1 (
                echo    (Mostrando commits locales no en origin/developer:)
                git log origin/%BRANCH%..HEAD --oneline
            )
        ) else (
            echo    El commit local esta en el historial del servidor
        )
    )
)
echo.

REM Resumen de sincronización
echo ============================================
echo   RESUMEN DE SINCRONIZACION
echo ============================================
echo.

if "!LOCAL_HASH!"=="!ORIGIN_HASH!" (
    echo [OK] Local y Origin/Developer estan sincronizados
) else (
    echo [PENDIENTE] Local tiene commits que no estan en Origin/Developer
    echo            Ejecute: git push origin %BRANCH%
)
echo.

if "!ORIGIN_HASH!"=="!SERVIDOR_HASH!" (
    echo [OK] Origin/Developer y Servidor estan sincronizados
) else (
    echo [PENDIENTE] Origin/Developer tiene commits que no estan en el Servidor
    echo            Ejecute: scripts\deploy_app.bat o scripts\commit_and_pull_servidor.bat
)
echo.

if "!LOCAL_HASH!"=="!SERVIDOR_HASH!" (
    echo [OK] Local y Servidor estan sincronizados
) else if "!SERVIDOR_HASH!"=="unknown" (
    echo [ERROR] No se pudo verificar el estado del servidor
) else (
    echo [PENDIENTE] Local y Servidor NO estan sincronizados
    echo            Sincronice primero Local con Origin, luego actualice el Servidor
)
echo.

echo ============================================
echo   FIN DE COMPARACION
echo ============================================
echo.

pause

