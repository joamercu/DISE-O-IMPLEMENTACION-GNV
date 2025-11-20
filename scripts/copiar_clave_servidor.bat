@echo off
REM ============================================
REM Script para copiar la clave pública al servidor
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   COPIAR CLAVE SSH AL SERVIDOR
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

REM Buscar clave pública
set KEY_DIR=%~dp0..\ssh_keys
set KEY_NAME=gnv_server_key
set PUBLIC_KEY=%KEY_DIR%\%KEY_NAME%.pub

REM Si no existe, buscar en la ruta de la clave privada
if not exist "%PUBLIC_KEY%" (
    if exist "%SSH_KEY%" (
        set PUBLIC_KEY=%SSH_KEY%.pub
    )
)

if not exist "%PUBLIC_KEY%" (
    echo ERROR: No se encontro la clave publica.
    echo Buscando en: %PUBLIC_KEY%
    echo.
    echo Ejecute primero: scripts\generar_clave_ssh.bat
    pause
    exit /b 1
)

echo Clave publica encontrada: %PUBLIC_KEY%
echo.

REM Solicitar usuario si no está en configuración
if "%SERVIDOR_USUARIO%"=="" (
    set /p SERVIDOR_USUARIO="Usuario del servidor (ej: root): "
)

if "%SERVIDOR_IP%"=="" (
    set /p SERVIDOR_IP="IP del servidor (ej: 72.61.10.156): "
)

echo.
echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo.

REM Verificar si ssh-copy-id está disponible (Windows no lo tiene por defecto)
where ssh-copy-id >nul 2>&1
if errorlevel 1 (
    echo Usando metodo manual para copiar la clave...
    echo.
    
    REM Leer la clave pública
    set /p PUB_KEY_CONTENT=<"%PUBLIC_KEY%"
    
    REM Crear directorio .ssh y agregar clave
    echo Ejecutando comandos en el servidor...
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo %PUB_KEY_CONTENT% >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'Clave agregada exitosamente'"
    ) else (
        ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo %PUB_KEY_CONTENT% >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'Clave agregada exitosamente'"
    )
    
    if errorlevel 1 (
        echo.
        echo ERROR: No se pudo copiar la clave automaticamente.
        echo.
        echo ===== INSTRUCCIONES MANUALES =====
        echo.
        echo 1. Copie el contenido de esta clave publica:
        echo    %PUBLIC_KEY%
        echo.
        type "%PUBLIC_KEY%"
        echo.
        echo 2. Conectese al servidor:
        echo    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP%
        echo.
        echo 3. Ejecute estos comandos:
        echo    mkdir -p ~/.ssh
        echo    chmod 700 ~/.ssh
        echo    nano ~/.ssh/authorized_keys
        echo.
        echo 4. Pegue el contenido de la clave publica
        echo    Guarde y salga (Ctrl+O, Enter, Ctrl+X)
        echo.
        echo 5. Ajuste permisos:
        echo    chmod 600 ~/.ssh/authorized_keys
        echo.
        pause
        exit /b 1
    )
) else (
    echo Usando ssh-copy-id...
    ssh-copy-id -i "%PUBLIC_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP%
    if errorlevel 1 (
        echo ERROR: No se pudo copiar la clave.
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo   CLAVE COPIADA EXITOSAMENTE
echo ============================================
echo.

REM Probar la conexión
echo Probando conexion sin contraseña...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "echo 'Conexion exitosa sin contraseña!'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "echo 'Conexion exitosa sin contraseña!'"
)
if errorlevel 1 (
    echo.
    echo ADVERTENCIA: La conexion sin contraseña no funciono.
    echo Verifique que la clave se haya copiado correctamente.
) else (
    echo.
    echo Conexion exitosa! Ya puede usar SSH sin contraseña.
)

echo.
pause

