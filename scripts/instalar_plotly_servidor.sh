#!/bin/bash
# ============================================
# Script para instalar Plotly en el servidor
# Soluciona el error: "⚠️ Plotly no está disponible. Mostrando datos en tabla."
# ============================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Instalación de Plotly en el Servidor${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Detectar si hay un entorno virtual
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual detectado: $VIRTUAL_ENV${NC}"
    PIP_CMD="$VIRTUAL_ENV/bin/pip"
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
    BREAK_SYSTEM_PACKAGES=""
else
    PIP_CMD="pip3"
    PYTHON_CMD="python3"
    # Debian 13+ requiere --break-system-packages para instalaciones globales
    BREAK_SYSTEM_PACKAGES="--break-system-packages"
    echo -e "${YELLOW}⚠️  Instalando en el sistema (Debian 13 requiere --break-system-packages)${NC}"
fi

# Verificar si Plotly ya está instalado
echo -e "${BLUE}[1/2] Verificando instalación actual de Plotly...${NC}"
if $PYTHON_CMD -c "import plotly; import plotly.express as px; print('OK')" 2>/dev/null; then
    PLOTLY_VERSION=$($PYTHON_CMD -c "import plotly; print(plotly.__version__)" 2>/dev/null || echo "desconocida")
    echo -e "${GREEN}✓ Plotly ya está instalado (versión: ${PLOTLY_VERSION})${NC}"
    echo -e "${YELLOW}¿Desea reinstalarlo? (s/n)${NC}"
    read -r respuesta
    if [[ ! "$respuesta" =~ ^[Ss]$ ]]; then
        echo -e "${GREEN}Instalación cancelada. Plotly ya está disponible.${NC}"
        exit 0
    fi
else
    echo -e "${YELLOW}⚠️  Plotly no está instalado${NC}"
fi

# Instalar Plotly
echo -e "${BLUE}[2/2] Instalando Plotly...${NC}"
$PIP_CMD install --upgrade pip $BREAK_SYSTEM_PACKAGES > /dev/null 2>&1
$PIP_CMD install --upgrade "plotly>=5.17.0" $BREAK_SYSTEM_PACKAGES

# Verificar instalación
echo -e "${BLUE}Verificando instalación...${NC}"
if $PYTHON_CMD -c "import plotly; import plotly.express as px; print('OK')" 2>/dev/null; then
    PLOTLY_VERSION=$($PYTHON_CMD -c "import plotly; print(plotly.__version__)" 2>/dev/null || echo "desconocida")
    echo -e "${GREEN}✓ Plotly instalado correctamente (versión: ${PLOTLY_VERSION})${NC}"
    echo -e "${GREEN}✓ Plotly Express disponible${NC}"
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  Instalación completada exitosamente${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${BLUE}Nota: Si está usando Streamlit, reinicie el servidor para que los cambios surtan efecto.${NC}"
    echo ""
else
    echo -e "${RED}❌ Error: No se pudo instalar Plotly${NC}"
    echo -e "${YELLOW}Intente ejecutar manualmente:${NC}"
    echo -e "${YELLOW}  $PIP_CMD install plotly>=5.17.0 $BREAK_SYSTEM_PACKAGES${NC}"
    exit 1
fi

