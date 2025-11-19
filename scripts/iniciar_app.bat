@echo off
REM ============================================
REM Script para iniciar la aplicación GNV
REM CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL
REM ============================================

echo.
echo ============================================
echo   CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL
echo ============================================
echo.
echo Iniciando aplicacion Streamlit...
echo.

REM Cambiar al directorio src
cd /d "%~dp0src"

REM Verificar que streamlit esté instalado
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Streamlit no esta instalado.
    echo Por favor, instale las dependencias ejecutando:
    echo     pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Verificar que el archivo principal existe
if not exist "calculos_combustible_vehicular.py" (
    echo.
    echo ERROR: No se encuentra el archivo calculos_combustible_vehicular.py
    echo Asegurese de estar en el directorio correcto.
    echo.
    pause
    exit /b 1
)

REM Iniciar la aplicación
echo Iniciando servidor Streamlit...
echo.
echo La aplicacion se abrira automaticamente en su navegador.
echo Para detener el servidor, presione Ctrl+C
echo.
echo ============================================
echo.

streamlit run calculos_combustible_vehicular.py

REM Si el usuario cierra la aplicación, mostrar mensaje
if errorlevel 1 (
    echo.
    echo La aplicacion se ha cerrado.
    pause
)

