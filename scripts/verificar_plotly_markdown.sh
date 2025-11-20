#!/bin/bash
# ============================================
# Script para verificar Plotly y Markdown
# Verifica instalación, funcionalidad y compatibilidad
# Compatible con Debian 13+ y otros sistemas Linux
# ============================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  VERIFICACIÓN DE PLOTLY Y MARKDOWN${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Obtener directorio del script y proyecto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Si se pasa un argumento, usar ese como directorio del proyecto
if [ -n "$1" ]; then
    PROJECT_DIR="$1"
fi

echo -e "${CYAN}Directorio del proyecto: ${PROJECT_DIR}${NC}"
echo ""

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Error: No se puede acceder al directorio del proyecto${NC}"
    echo -e "${RED}   Ruta intentada: ${PROJECT_DIR}${NC}"
    exit 1
}

# Detectar si hay un entorno virtual
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual detectado: $VIRTUAL_ENV${NC}"
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
    PIP_CMD="$VIRTUAL_ENV/bin/pip"
    BREAK_SYSTEM_PACKAGES=""
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
    # Debian 13+ requiere --break-system-packages para instalaciones globales
    BREAK_SYSTEM_PACKAGES="--break-system-packages"
    echo -e "${YELLOW}⚠️  Usando Python del sistema${NC}"
fi

# Verificar que Python está disponible
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Error: Python3 no está instalado o no está en el PATH${NC}"
    echo -e "${YELLOW}   Instale Python3: sudo apt-get install python3${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python detectado:${NC}"
$PYTHON_CMD --version
echo ""

# Verificar que el script de verificación existe
if [ ! -f "$PROJECT_DIR/verificar_plotly_markdown.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra el archivo verificar_plotly_markdown.py${NC}"
    echo -e "${RED}   Asegúrese de que el archivo existe en el directorio raíz del proyecto${NC}"
    exit 1
fi

echo -e "${CYAN}Ejecutando verificación...${NC}"
echo ""
echo -e "${BLUE}============================================${NC}"
echo ""

# Ejecutar el script de verificación
$PYTHON_CMD verificar_plotly_markdown.py
VERIFICACION_EXIT_CODE=$?

echo ""
echo -e "${BLUE}============================================${NC}"
echo ""

# Verificar el resultado
if [ $VERIFICACION_EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  VERIFICACIÓN COMPLETADA EXITOSAMENTE${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${GREEN}✓ Plotly y Markdown están funcionando correctamente${NC}"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}  VERIFICACIÓN COMPLETADA CON PROBLEMAS${NC}"
    echo -e "${RED}============================================${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Se encontraron problemas con Plotly o Markdown${NC}"
    echo ""
    echo -e "${CYAN}¿Desea instalar/corregir las dependencias ahora? (s/n)${NC}"
    read -r respuesta
    
    if [[ "$respuesta" =~ ^[Ss]$ ]]; then
        echo ""
        echo -e "${BLUE}Instalando dependencias...${NC}"
        echo ""
        
        # Actualizar pip primero
        $PIP_CMD install --upgrade pip $BREAK_SYSTEM_PACKAGES > /dev/null 2>&1 || true
        
        # Instalar Plotly y Markdown
        if $PIP_CMD install --upgrade "plotly>=5.17.0" "markdown>=3.4.0" $BREAK_SYSTEM_PACKAGES; then
            echo ""
            echo -e "${GREEN}✓ Dependencias instaladas correctamente${NC}"
            echo ""
            echo -e "${CYAN}Ejecutando verificación nuevamente...${NC}"
            echo ""
            $PYTHON_CMD verificar_plotly_markdown.py
            exit $?
        else
            echo ""
            echo -e "${RED}❌ Error: No se pudieron instalar las dependencias${NC}"
            echo -e "${YELLOW}   Intente instalarlas manualmente:${NC}"
            echo -e "${YELLOW}   $PIP_CMD install --upgrade plotly>=5.17.0 markdown>=3.4.0 $BREAK_SYSTEM_PACKAGES${NC}"
            echo ""
            exit 1
        fi
    else
        echo ""
        echo -e "${YELLOW}Instalación cancelada por el usuario${NC}"
        echo ""
        exit $VERIFICACION_EXIT_CODE
    fi
fi

