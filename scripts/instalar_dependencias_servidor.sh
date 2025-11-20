#!/bin/bash
# ============================================
# Script para instalar todas las dependencias
# necesarias en el servidor Debian
# Incluye dependencias del sistema para WeasyPrint
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
echo -e "${BLUE}  Instalación de Dependencias del Servidor${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Verificar que se ejecuta como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Este script requiere privilegios de administrador${NC}"
    echo -e "${YELLOW}Ejecutando con sudo...${NC}"
    exec sudo "$0" "$@"
fi

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Si se pasa un argumento, usar ese como directorio del proyecto
if [ -n "$1" ]; then
    PROJECT_DIR="$1"
fi

echo -e "${GREEN}Directorio del proyecto: ${PROJECT_DIR}${NC}"
echo ""

# Verificar que existe requirements.txt
if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    echo -e "${RED}❌ Error: No se encuentra requirements.txt en ${PROJECT_DIR}${NC}"
    exit 1
fi

# Paso 1: Actualizar lista de paquetes
echo -e "${BLUE}[1/4] Actualizando lista de paquetes...${NC}"
apt-get update -qq
echo -e "${GREEN}✓ Lista de paquetes actualizada${NC}"
echo ""

# Paso 2: Instalar dependencias del sistema para WeasyPrint
echo -e "${BLUE}[2/4] Instalando dependencias del sistema para WeasyPrint...${NC}"

# Detectar versión de Debian para usar el paquete correcto de gdk-pixbuf
DEBIAN_VERSION=$(cat /etc/debian_version 2>/dev/null | cut -d. -f1 || echo "0")
if [ "$DEBIAN_VERSION" -ge "13" ] || [ -f /etc/os-release ] && grep -q "VERSION_ID=\"13\"" /etc/os-release; then
    # Debian 13+ usa libgdk-pixbuf-xlib-2.0-0
    GDK_PIXBUF_PKG="libgdk-pixbuf-xlib-2.0-0"
else
    # Debian 11/12 y Ubuntu usan libgdk-pixbuf2.0-0
    GDK_PIXBUF_PKG="libgdk-pixbuf2.0-0"
fi

apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    ${GDK_PIXBUF_PKG} \
    libffi-dev \
    shared-mime-info > /dev/null 2>&1

echo -e "${GREEN}✓ Dependencias del sistema instaladas${NC}"
echo ""

# Paso 3: Instalar dependencias de Python
echo -e "${BLUE}[3/4] Instalando dependencias de Python...${NC}"

# Detectar si hay un entorno virtual
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual detectado: $VIRTUAL_ENV${NC}"
    PIP_CMD="$VIRTUAL_ENV/bin/pip"
    BREAK_SYSTEM_PACKAGES=""
else
    PIP_CMD="pip3"
    # Debian 13+ requiere --break-system-packages para instalaciones globales
    BREAK_SYSTEM_PACKAGES="--break-system-packages"
    echo -e "${YELLOW}⚠️  Instalando en el sistema (Debian 13 requiere --break-system-packages)${NC}"
fi

cd "$PROJECT_DIR"
$PIP_CMD install --upgrade pip $BREAK_SYSTEM_PACKAGES > /dev/null 2>&1
$PIP_CMD install -r requirements.txt $BREAK_SYSTEM_PACKAGES

echo -e "${GREEN}✓ Dependencias de Python instaladas${NC}"
echo ""

# Paso 4: Verificación
echo -e "${BLUE}[4/4] Verificando instalación...${NC}"

# Detectar comando de Python
if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
else
    PYTHON_CMD="python3"
fi

# Verificar WeasyPrint
if $PYTHON_CMD -c "from weasyprint import HTML; print('OK')" 2>/dev/null; then
    echo -e "${GREEN}✓ WeasyPrint funciona correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Advertencia: WeasyPrint no se pudo verificar${NC}"
    echo -e "${YELLOW}   Esto puede ser normal si no hay entorno virtual activo${NC}"
fi

# Verificar otras dependencias importantes
echo -e "${GREEN}✓ Verificando otras dependencias...${NC}"
$PYTHON_CMD -c "import streamlit; import pandas; import openpyxl; print('✓ Dependencias principales OK')" 2>/dev/null || echo -e "${YELLOW}⚠️  Algunas dependencias pueden no estar instaladas${NC}"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Instalación completada${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

