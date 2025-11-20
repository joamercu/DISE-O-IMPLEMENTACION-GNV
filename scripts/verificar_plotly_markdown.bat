@echo off
REM ============================================
REM Script para verificar Plotly y Markdown
REM Verifica instalación, funcionalidad y compatibilidad
REM ============================================

echo.
echo ============================================
echo   VERIFICACION DE PLOTLY Y MARKDOWN
echo ============================================
echo.

REM Cambiar al directorio raíz del proyecto
cd /d "%~dp0.."
if errorlevel 1 (
    echo.
    echo ERROR: No se puede acceder al directorio raiz del proyecto.
    echo Ruta intentada: %~dp0..
    echo.
    pause
    exit /b 1
)

REM Verificar que Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo Por favor, instale Python y asegurese de que este en el PATH.
    echo.
    pause
    exit /b 1
)

echo Python detectado:
python --version
echo.

REM Verificar que el script de verificación existe
if not exist "verificar_plotly_markdown.py" (
    echo.
    echo ERROR: No se encuentra el archivo verificar_plotly_markdown.py
    echo Asegurese de que el archivo existe en el directorio raiz del proyecto.
    echo.
    pause
    exit /b 1
)

echo Ejecutando verificacion...
echo.
echo ============================================
echo.

REM Ejecutar el script de verificación
python verificar_plotly_markdown.py

REM Capturar el código de salida
set VERIFICACION_EXIT_CODE=%ERRORLEVEL%

echo.
echo ============================================
echo.

REM Verificar el resultado
if %VERIFICACION_EXIT_CODE% EQU 0 (
    echo.
    echo ============================================
    echo   VERIFICACION COMPLETADA EXITOSAMENTE
    echo ============================================
    echo.
    echo Plotly y Markdown estan funcionando correctamente.
    echo.
) else (
    echo.
    echo ============================================
    echo   VERIFICACION COMPLETADA CON PROBLEMAS
    echo ============================================
    echo.
    echo Se encontraron problemas con Plotly o Markdown.
    echo.
    echo Desea instalar/corregir las dependencias ahora? (S/N)
    set /p INSTALAR="> "
    
    if /i "%INSTALAR%"=="S" (
        echo.
        echo Instalando dependencias...
        echo.
        pip install --upgrade plotly>=5.17.0 markdown>=3.4.0
        if errorlevel 1 (
            echo.
            echo ERROR: No se pudieron instalar las dependencias.
            echo Intente instalarlas manualmente:
            echo     pip install --upgrade plotly>=5.17.0 markdown>=3.4.0
            echo.
        ) else (
            echo.
            echo Dependencias instaladas. Ejecute la verificacion nuevamente.
            echo.
        )
    )
)

echo.
pause
exit /b %VERIFICACION_EXIT_CODE%

