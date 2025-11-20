@echo off
REM ============================================
REM Script para generar clave SSH para el servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   GENERAR CLAVE SSH PARA SERVIDOR
echo ============================================
echo.

REM Variables
set EMAIL=joamercu@gmail.com
set KEY_NAME=gnv_server_key
set KEY_DIR=%~dp0..\ssh_keys
set PRIVATE_KEY=%KEY_DIR%\%KEY_NAME%
set PUBLIC_KEY=%KEY_DIR%\%KEY_NAME%.pub

REM Crear directorio para claves si no existe
if not exist "%KEY_DIR%" (
    echo Creando directorio para claves SSH...
    mkdir "%KEY_DIR%"
)

REM Verificar si la clave ya existe
if exist "%PRIVATE_KEY%" (
    echo.
    echo ADVERTENCIA: Ya existe una clave SSH en:
    echo   %PRIVATE_KEY%
    echo.
    set /p SOBRESCRIBIR="Desea generar una nueva clave? (S/N): "
    if /i not "!SOBRESCRIBIR!"=="S" (
        echo Cancelado.
        pause
        exit /b 0
    )
    echo Eliminando clave existente...
    del "%PRIVATE_KEY%" 2>nul
    del "%PUBLIC_KEY%" 2>nul
)

echo.
echo Generando clave SSH Ed25519...
echo Email: %EMAIL%
echo.
echo NOTA: Cuando se le solicite, puede:
echo   - Presionar Enter para usar la ruta por defecto
echo   - O ingresar una ruta personalizada
echo   - Presionar Enter para NO usar passphrase (mas facil)
echo     O ingresar una passphrase para mayor seguridad
echo.

REM Generar la clave SSH
ssh-keygen -t ed25519 -C "%EMAIL%" -f "%PRIVATE_KEY%"

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo generar la clave SSH.
    echo Verifique que tenga OpenSSH instalado.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   CLAVE SSH GENERADA EXITOSAMENTE
echo ============================================
echo.
echo Clave privada: %PRIVATE_KEY%
echo Clave publica:  %PUBLIC_KEY%
echo.

REM Mostrar la clave pública
echo ===== CLAVE PUBLICA (copie esto al servidor) =====
type "%PUBLIC_KEY%"
echo.

REM Actualizar configuración si existe
set CONFIG_FILE=%~dp0deploy_config.txt
if exist "%CONFIG_FILE%" (
    echo.
    echo Actualizando configuracion de despliegue...
    REM Leer configuración existente y actualizar SSH_KEY
    (for /f "usebackq tokens=1,2 delims==" %%a in ("%CONFIG_FILE%") do (
        if "%%a"=="SSH_KEY" (
            echo SSH_KEY=%PRIVATE_KEY%
        ) else (
            echo %%a=%%b
        )
    )) > "%CONFIG_FILE%.tmp"
    move /y "%CONFIG_FILE%.tmp" "%CONFIG_FILE%" >nul
    echo Configuracion actualizada.
)

echo.
echo ============================================
echo   SIGUIENTES PASOS
echo ============================================
echo.
echo 1. Copiar la clave publica al servidor:
echo.
echo    Opcion A - Automatico (recomendado):
echo      Ejecute: scripts\copiar_clave_servidor.bat
echo.
echo    Opcion B - Manual:
echo      Conectese al servidor y ejecute:
echo        mkdir -p ~/.ssh
echo        chmod 700 ~/.ssh
echo        nano ~/.ssh/authorized_keys
echo.
echo      Luego pegue el contenido de:
echo        %PUBLIC_KEY%
echo.
echo      Y guarde el archivo (Ctrl+O, Enter, Ctrl+X)
echo.
echo 2. Probar la conexion:
echo      ssh -i "%PRIVATE_KEY%" usuario@72.61.10.156
echo.
echo 3. Configurar despliegue:
echo      scripts\config_servidor.bat
echo.
echo ============================================
echo.

pause

