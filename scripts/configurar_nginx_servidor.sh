#!/bin/bash
# ============================================
# Script para configurar Nginx en el servidor
# Solo responde a gnv.weldtech.cloud
# ============================================

set -e

echo "============================================"
echo "  CONFIGURACION NGINX PARA GNV"
echo "============================================"
echo ""

# Verificar que nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo "ERROR: Nginx no está instalado."
    echo "Instale nginx con: apt-get update && apt-get install -y nginx"
    exit 1
fi

# Directorios de configuración
SITES_AVAILABLE="/etc/nginx/sites-available"
SITES_ENABLED="/etc/nginx/sites-enabled"
CONFIG_FILE="$SITES_AVAILABLE/gnv.weldtech.cloud"

echo "1. Verificando configuración actual..."
echo ""

# Mostrar configuraciones existentes
echo "Configuraciones actuales en sites-available:"
ls -la "$SITES_AVAILABLE/" | grep -E "\.(conf|nginx)" || echo "  (ninguna encontrada)"
echo ""

echo "Configuraciones habilitadas en sites-enabled:"
ls -la "$SITES_ENABLED/" | grep -E "\.(conf|nginx)" || echo "  (ninguna encontrada)"
echo ""

# Verificar si hay configuración para weldtech.cloud que apunte a GNV
echo "2. Verificando configuración de weldtech.cloud..."
if [ -f "$SITES_AVAILABLE/weldtech.cloud" ] || [ -f "$SITES_AVAILABLE/default" ]; then
    echo "   Revisando archivos de configuración..."
    if grep -r "server_name.*weldtech.cloud" "$SITES_AVAILABLE/" 2>/dev/null | grep -q "8501\|gnv"; then
        echo "   ⚠️  ADVERTENCIA: Se encontró configuración de weldtech.cloud apuntando a GNV"
        echo "   Esto debe corregirse manualmente."
    fi
fi
echo ""

# Crear configuración para gnv.weldtech.cloud
echo "3. Creando configuración para gnv.weldtech.cloud..."
cat > "$CONFIG_FILE" << 'EOF'
# ============================================
# Configuración Nginx para aplicación GNV
# Solo debe responder a gnv.weldtech.cloud
# ============================================

# Configuración para la aplicación Streamlit (puerto 8501)
server {
    listen 80;
    server_name gnv.weldtech.cloud;  # SOLO este dominio
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}

# Configuración para la API (puerto 8000)
server {
    listen 80;
    server_name api-gnv.weldtech.cloud;  # SOLO este dominio para la API
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "   ✓ Configuración creada en: $CONFIG_FILE"
echo ""

# Habilitar la configuración
echo "4. Habilitando configuración..."
if [ ! -L "$SITES_ENABLED/gnv.weldtech.cloud" ]; then
    ln -s "$CONFIG_FILE" "$SITES_ENABLED/gnv.weldtech.cloud"
    echo "   ✓ Enlace simbólico creado"
else
    echo "   ✓ Enlace simbólico ya existe"
fi
echo ""

# Verificar configuración de nginx
echo "5. Verificando configuración de nginx..."
if nginx -t; then
    echo "   ✓ Configuración válida"
else
    echo "   ✗ ERROR: Configuración inválida"
    exit 1
fi
echo ""

# Recargar nginx
echo "6. Recargando nginx..."
if systemctl reload nginx; then
    echo "   ✓ Nginx recargado correctamente"
else
    echo "   ✗ ERROR: No se pudo recargar nginx"
    exit 1
fi
echo ""

# Verificar que los servicios están corriendo
echo "7. Verificando servicios..."
if pgrep -f "streamlit.*calculos_combustible_vehicular" > /dev/null; then
    echo "   ✓ Streamlit está corriendo en puerto 8501"
else
    echo "   ⚠️  ADVERTENCIA: Streamlit no está corriendo"
fi

if pgrep -f "uvicorn.*api_endpoint" > /dev/null; then
    echo "   ✓ API está corriendo en puerto 8000"
else
    echo "   ⚠️  ADVERTENCIA: API no está corriendo"
fi
echo ""

echo "============================================"
echo "  CONFIGURACION COMPLETADA"
echo "============================================"
echo ""
echo "La aplicación GNV ahora solo responde a:"
echo "  - http://gnv.weldtech.cloud"
echo "  - http://api-gnv.weldtech.cloud"
echo ""
echo "Verificar con:"
echo "  curl -H 'Host: gnv.weldtech.cloud' http://localhost"
echo "  curl -H 'Host: api-gnv.weldtech.cloud' http://localhost"
echo ""

