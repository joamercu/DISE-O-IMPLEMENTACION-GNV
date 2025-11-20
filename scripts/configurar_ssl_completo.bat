@echo off
REM ============================================
REM Script maestro para configurar SSL completo
REM Instala certificados y configura nginx
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   CONFIGURACION COMPLETA SSL Y NGINX
echo ============================================
echo.
echo Este script ejecutara en orden:
echo   1. Instalar/renovar certificados SSL
echo   2. Configurar nginx para todos los dominios
echo.
echo IMPORTANTE: Asegurese de que los dominios
echo apunten correctamente a este servidor antes
echo de continuar.
echo.
pause

REM Paso 1: Instalar certificados
echo.
echo ============================================
echo   PASO 1: INSTALAR CERTIFICADOS SSL
echo ============================================
echo.
call "%~dp0instalar_certificados_ssl.bat"

if errorlevel 1 (
    echo.
    echo ERROR: La instalacion de certificados fallo.
    echo Revise los errores y vuelva a intentar.
    pause
    exit /b 1
)

REM Paso 2: Configurar nginx
echo.
echo ============================================
echo   PASO 2: CONFIGURAR NGINX
echo ============================================
echo.
call "%~dp0configurar_nginx_completo_ssl.bat"

if errorlevel 1 (
    echo.
    echo ERROR: La configuracion de nginx fallo.
    echo Revise los errores y vuelva a intentar.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   CONFIGURACION COMPLETA FINALIZADA
echo ============================================
echo.
echo ✓ Certificados SSL instalados/renovados
echo ✓ Nginx configurado para todos los dominios
echo.
echo Los siguientes dominios estan configurados:
echo   - https://weldtech.cloud (aplicacion de login)
echo   - https://gnv.weldtech.cloud (aplicacion Streamlit)
echo   - https://api-gnv.weldtech.cloud (API)
echo.
echo Todos usan HTTPS con certificados validos.
echo.

pause

