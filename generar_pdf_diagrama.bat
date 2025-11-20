@echo off
REM Script para generar PDF directamente desde diagrama Draw.io
REM Uso: generar_pdf_diagrama.bat [archivo.xml] [archivo_salida.pdf]

setlocal enabledelayedexpansion

set "ARCHIVO_XML=%~1"
set "ARCHIVO_PDF=%~2"

REM Si no se especifica archivo, usar el por defecto
if "%ARCHIVO_XML%"=="" (
    set "ARCHIVO_XML=c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19.drawio.xml"
    echo ============================================================
    echo GENERADOR DE PDF DESDE DIAGRAMA DRAW.IO
    echo ============================================================
    echo.
    echo Usando archivo por defecto: %ARCHIVO_XML%
    echo.
)

if not exist "%ARCHIVO_XML%" (
    echo ERROR: El archivo no existe: %ARCHIVO_XML%
    echo.
    pause
    exit /b 1
)

REM Determinar nombre del PDF de salida
if "%ARCHIVO_PDF%"=="" (
    for %%F in ("%ARCHIVO_XML%") do set "ARCHIVO_PDF=%%~dpnF.pdf"
)

echo ============================================================
echo GENERANDO PDF DESDE DIAGRAMA DRAW.IO
echo ============================================================
echo.
echo Archivo origen: %ARCHIVO_XML%
echo Archivo destino: %ARCHIVO_PDF%
echo.

REM Método 1: Intentar usar Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [1/3] Usando script Python...
    python generar_pdf_diagrama.py "%ARCHIVO_XML%" "%ARCHIVO_PDF%"
    if exist "%ARCHIVO_PDF%" (
        echo.
        echo ============================================================
        echo PDF GENERADO EXITOSAMENTE
        echo ============================================================
        echo Archivo: %ARCHIVO_PDF%
        echo.
        echo Abriendo carpeta...
        for %%F in ("%ARCHIVO_PDF%") do explorer "%%~dpF"
        echo.
        echo ¿Deseas abrir el PDF? (S/N): 
        set /p ABRIR=
        if /i "!ABRIR!"=="S" (
            start "" "%ARCHIVO_PDF%"
        )
        goto :end
    )
)

REM Método 2: Intentar Draw.io CLI
drawio --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [2/3] Usando Draw.io CLI...
    drawio --export --format pdf --output "%ARCHIVO_PDF%" --border 10 "%ARCHIVO_XML%"
    if %errorlevel% equ 0 (
        if exist "%ARCHIVO_PDF%" (
            echo.
            echo ============================================================
            echo PDF GENERADO EXITOSAMENTE
            echo ============================================================
            echo Archivo: %ARCHIVO_PDF%
            echo.
            echo Abriendo carpeta...
            for %%F in ("%ARCHIVO_PDF%") do explorer "%%~dpF"
            goto :end
        )
    )
)

REM Método 3: Intentar Draw.io Desktop
echo [3/3] Buscando Draw.io Desktop...
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
    echo Draw.io Desktop encontrado: !DRAWIO_PATH!
    echo.
    echo Intentando exportar...
    "!DRAWIO_PATH!" --export --format pdf --output "%ARCHIVO_PDF%" --border 10 "%ARCHIVO_XML%"
    timeout /t 2 >nul
    if exist "%ARCHIVO_PDF%" (
        echo.
        echo ============================================================
        echo PDF GENERADO EXITOSAMENTE
        echo ============================================================
        echo Archivo: %ARCHIVO_PDF%
        echo.
        echo Abriendo carpeta...
        for %%F in ("%ARCHIVO_PDF%") do explorer "%%~dpF"
        goto :end
    ) else (
        echo.
        echo Abriendo Draw.io Desktop para exportación manual...
        echo.
        echo INSTRUCCIONES:
        echo 1. En Draw.io Desktop, presiona Ctrl+Shift+E
        echo 2. Guarda como: %ARCHIVO_PDF%
        echo.
        start "" "!DRAWIO_PATH!" "%ARCHIVO_XML%"
        goto :end
    )
)

REM Si nada funciona, mostrar instrucciones
echo.
echo ============================================================
echo NO SE PUDO GENERAR EL PDF AUTOMATICAMENTE
echo ============================================================
echo.
echo OPCIONES:
echo.
echo 1. INSTALAR DRAW.IO CLI:
echo    npm install -g @drawio/cli
echo    Luego ejecuta este script nuevamente
echo.
echo 2. INSTALAR DRAW.IO DESKTOP:
echo    https://github.com/jgraph/drawio-desktop/releases
echo    Luego ejecuta este script nuevamente
echo.
echo 3. EXPORTACIÓN MANUAL:
echo    a) Abre: %ARCHIVO_XML%
echo    b) En https://app.diagrams.net:
echo       - Archivo ^> Abrir desde ^> Dispositivo
echo       - Selecciona el archivo XML
echo       - Archivo ^> Exportar como ^> PDF
echo       - Guarda como: %ARCHIVO_PDF%
echo.
echo Abriendo Draw.io online...
start https://app.diagrams.net/
timeout /t 2 >nul
start "" "%ARCHIVO_XML%"

:end
echo.
pause

