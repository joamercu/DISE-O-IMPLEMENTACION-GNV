@echo off
REM ============================================
REM Script para verificar la configuración SSH
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   VERIFICACION DE CONFIGURACION SSH
echo ============================================
echo.

REM Cargar configuración si existe
set CONFIG_FILE=%~dp0deploy_config.txt
set SSH_KEY=
set SERVIDOR_IP=
set SERVIDOR_USUARIO=

if exist "%CONFIG_FILE%" (
    echo Leyendo configuracion...
    for /f "usebackq tokens=1,2 delims==" %%a in ("%CONFIG_FILE%") do (
        if "%%a"=="SSH_KEY" set SSH_KEY=%%b
        if "%%a"=="SERVIDOR_IP" set SERVIDOR_IP=%%b
        if "%%a"=="SERVIDOR_USUARIO" set SERVIDOR_USUARIO=%%b
    )
)

REM Verificar si existe clave SSH
echo ===== VERIFICANDO CLAVE SSH =====
echo.

if "%SSH_KEY%"=="" (
    echo ADVERTENCIA: No se encontro configuracion de clave SSH.
    echo.
    set KEY_DIR=%~dp0..\ssh_keys\gnv_server_key
    if exist "!KEY_DIR!" (
        echo Clave encontrada en ubicacion por defecto: !KEY_DIR!
        set SSH_KEY=!KEY_DIR!
    ) else (
        echo Buscando clave en ubicaciones comunes...
        if exist "%USERPROFILE%\.ssh\id_ed25519" (
            echo Clave encontrada en: %USERPROFILE%\.ssh\id_ed25519
            set SSH_KEY=%USERPROFILE%\.ssh\id_ed25519
        ) else (
            echo ERROR: No se encontro ninguna clave SSH.
            echo.
            echo Ejecute: scripts\generar_clave_ssh.bat
            echo.
            pause
            exit /b 1
        )
    )
) else (
    echo Clave configurada: %SSH_KEY%
)

REM Verificar que existe la clave privada
if not exist "%SSH_KEY%" (
    echo ERROR: La clave privada no existe en: %SSH_KEY%
    echo.
    pause
    exit /b 1
)

echo Clave privada encontrada: %SSH_KEY%
echo.

REM Verificar que existe la clave pública
set PUBLIC_KEY=%SSH_KEY%.pub
if not exist "%PUBLIC_KEY%" (
    echo ADVERTENCIA: No se encontro la clave publica en: %PUBLIC_KEY%
) else (
    echo Clave publica encontrada: %PUBLIC_KEY%
    echo.
    echo Contenido de la clave publica:
    type "%PUBLIC_KEY%"
    echo.
)

REM Verificar servidor
echo ===== VERIFICANDO CONFIGURACION DEL SERVIDOR =====
echo.

if "%SERVIDOR_IP%"=="" (
    set SERVIDOR_IP=72.61.10.156
    echo Usando IP por defecto: %SERVIDOR_IP%
) else (
    echo IP del servidor: %SERVIDOR_IP%
)

if "%SERVIDOR_USUARIO%"=="" (
    set SERVIDOR_USUARIO=root
    echo Usando usuario por defecto: %SERVIDOR_USUARIO%
) else (
    echo Usuario: %SERVIDOR_USUARIO%
)

echo.

REM Probar conexión SSH
echo ===== PROBANDO CONEXION SSH =====
echo.

echo Intentando conectar a %SERVIDOR_USUARIO%@%SERVIDOR_IP%...
echo.

ssh -i "%SSH_KEY%" -o ConnectTimeout=5 -o BatchMode=yes %SERVIDOR_USUARIO%@%SERVIDOR_IP% "echo 'Conexion exitosa sin contraseña!'" 2>nul

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo conectar sin contraseña.
    echo.
    echo Posibles causas:
    echo   1. La clave publica no esta en el servidor
    echo   2. Los permisos en el servidor son incorrectos
    echo   3. El servidor no es accesible
    echo.
    echo Soluciones:
    echo   1. Ejecute: scripts\copiar_clave_servidor.bat
    echo   2. Verifique que el servidor este accesible
    echo   3. Verifique los permisos en el servidor:
    echo      chmod 700 ~/.ssh
    echo      chmod 600 ~/.ssh/authorized_keys
    echo.
    
    REM Intentar con contraseña
    echo Intentando conectar con contraseña...
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "echo 'Conexion exitosa (con contraseña)'"
    if errorlevel 1 (
        echo ERROR: No se pudo conectar al servidor.
    ) else (
        echo.
        echo ADVERTENCIA: La conexion funciona pero requiere contraseña.
        echo Ejecute: scripts\copiar_clave_servidor.bat
    )
) else (
    echo.
    echo ============================================
    echo   CONEXION SSH CONFIGURADA CORRECTAMENTE
    echo ============================================
    echo.
    echo Puede usar los scripts de despliegue sin problemas.
    echo.
)

echo.
pause

