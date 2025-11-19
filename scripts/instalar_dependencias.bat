@echo off
REM ============================================
REM Script para instalar dependencias
REM CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL
REM ============================================

echo.
echo ============================================
echo   Instalando dependencias
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor, instale Python desde https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Obtener directorio del script y navegar a la raíz del proyecto
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%.."

REM Verificar que requirements.txt existe
if not exist "requirements.txt" (
    echo [ERROR] No se encuentra requirements.txt
    echo.
    pause
    exit /b 1
)

echo Instalando paquetes desde requirements.txt...
echo.

REM Actualizar pip primero
python -m pip install --upgrade pip

REM Instalar dependencias
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un problema al instalar las dependencias
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Dependencias instaladas correctamente
echo ============================================
echo.
echo Puede iniciar la aplicacion ejecutando: scripts\iniciar_app.bat
echo.
pause

