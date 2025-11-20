@echo off
REM ============================================
REM Script maestro para desplegar completo
REM Despliega, inicia app y API en un solo paso
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   DESPLIEGUE COMPLETO AL SERVIDOR
echo ============================================
echo.

REM Verificar configuración
set CONFIG_FILE=%~dp0deploy_config.txt
if not exist "%CONFIG_FILE%" (
    echo ERROR: Archivo de configuracion no encontrado.
    echo.
    echo Ejecutando configuracion inicial...
    call "%~dp0config_servidor.bat"
    if errorlevel 1 (
        echo ERROR: No se pudo configurar el servidor.
        pause
        exit /b 1
    )
)

echo.
echo Este script realizara:
echo   1. Desplegar codigo desde branch developer
echo   2. Iniciar aplicacion Streamlit
echo   3. Iniciar API FastAPI
echo.
set /p CONFIRMAR="Desea continuar? (S/N): "
if /i not "%CONFIRMAR%"=="S" (
    echo Cancelado.
    pause
    exit /b 0
)

echo.
echo ============================================
echo   PASO 1: DESPLEGAR CODIGO
echo ============================================
call "%~dp0deploy_app.bat"
if errorlevel 1 (
    echo ERROR: El despliegue fallo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   PASO 2: INICIAR APLICACION
echo ============================================
call "%~dp0iniciar_app_servidor.bat"
if errorlevel 1 (
    echo ERROR: No se pudo iniciar la aplicacion.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   PASO 3: INICIAR API
echo ============================================
set /p INICIAR_API="Desea iniciar la API tambien? (S/N): "
if /i "%INICIAR_API%"=="S" (
    call "%~dp0iniciar_api_servidor.bat"
    if errorlevel 1 (
        echo ADVERTENCIA: No se pudo iniciar la API.
    )
)

echo.
echo ============================================
echo   DESPLIEGUE COMPLETO FINALIZADO
echo ============================================
echo.
echo La aplicacion esta disponible en:
echo   - http://gnv.weldtech.cloud
echo   - http://72.61.10.156:8501
echo.
if /i "%INICIAR_API%"=="S" (
    echo La API esta disponible en:
    echo   - http://api-gnv.weldtech.cloud
    echo   - http://72.61.10.156:8000
    echo   - http://72.61.10.156:8000/docs
    echo.
)
echo Para ver el estado, ejecute:
echo   scripts\estado_servidor.bat
echo.
echo Para ver logs, ejecute:
echo   scripts\ver_logs_servidor.bat
echo.

pause

