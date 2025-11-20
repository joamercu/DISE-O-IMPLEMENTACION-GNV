@echo off
REM Script para exportar diagrama Draw.io a PDF
REM Uso: exportar_diagrama_pdf.bat [archivo.xml]

setlocal enabledelayedexpansion

set "ARCHIVO_XML=%~1"

if "%ARCHIVO_XML%"=="" (
    echo ============================================================
    echo EXPORTADOR DE DIAGRAMAS DRAW.IO A PDF
    echo ============================================================
    echo.
    echo Uso: exportar_diagrama_pdf.bat [archivo.xml]
    echo.
    echo Si no especificas un archivo, se usara el archivo por defecto
    echo.
    set "ARCHIVO_XML=c:\Users\JOSE\Documents\diagrama_gnv_PETROLIQUIDOS_2024-12-19.drawio.xml"
    echo Usando archivo por defecto: %ARCHIVO_XML%
    echo.
)

if not exist "%ARCHIVO_XML%" (
    echo ERROR: El archivo no existe: %ARCHIVO_XML%
    echo.
    pause
    exit /b 1
)

echo ============================================================
echo EXPORTANDO DIAGRAMA A PDF
echo ============================================================
echo.
echo Archivo: %ARCHIVO_XML%
echo.

REM Intentar usar Python si está disponible
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Usando script Python...
    python exportar_diagrama_pdf.py "%ARCHIVO_XML%"
    goto :end
)

REM Si Python no está disponible, intentar draw.io CLI
drawio --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Usando draw.io CLI...
    for %%F in ("%ARCHIVO_XML%") do set "PDF_OUTPUT=%%~dpnF.pdf"
    drawio --export --format pdf --output "!PDF_OUTPUT!" "%ARCHIVO_XML%"
    if %errorlevel% equ 0 (
        echo.
        echo ============================================================
        echo PDF GENERADO EXITOSAMENTE
        echo ============================================================
        echo Archivo: !PDF_OUTPUT!
        echo.
        echo Abriendo carpeta...
        explorer "%%~dpF"
        goto :end
    )
)

REM Si nada funciona, abrir en navegador
echo.
echo ============================================================
echo ABRIENDO EN NAVEGADOR
echo ============================================================
echo.
echo No se encontro draw.io CLI ni Python.
echo Abriendo Draw.io online en el navegador...
echo.
echo INSTRUCCIONES:
echo 1. En Draw.io, ve a: Archivo ^> Abrir desde ^> Dispositivo
echo 2. Selecciona: %ARCHIVO_XML%
echo 3. Una vez abierto, ve a: Archivo ^> Exportar como ^> PDF
echo.
start https://app.diagrams.net/
timeout /t 2 >nul
start "" "%ARCHIVO_XML%"

:end
echo.
pause

