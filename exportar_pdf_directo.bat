@echo off
REM Script directo para exportar diagrama Draw.io a PDF
REM Busca draw.io desktop y lo usa si está disponible

setlocal enabledelayedexpansion

set "ARCHIVO_XML=c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19.drawio.xml"
set "PDF_OUTPUT=c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19.pdf"

if not exist "%ARCHIVO_XML%" (
    echo ERROR: El archivo no existe: %ARCHIVO_XML%
    pause
    exit /b 1
)

echo ============================================================
echo EXPORTANDO DIAGRAMA DRAW.IO A PDF
echo ============================================================
echo.
echo Archivo origen: %ARCHIVO_XML%
echo Archivo destino: %PDF_OUTPUT%
echo.

REM Método 1: Buscar Draw.io Desktop en ubicaciones comunes
set "DRAWIO_PATH="
if exist "%LOCALAPPDATA%\Programs\draw.io\draw.io.exe" (
    set "DRAWIO_PATH=%LOCALAPPDATA%\Programs\draw.io\draw.io.exe"
)
if exist "%PROGRAMFILES%\draw.io\draw.io.exe" (
    set "DRAWIO_PATH=%PROGRAMFILES%\draw.io\draw.io.exe"
)
if exist "%PROGRAMFILES(X86)%\draw.io\draw.io.exe" (
    set "DRAWIO_PATH=%PROGRAMFILES(X86)%\draw.io\draw.io.exe"
)

if not "!DRAWIO_PATH!"=="" (
    echo Encontrado Draw.io Desktop en: !DRAWIO_PATH!
    echo.
    echo Abriendo Draw.io Desktop...
    echo.
    echo INSTRUCCIONES:
    echo 1. El archivo se abrira en Draw.io Desktop
    echo 2. Presiona Ctrl+Shift+E para exportar a PDF
    echo 3. O ve a: Archivo ^> Exportar como ^> PDF
    echo 4. Guarda en: %PDF_OUTPUT%
    echo.
    start "" "!DRAWIO_PATH!" "%ARCHIVO_XML%"
    timeout /t 2 >nul
    goto :end
)

REM Método 2: Intentar draw.io CLI
drawio --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Usando draw.io CLI para exportar...
    drawio --export --format pdf --output "%PDF_OUTPUT%" --border 10 "%ARCHIVO_XML%"
    if %errorlevel% equ 0 (
        echo.
        echo ============================================================
        echo PDF GENERADO EXITOSAMENTE
        echo ============================================================
        echo Archivo: %PDF_OUTPUT%
        echo.
        echo Abriendo carpeta...
        explorer "c:\Users\JOSE\Documents"
        goto :end
    )
)

REM Método 3: Abrir en navegador con instrucciones
echo Draw.io Desktop no encontrado.
echo.
echo ============================================================
echo ABRIENDO EN NAVEGADOR
echo ============================================================
echo.
echo INSTRUCCIONES PARA EXPORTAR A PDF:
echo.
echo 1. En Draw.io online, ve a: Archivo ^> Abrir desde ^> Dispositivo
echo 2. Selecciona: %ARCHIVO_XML%
echo 3. Una vez abierto, presiona: Ctrl+Shift+E
echo    O ve a: Archivo ^> Exportar como ^> PDF
echo 4. Guarda como: diagrama_gnv_PETROLIQUIDOS_2024-12-19.pdf
echo.
echo Abriendo Draw.io online...
start https://app.diagrams.net/
timeout /t 2 >nul
start "" "%ARCHIVO_XML%"

:end
echo.
echo ============================================================
echo Para instalar Draw.io Desktop:
echo https://github.com/jgraph/drawio-desktop/releases
echo ============================================================
echo.
pause

