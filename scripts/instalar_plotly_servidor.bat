@echo off
REM ============================================
REM Script para instalar Plotly en el servidor
REM Soluciona el error: "⚠️ Plotly no está disponible. Mostrando datos en tabla."
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   INSTALACION DE PLOTLY EN EL SERVIDOR
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
set "SSH_KEY=%SSH_KEY: =%"

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

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo Ruta del proyecto: %SERVIDOR_RUTA%
echo.

REM Construir comando SSH
set SSH_CMD=ssh
if not "%SSH_KEY%"=="" (
    set SSH_CMD=!SSH_CMD! -i "%SSH_KEY%"
)
set SSH_CMD=!SSH_CMD! %SERVIDOR_USUARIO%@%SERVIDOR_IP%

REM Verificar si el script existe en el servidor
echo [1/3] Verificando script de instalacion en el servidor...
%SSH_CMD% "test -f %SERVIDOR_RUTA%/scripts/instalar_plotly_servidor.sh"
if errorlevel 1 (
    echo.
    echo El script no existe en el servidor. Subiendo script...
    
    REM Subir el script al servidor
    set SCP_CMD=scp
    if not "%SSH_KEY%"=="" (
        set SCP_CMD=!SCP_CMD! -i "%SSH_KEY%"
    )
    !SCP_CMD! "%~dp0instalar_plotly_servidor.sh" %SERVIDOR_USUARIO%@%SERVIDOR_IP%:%SERVIDOR_RUTA%/scripts/
    
    if errorlevel 1 (
        echo ERROR: No se pudo subir el script al servidor
        pause
        exit /b 1
    )
    
    REM Hacer el script ejecutable
    %SSH_CMD% "chmod +x %SERVIDOR_RUTA%/scripts/instalar_plotly_servidor.sh"
    
    if errorlevel 1 (
        echo ADVERTENCIA: No se pudo hacer el script ejecutable
        echo Intentando continuar...
    )
)

echo.
echo [2/3] Ejecutando instalacion de Plotly en el servidor...
echo.

REM Ejecutar el script en el servidor
%SSH_CMD% "cd %SERVIDOR_RUTA% && bash scripts/instalar_plotly_servidor.sh"

if errorlevel 1 (
    echo.
    echo ERROR: La instalacion fallo
    echo.
    echo Intentando instalacion manual...
    echo.
    
    REM Intentar instalación manual
    echo [3/3] Instalando Plotly manualmente...
    %SSH_CMD% "cd %SERVIDOR_RUTA% && pip3 install --upgrade plotly>=5.17.0 --break-system-packages"
    
    if errorlevel 1 (
        echo.
        echo ERROR: La instalacion manual tambien fallo
        echo.
        echo Por favor, conectese al servidor y ejecute manualmente:
        echo   pip3 install --upgrade plotly^>=5.17.0 --break-system-packages
        echo.
        pause
        exit /b 1
    )
) else (
    echo.
    echo [3/3] Verificando instalacion...
    %SSH_CMD% "python3 -c 'import plotly; import plotly.express as px; print(\"Plotly version:\", plotly.__version__)'"
)

echo.
echo ============================================
echo   INSTALACION COMPLETADA
echo ============================================
echo.
echo IMPORTANTE: Si Streamlit esta corriendo, reinicie el servidor
echo   para que los cambios surtan efecto.
echo.
pause

