@echo off
REM ============================================
REM Script para iniciar la aplicación GNV
REM CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL
REM Versión con información detallada
REM ============================================

title CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL

echo.
echo ============================================
echo   CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL
echo ============================================
echo.
echo Verificando entorno...
echo.

REM Obtener directorio del script
set SCRIPT_DIR=%~dp0
set SRC_DIR=%SCRIPT_DIR%src

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

REM Verificar que estamos en el directorio correcto
if not exist "%SRC_DIR%\calculos_combustible_vehicular.py" (
    echo.
    echo [ERROR] No se encuentra el archivo principal
    echo Ruta esperada: %SRC_DIR%\calculos_combustible_vehicular.py
    echo.
    pause
    exit /b 1
)

echo [OK] Archivo principal encontrado

REM Verificar dependencias
echo.
echo Verificando dependencias...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [ERROR] Streamlit no esta instalado
    echo.
    echo Instalando dependencias...
    pip install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

python -c "import pandas" 2>nul
if errorlevel 1 (
    echo [ADVERTENCIA] pandas no esta instalado
)

echo [OK] Dependencias verificadas

REM Verificar estructura de directorios
if not exist "%SCRIPT_DIR%data" (
    echo [ADVERTENCIA] Directorio 'data' no encontrado
    echo Algunas funcionalidades pueden no estar disponibles
)

echo [OK] Estructura de directorios verificada

REM Cambiar al directorio src
cd /d "%SRC_DIR%"

echo.
echo ============================================
echo   Iniciando aplicacion...
echo ============================================
echo.
echo La aplicacion se abrira automaticamente en su navegador.
echo URL: http://localhost:8501
echo.
echo Para detener el servidor, presione Ctrl+C
echo.
echo ============================================
echo.

REM Iniciar Streamlit
streamlit run calculos_combustible_vehicular.py --server.headless false

REM Manejar cierre
if errorlevel 1 (
    echo.
    echo ============================================
    echo   La aplicacion se ha cerrado
    echo ============================================
    echo.
    pause
)

