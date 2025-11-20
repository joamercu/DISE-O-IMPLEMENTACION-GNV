@echo off
REM ============================================
REM Script para ejecutar tests del sistema de notificaciones
REM ============================================

echo.
echo ============================================
echo   TEST DEL SISTEMA DE NOTIFICACIONES
echo ============================================
echo.

REM Verificar que Python esté disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

REM Ejecutar test
python scripts\test_sistema_notificaciones.py

echo.
pause

