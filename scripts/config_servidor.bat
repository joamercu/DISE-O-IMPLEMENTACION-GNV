@echo off
REM ============================================
REM Configuración de variables para despliegue
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   CONFIGURACION DE DESPLIEGUE SERVIDOR
echo ============================================
echo.

REM Variables de configuración del servidor
set SERVIDOR_IP=72.61.10.156
set SERVIDOR_USUARIO=root
set SERVIDOR_RUTA=/var/www/gnv-app
set BRANCH=developer

REM Obtener rutas absolutas con comillas para manejar espacios
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "SSH_KEY=%PROJECT_DIR%\ssh_keys\gnv_server_key"
set "LOGS_DIR=%PROJECT_DIR%\logs_deploy"

REM Crear directorio de logs si no existe
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

REM Guardar configuración en archivo
set "CONFIG_FILE=%SCRIPT_DIR%deploy_config.txt"

REM Guardar sin espacios al final (usando > para sobrescribir cada vez)
> "%CONFIG_FILE%" echo SERVIDOR_IP=%SERVIDOR_IP%
>> "%CONFIG_FILE%" echo SERVIDOR_USUARIO=%SERVIDOR_USUARIO%
>> "%CONFIG_FILE%" echo SERVIDOR_RUTA=%SERVIDOR_RUTA%
>> "%CONFIG_FILE%" echo BRANCH=%BRANCH%
>> "%CONFIG_FILE%" echo SSH_KEY=%SSH_KEY%
>> "%CONFIG_FILE%" echo LOGS_DIR=%LOGS_DIR%

echo Configuracion guardada:
echo   - IP Servidor: %SERVIDOR_IP%
echo   - Usuario: %SERVIDOR_USUARIO%
echo   - Ruta: %SERVIDOR_RUTA%
echo   - Branch: %BRANCH%
echo   - Clave SSH: %SSH_KEY%
echo   - Logs: %LOGS_DIR%
echo.
echo Si necesita cambiar estos valores, edite: %CONFIG_FILE%
echo.

pause

