#!/bin/bash
# ============================================
# Script de Instalación de WeasyPrint en Debian/Ubuntu
# Instala todas las dependencias necesarias
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
echo -e "${BLUE}  Instalación de WeasyPrint en Debian/Ubuntu${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Verificar que se ejecuta como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Este script requiere privilegios de administrador${NC}"
    echo -e "${YELLOW}Ejecutando con sudo...${NC}"
    exec sudo "$0" "$@"
fi

# Verificar que es Debian/Ubuntu
if [ ! -f /etc/debian_version ] && [ ! -f /etc/os-release ]; then
    echo -e "${RED}❌ Error: Este script es solo para Debian/Ubuntu${NC}"
    exit 1
fi

# Detectar si es Debian o Ubuntu
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    OS="debian"
fi

echo -e "${GREEN}✓ Sistema detectado: ${OS} ${VERSION}${NC}"
echo ""

# Paso 1: Actualizar lista de paquetes
echo -e "${BLUE}[1/3] Actualizando lista de paquetes...${NC}"
apt-get update -qq
echo -e "${GREEN}✓ Lista de paquetes actualizada${NC}"
echo ""

# Paso 2: Instalar dependencias del sistema
echo -e "${BLUE}[2/3] Instalando dependencias del sistema...${NC}"

# Detectar versión de Debian para usar el paquete correcto de gdk-pixbuf
DEBIAN_VERSION=$(cat /etc/debian_version 2>/dev/null | cut -d. -f1 || echo "0")
if [ "$DEBIAN_VERSION" -ge "13" ] || [ -f /etc/os-release ] && grep -q "VERSION_ID=\"13\"" /etc/os-release; then
    # Debian 13+ usa libgdk-pixbuf-xlib-2.0-0
    GDK_PIXBUF_PKG="libgdk-pixbuf-xlib-2.0-0"
    echo -e "${YELLOW}Detectado Debian 13+, usando ${GDK_PIXBUF_PKG}${NC}"
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
    shared-mime-info

echo -e "${GREEN}✓ Dependencias del sistema instaladas${NC}"
echo ""

# Paso 3: Instalar WeasyPrint
echo -e "${BLUE}[3/3] Instalando WeasyPrint...${NC}"

# Detectar si hay un entorno virtual activo
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

# Instalar WeasyPrint
$PIP_CMD install --upgrade weasyprint $BREAK_SYSTEM_PACKAGES

echo -e "${GREEN}✓ WeasyPrint instalado${NC}"
echo ""

# Verificación
echo -e "${BLUE}Verificando instalación...${NC}"
if $PYTHON_CMD -c "from weasyprint import HTML; print('OK')" 2>/dev/null; then
    echo -e "${GREEN}✓ WeasyPrint funciona correctamente${NC}"
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  Instalación completada exitosamente${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    
    # Mostrar información de versión
    VERSION=$($PYTHON_CMD -c "import weasyprint; print(weasyprint.__version__)" 2>/dev/null || echo "desconocida")
    echo -e "${GREEN}Versión de WeasyPrint: ${VERSION}${NC}"
else
    echo -e "${RED}❌ Error: WeasyPrint no se pudo importar correctamente${NC}"
    echo -e "${YELLOW}Intenta ejecutar manualmente:${NC}"
    echo -e "${YELLOW}  $PYTHON_CMD -c \"from weasyprint import HTML\"${NC}"
    exit 1
fi

echo ""

