@echo off
echo ========================================
echo Iniciando API de Datos de Salida
echo ========================================
echo.

cd /d "%~dp0.."

echo Verificando dependencias...
python -m pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    python -m pip install -r requirements.txt
)

echo.
echo Iniciando servidor API...
echo.
echo El servidor estara disponible en:
echo   - http://localhost:8000
echo   - http://localhost:8000/docs (Documentacion interactiva)
echo   - http://localhost:8000/datos-salida (Endpoint principal)
echo.
echo Presione Ctrl+C para detener el servidor
echo.

set PYTHONPATH=%CD%
python -m uvicorn src.api_endpoint:app --reload --host 0.0.0.0 --port 8000

pause

