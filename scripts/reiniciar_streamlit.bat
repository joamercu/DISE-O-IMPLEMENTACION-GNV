@echo off
REM ============================================
REM Script para reiniciar Streamlit correctamente
REM Mata procesos colgados y reinicia
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   REINICIAR STREAMLIT
echo ============================================
echo.

REM Cargar configuración
set CONFIG_FILE=%~dp0deploy_config.txt
if not exist "%CONFIG_FILE%" (
    echo ERROR: Archivo de configuracion no encontrado.
    echo Ejecute primero: config_servidor.bat
    pause
    exit /b 1
)

REM Leer configuración
for /f "usebackq tokens=1,2 delims==" %%a in ("%CONFIG_FILE%") do (
    set "%%a=%%b"
)

REM Validar variables
if "%SERVIDOR_IP%"=="" (
    echo ERROR: SERVIDOR_IP no esta configurado.
    pause
    exit /b 1
)
if "%SERVIDOR_USUARIO%"=="" (
    echo ERROR: SERVIDOR_USUARIO no esta configurado.
    pause
    exit /b 1
)
if "%SERVIDOR_RUTA%"=="" (
    echo ERROR: SERVIDOR_RUTA no esta configurado.
    pause
    exit /b 1
)

echo Servidor: %SERVIDOR_USUARIO%@%SERVIDOR_IP%
echo Ruta: %SERVIDOR_RUTA%
echo.

REM Paso 1: Detener todos los procesos de Streamlit
echo [1/4] Deteniendo procesos de Streamlit...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -9 -f 'streamlit.*calculos_combustible_vehicular' 2>/dev/null; sleep 2; pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null && echo '  ⚠ Algunos procesos aun estan corriendo' || echo '  ✓ Todos los procesos detenidos'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pkill -9 -f 'streamlit.*calculos_combustible_vehicular' 2>/dev/null; sleep 2; pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null && echo '  ⚠ Algunos procesos aun estan corriendo' || echo '  ✓ Todos los procesos detenidos'"
)
echo.

REM Paso 2: Verificar que el puerto esté libre
echo [2/4] Verificando que el puerto 8501 este libre...
timeout /t 3 >nul
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null" >nul 2>&1
)

if not errorlevel 1 (
    echo   ⚠ Puerto 8501 aun esta en uso
    echo   Intentando liberar el puerto...
    if exist "%SSH_KEY%" (
        ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "fuser -k 8501/tcp 2>/dev/null || true; sleep 2"
    ) else (
        ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "fuser -k 8501/tcp 2>/dev/null || true; sleep 2"
    )
    timeout /t 2 >nul
) else (
    echo   ✓ Puerto 8501 esta libre
)
echo.

REM Paso 3: Crear directorio de logs si no existe
echo [3/4] Preparando directorio de logs...
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "mkdir -p %SERVIDOR_RUTA%/logs && echo '  ✓ Directorio de logs listo'"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "mkdir -p %SERVIDOR_RUTA%/logs && echo '  ✓ Directorio de logs listo'"
)
echo.

REM Paso 4: Iniciar Streamlit
echo [4/4] Iniciando Streamlit...
echo   Esto puede tardar unos segundos...
echo.

REM Crear script de inicio mejorado
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > %SERVIDOR_RUTA%/start_app.sh << 'EOF'
#!/bin/bash
cd %SERVIDOR_RUTA%/src
export PYTHONPATH=%SERVIDOR_RUTA%

# Limpiar procesos anteriores
pkill -9 -f 'streamlit.*calculos_combustible_vehicular' 2>/dev/null || true
sleep 2

# Verificar que el puerto esté libre
if netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null; then
    echo 'ERROR: Puerto 8501 aun esta en uso'
    exit 1
fi

# Iniciar Streamlit
nohup streamlit run calculos_combustible_vehicular.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true > %SERVIDOR_RUTA%/logs/streamlit.log 2>&1 &
STREAMLIT_PID=\$!

# Esperar un momento
sleep 3

# Verificar que está corriendo
if ps -p \$STREAMLIT_PID > /dev/null; then
    echo \$STREAMLIT_PID > %SERVIDOR_RUTA%/logs/streamlit.pid
    echo 'Streamlit iniciado con PID: '\$STREAMLIT_PID
    
    # Verificar que está escuchando en el puerto
    sleep 2
    if netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null; then
        echo '✓ Streamlit esta escuchando en el puerto 8501'
    else
        echo '⚠ ADVERTENCIA: Streamlit no esta escuchando en el puerto 8501'
        echo 'Revise los logs: tail -f %SERVIDOR_RUTA%/logs/streamlit.log'
    fi
else
    echo 'ERROR: Streamlit no se inicio correctamente'
    echo 'Revise los logs: tail -f %SERVIDOR_RUTA%/logs/streamlit.log'
    exit 1
fi
EOF
chmod +x %SERVIDOR_RUTA%/start_app.sh" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "cat > %SERVIDOR_RUTA%/start_app.sh << 'EOF'
#!/bin/bash
cd %SERVIDOR_RUTA%/src
export PYTHONPATH=%SERVIDOR_RUTA%

# Limpiar procesos anteriores
pkill -9 -f 'streamlit.*calculos_combustible_vehicular' 2>/dev/null || true
sleep 2

# Verificar que el puerto esté libre
if netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null; then
    echo 'ERROR: Puerto 8501 aun esta en uso'
    exit 1
fi

# Iniciar Streamlit
nohup streamlit run calculos_combustible_vehicular.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true > %SERVIDOR_RUTA%/logs/streamlit.log 2>&1 &
STREAMLIT_PID=\$!

# Esperar un momento
sleep 3

# Verificar que está corriendo
if ps -p \$STREAMLIT_PID > /dev/null; then
    echo \$STREAMLIT_PID > %SERVIDOR_RUTA%/logs/streamlit.pid
    echo 'Streamlit iniciado con PID: '\$STREAMLIT_PID
    
    # Verificar que está escuchando en el puerto
    sleep 2
    if netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null; then
        echo '✓ Streamlit esta escuchando en el puerto 8501'
    else
        echo '⚠ ADVERTENCIA: Streamlit no esta escuchando en el puerto 8501'
        echo 'Revise los logs: tail -f %SERVIDOR_RUTA%/logs/streamlit.log'
    fi
else
    echo 'ERROR: Streamlit no se inicio correctamente'
    echo 'Revise los logs: tail -f %SERVIDOR_RUTA%/logs/streamlit.log'
    exit 1
fi
EOF
chmod +x %SERVIDOR_RUTA%/start_app.sh" >nul 2>&1
)

REM Ejecutar el script
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash %SERVIDOR_RUTA%/start_app.sh"
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "bash %SERVIDOR_RUTA%/start_app.sh"
)

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo iniciar Streamlit.
    echo.
    echo Revise los logs en el servidor:
    echo   ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "tail -f %SERVIDOR_RUTA%/logs/streamlit.log"
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   STREAMLIT REINICIADO
echo ============================================
echo.
echo Verificando estado final...
timeout /t 3 >nul

REM Verificación final
if exist "%SSH_KEY%" (
    ssh -i "%SSH_KEY%" %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null && netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null" >nul 2>&1
) else (
    ssh %SERVIDOR_USUARIO%@%SERVIDOR_IP% "pgrep -f 'streamlit.*calculos_combustible_vehicular' > /dev/null && netstat -tlnp 2>/dev/null | grep ':8501' > /dev/null || ss -tlnp 2>/dev/null | grep ':8501' > /dev/null" >nul 2>&1
)

if errorlevel 1 (
    echo   ✗ Streamlit NO esta funcionando correctamente
    echo   Revise los logs: scripts\ver_logs_servidor.bat
) else (
    echo   ✓ Streamlit esta corriendo y escuchando en el puerto 8501
    echo.
    echo   Ahora configure nginx si aun no lo ha hecho:
    echo     scripts\configurar_nginx.bat
)

echo.

pause

