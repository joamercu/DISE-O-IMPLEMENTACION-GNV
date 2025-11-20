@echo off
REM ============================================
REM Script para solucionar el problema de Markdown
REM Verifica e instala markdown si es necesario
REM ============================================

echo.
echo ============================================
echo   SOLUCIONADOR DE PROBLEMA MARKDOWN
echo ============================================
echo.

REM Cambiar al directorio raíz del proyecto
cd /d "%~dp0.."
if errorlevel 1 (
    echo.
    echo ERROR: No se puede acceder al directorio raiz del proyecto.
    echo.
    pause
    exit /b 1
)

echo Verificando Python...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Paso 1: Verificando instalacion de Markdown
echo ============================================
echo.

python -c "import markdown; print(f'✅ Markdown instalado: version {markdown.__version__}')" 2>nul
if errorlevel 1 (
    echo ❌ Markdown NO esta instalado. Instalando...
    echo.
    python -m pip install --upgrade markdown>=3.4.0
    if errorlevel 1 (
        echo.
        echo ERROR: No se pudo instalar markdown.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ✅ Markdown instalado correctamente.
) else (
    echo ✅ Markdown ya esta instalado.
)

echo.
echo ============================================
echo Paso 2: Verificando importacion desde el proyecto
echo ============================================
echo.

python -c "import sys; sys.path.insert(0, 'src'); from utils.documentos_utils import convertir_md_a_html; print('✅ Importacion desde documentos_utils exitosa')" 2>nul
if errorlevel 1 (
    echo ❌ Error al importar desde documentos_utils.
    echo.
    echo Reinstalando todas las dependencias...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: No se pudieron instalar las dependencias.
        echo.
        pause
        exit /b 1
    )
) else (
    echo ✅ Importacion funcionando correctamente.
)

echo.
echo ============================================
echo Paso 3: Limpiando cache de Python
echo ============================================
echo.

REM Limpiar cache de Python (__pycache__)
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
echo ✅ Cache de Python limpiado.

echo.
echo ============================================
echo Paso 4: Verificacion final
echo ============================================
echo.

python verificar_plotly_markdown.py
set VERIFICACION_EXIT_CODE=%ERRORLEVEL%

echo.
echo ============================================
echo.

if %VERIFICACION_EXIT_CODE% EQU 0 (
    echo ✅ TODO FUNCIONA CORRECTAMENTE
    echo.
    echo IMPORTANTE: Si Streamlit esta corriendo, REINICIALO para que
    echo los cambios surtan efecto.
    echo.
    echo Para reiniciar Streamlit:
    echo   1. Detenlo con Ctrl+C
    echo   2. Ejecuta: scripts\iniciar_app.bat
    echo.
) else (
    echo ❌ AUN HAY PROBLEMAS
    echo.
    echo Por favor, ejecuta manualmente:
    echo   python -m pip install --upgrade markdown>=3.4.0
    echo   python -m pip install -r requirements.txt
    echo.
)

pause
exit /b %VERIFICACION_EXIT_CODE%

