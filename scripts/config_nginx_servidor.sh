#!/bin/bash
# ============================================
# Script para configurar Nginx en el servidor
# Solo gnv.weldtech.cloud debe apuntar a esta app
# ============================================

set -e

echo "============================================="
echo "  CONFIGURANDO NGINX PARA GNV"
echo "============================================="
echo

# Verificar que nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo "ERROR: Nginx no está instalado."
    echo "Instale nginx con: apt-get update && apt-get install -y nginx"
    exit 1
fi

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: Este script debe ejecutarse como root"
    echo "Use: sudo bash $0"
    exit 1
fi

# Crear backup de configuración actual
BACKUP_DIR=/etc/nginx/backup_gnv_$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"
echo "Creando backup en: $BACKUP_DIR"

# Backup de configuraciones existentes
if [ -f /etc/nginx/sites-available/gnv.weldtech.cloud ]; then
    cp /etc/nginx/sites-available/gnv.weldtech.cloud "$BACKUP_DIR/" 2>/dev/null || true
    echo "  - Backup de gnv.weldtech.cloud"
fi
if [ -f /etc/nginx/sites-enabled/gnv.weldtech.cloud ]; then
    cp /etc/nginx/sites-enabled/gnv.weldtech.cloud "$BACKUP_DIR/" 2>/dev/null || true
fi

# Crear configuración para gnv.weldtech.cloud
echo
echo "Creando configuración para gnv.weldtech.cloud..."
cat > /etc/nginx/sites-available/gnv.weldtech.cloud << 'NGINX_CONFIG'
# ============================================
# Configuración Nginx para aplicación GNV
# Solo debe responder a gnv.weldtech.cloud
# ============================================

# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name gnv.weldtech.cloud;
    return 301 https://$server_name$request_uri;
}

# Configuración para la aplicación Streamlit (puerto 8501) - HTTPS
server {
    listen 443 ssl http2;
    server_name gnv.weldtech.cloud;  # SOLO este dominio
    
    # Configuración SSL (ajustar rutas según tu certificado)
    # Si usas Let's Encrypt, las rutas típicas son:
    # ssl_certificate /etc/letsencrypt/live/gnv.weldtech.cloud/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/gnv.weldtech.cloud/privkey.pem;
    # Si tienes certificado en otra ubicación, actualiza estas rutas:
    ssl_certificate /etc/ssl/certs/gnv.weldtech.cloud.crt;
    ssl_certificate_key /etc/ssl/private/gnv.weldtech.cloud.key;
    
    # Configuración SSL recomendada
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
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

# Redirigir HTTP a HTTPS para API
server {
    listen 80;
    server_name api-gnv.weldtech.cloud;
    return 301 https://$server_name$request_uri;
}

# Configuración para la API (puerto 8000) - HTTPS
server {
    listen 443 ssl http2;
    server_name api-gnv.weldtech.cloud;  # SOLO este dominio para la API
    
    # Configuración SSL (ajustar rutas según tu certificado)
    ssl_certificate /etc/ssl/certs/api-gnv.weldtech.cloud.crt;
    ssl_certificate_key /etc/ssl/private/api-gnv.weldtech.cloud.key;
    
    # Configuración SSL recomendada
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_CONFIG

echo "  ✓ Archivo creado: /etc/nginx/sites-available/gnv.weldtech.cloud"

# Habilitar el sitio
echo
echo "Habilitando sitio..."
ln -sf /etc/nginx/sites-available/gnv.weldtech.cloud /etc/nginx/sites-enabled/
echo "  ✓ Enlace simbólico creado"

# Verificar configuraciones existentes
echo
echo "============================================="
echo "  VERIFICANDO CONFIGURACIONES EXISTENTES"
echo "============================================="
echo
echo "Configuraciones que contienen 'weldtech.cloud':"
grep -r "server_name.*weldtech.cloud" /etc/nginx/sites-available/ 2>/dev/null | while read line; do
    echo "  - $line"
done || echo "  (ninguna encontrada)"
echo

# Verificar que NO hay configuración incorrecta
echo "Verificando que weldtech.cloud NO apunta a GNV..."
WRONG_CONFIG=$(grep -r "server_name.*weldtech.cloud" /etc/nginx/sites-available/ 2>/dev/null | grep -v "gnv.weldtech.cloud" | grep -v "api-gnv.weldtech.cloud" || true)

if [ -n "$WRONG_CONFIG" ]; then
    echo "⚠ ADVERTENCIA: Se encontraron configuraciones que pueden ser incorrectas:"
    echo "$WRONG_CONFIG"
    echo
    echo "Verifique que weldtech.cloud apunte a OTRA aplicación, NO a esta."
    echo
else
    echo "  ✓ No se encontraron configuraciones conflictivas"
fi

# Verificar configuración de nginx
echo
echo "============================================="
echo "  VALIDANDO CONFIGURACION"
echo "============================================="
echo
if nginx -t; then
    echo "  ✓ Configuración válida"
else
    echo "  ✗ ERROR: Configuración inválida"
    echo
    echo "Revise los errores arriba y corrija la configuración."
    exit 1
fi

# Recargar nginx
echo
echo "============================================="
echo "  RECARGANDO NGINX"
echo "============================================="
echo
if systemctl reload nginx 2>/dev/null || service nginx reload 2>/dev/null; then
    echo "  ✓ Nginx recargado exitosamente"
else
    echo "  ✗ ERROR: No se pudo recargar nginx"
    exit 1
fi

# Verificar estado
echo
echo "============================================="
echo "  VERIFICACION FINAL"
echo "============================================="
echo
echo "Estado de nginx:"
systemctl status nginx --no-pager -l | head -n 5 || service nginx status | head -n 5
echo

echo "Configuraciones activas:"
ls -la /etc/nginx/sites-enabled/ | grep gnv || echo "  (ninguna encontrada)"
echo

echo "============================================="
echo "  CONFIGURACION COMPLETADA"
echo "============================================="
echo
echo "✓ La aplicación GNV ahora solo responde a:"
echo "  - http://gnv.weldtech.cloud"
echo "  - http://api-gnv.weldtech.cloud"
echo
echo "⚠ IMPORTANTE: Verifique que weldtech.cloud"
echo "  apunte a otra aplicación, NO a esta."
echo
echo "Backup guardado en: $BACKUP_DIR"
echo

