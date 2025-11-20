@echo off
REM ============================================
REM Script para configurar archivo .env
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   CONFIGURACION DE VARIABLES DE ENTORNO
echo ============================================
echo.

set ENV_FILE=.env
set ENV_EXAMPLE=.env.example

REM Verificar si .env.example existe
if not exist "%ENV_EXAMPLE%" (
    echo ERROR: No se encuentra el archivo .env.example
    echo Por favor, cree el archivo .env.example primero.
    pause
    exit /b 1
)

REM Si .env ya existe, preguntar si sobrescribir
if exist "%ENV_FILE%" (
    echo El archivo .env ya existe.
    set /p OVERWRITE="¿Desea sobrescribirlo? (s/n): "
    if /i not "!OVERWRITE!"=="s" (
        echo Operacion cancelada.
        pause
        exit /b 0
    )
)

echo.
echo Configurando variables de entorno...
echo.

REM Copiar .env.example a .env
copy "%ENV_EXAMPLE%" "%ENV_FILE%" >nul

echo Archivo .env creado desde .env.example
echo.
echo Por favor, edite el archivo .env y configure:
echo   - Credenciales de PostgreSQL
echo   - Configuracion de SMTP para emails
echo.
echo Archivo: %CD%\%ENV_FILE%
echo.

pause

