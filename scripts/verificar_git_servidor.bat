@echo off
REM ============================================
REM Script para verificar el estado de Git en el servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   VERIFICAR ESTADO GIT EN EL SERVIDOR
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

REM Construir comando SSH
if exist "%SSH_KEY%" (
    set "SSH_CMD=ssh -i \"%SSH_KEY%\""
) else (
    set "SSH_CMD=ssh"
)

REM Verificar conexión SSH
echo Verificando conexion SSH...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "echo 'Conexion exitosa'" >nul 2>&1
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "echo 'Conexion exitosa'" >nul 2>&1
)
if errorlevel 1 (
    echo ERROR: No se pudo conectar al servidor.
    echo Verifique:
    echo   1. La clave SSH esta en: %SSH_KEY%
    echo   2. El servidor es accesible: %SERVIDOR_IP%
    echo   3. El usuario tiene permisos: %SERVIDOR_USUARIO%
    pause
    exit /b 1
)

echo Conexion SSH exitosa.
echo.
echo ============================================
echo   ESTADO DEL REPOSITORIO GIT
echo ============================================
echo.

REM Verificar si existe repositorio git
echo [1] Verificando si existe repositorio Git...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status > /dev/null 2>&1"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status > /dev/null 2>&1"
)
if errorlevel 1 (
    echo   ERROR: No se encuentra un repositorio Git en %SERVIDOR_RUTA%
    echo   Necesita clonar el repositorio primero.
    pause
    exit /b 1
)
echo   OK: Repositorio Git encontrado
echo.

REM Estado del repositorio
echo [2] Estado del repositorio:
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git status"
)
echo.

REM Branch actual
echo [3] Branch actual:
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git branch --show-current"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git branch --show-current"
)
echo.

REM Últimos commits
echo [4] Ultimos 5 commits:
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log --oneline -5"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log --oneline -5"
)
echo.

REM Información del commit actual
echo [5] Informacion del commit actual (HEAD):
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:'Hash: %%H%%nAutor: %%an <%%ae>%%nFecha: %%ad%%nMensaje: %%s' --date=format:'%%Y-%%m-%%d %%H:%%M:%%S'"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git log -1 --pretty=format:'Hash: %%H%%nAutor: %%an <%%ae>%%nFecha: %%ad%%nMensaje: %%s' --date=format:'%%Y-%%m-%%d %%H:%%M:%%S'"
)
echo.
echo.

REM Verificar si hay cambios sin commitear
echo [6] Verificando cambios sin commitear:
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git diff --stat"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git diff --stat"
)
echo.

REM Verificar estado con remoto
echo [7] Estado con el remoto (origin/%BRANCH%):
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git fetch origin --quiet && git status -sb"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git fetch origin --quiet && git status -sb"
)
echo.

REM URL del remoto
echo [8] URL del repositorio remoto:
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git remote get-url origin"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && git remote get-url origin"
)
echo.

REM Comparar commits local vs remoto
echo [9] Comparacion con remoto:
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && echo Commits locales no en remoto: && git log origin/%BRANCH%..HEAD --oneline && echo. && echo Commits remotos no en local: && git log HEAD..origin/%BRANCH% --oneline"
) else (
    ssh "%SERVIDOR_USUARIO%@%SERVIDOR_IP%" "cd %SERVIDOR_RUTA% && echo Commits locales no en remoto: && git log origin/%BRANCH%..HEAD --oneline && echo. && echo Commits remotos no en local: && git log HEAD..origin/%BRANCH% --oneline"
)
echo.

echo ============================================
echo   VERIFICACION COMPLETA
echo ============================================
echo.

pause

