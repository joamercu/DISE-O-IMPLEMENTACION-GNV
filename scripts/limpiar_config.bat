@echo off
REM ============================================
REM Script para limpiar espacios en blanco del archivo de configuración
REM ============================================

setlocal enabledelayedexpansion

set CONFIG_FILE=%~dp0deploy_config.txt

if not exist "%CONFIG_FILE%" (
    echo ERROR: Archivo de configuracion no encontrado.
    pause
    exit /b 1
)

echo Limpiando espacios en blanco del archivo de configuracion...
echo.

REM Leer y limpiar
(for /f "usebackq tokens=1,* delims==" %%a in ("%CONFIG_FILE%") do (
    set "VAR=%%a"
    set "VAL=%%b"
    REM Eliminar espacios al inicio y final
    set "VAL=!VAL: =!"
    echo !VAR!=!VAL!
)) > "%CONFIG_FILE%.tmp"

move /y "%CONFIG_FILE%.tmp" "%CONFIG_FILE%" >nul

echo Archivo de configuracion limpiado exitosamente.
echo.
pause

