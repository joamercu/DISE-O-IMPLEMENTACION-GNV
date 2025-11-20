#!/bin/bash
# ============================================
# Script de Diagnóstico Completo del Servidor
# Analiza todos los elementos del servidor Debian
# ============================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir secciones
print_section() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

print_subsection() {
    echo ""
    echo -e "${GREEN}--- $1 ---${NC}"
    echo ""
}

# Crear directorio de salida
OUTPUT_DIR="/tmp/diagnostico_servidor_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"
REPORT_FILE="$OUTPUT_DIR/reporte_completo.txt"

# Función para guardar en archivo y mostrar
log_and_print() {
    echo "$1" | tee -a "$REPORT_FILE"
}

# Iniciar reporte
{
    echo "============================================"
    echo "REPORTE DE DIAGNÓSTICO COMPLETO DEL SERVIDOR"
    echo "Fecha: $(date)"
    echo "Hostname: $(hostname)"
    echo "IP: $(hostname -I | awk '{print $1}')"
    echo "============================================"
    echo ""
} > "$REPORT_FILE"

# ============================================
# 1. INFORMACIÓN DEL SISTEMA
# ============================================
print_section "1. INFORMACIÓN DEL SISTEMA"

log_and_print "=== Sistema Operativo ==="
log_and_print "$(cat /etc/os-release 2>/dev/null || echo 'No disponible')"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Kernel ==="
log_and_print "Versión: $(uname -r)"
log_and_print "Arquitectura: $(uname -m)"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Uptime ==="
log_and_print "$(uptime)"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Hostname ==="
log_and_print "Hostname: $(hostname)"
log_and_print "FQDN: $(hostname -f 2>/dev/null || echo 'No disponible')"
echo "" | tee -a "$REPORT_FILE"

# ============================================
# 2. CERTIFICADOS SSL
# ============================================
print_section "2. CERTIFICADOS SSL"

log_and_print "=== Certificados Let's Encrypt ==="
if [ -d "/etc/letsencrypt/live" ]; then
    for domain_dir in /etc/letsencrypt/live/*; do
        if [ -d "$domain_dir" ]; then
            domain=$(basename "$domain_dir")
            log_and_print "Dominio: $domain"
            
            if [ -f "$domain_dir/fullchain.pem" ]; then
                log_and_print "  Certificado: $(openssl x509 -in "$domain_dir/fullchain.pem" -noout -subject 2>/dev/null || echo 'Error al leer')"
                log_and_print "  Emisor: $(openssl x509 -in "$domain_dir/fullchain.pem" -noout -issuer 2>/dev/null || echo 'Error al leer')"
                log_and_print "  Válido desde: $(openssl x509 -in "$domain_dir/fullchain.pem" -noout -startdate 2>/dev/null | cut -d= -f2 || echo 'Error al leer')"
                log_and_print "  Válido hasta: $(openssl x509 -in "$domain_dir/fullchain.pem" -noout -enddate 2>/dev/null | cut -d= -f2 || echo 'Error al leer')"
                
                # Verificar días restantes
                expiry=$(openssl x509 -in "$domain_dir/fullchain.pem" -noout -enddate 2>/dev/null | cut -d= -f2)
                if [ -n "$expiry" ]; then
                    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || echo "0")
                    now_epoch=$(date +%s)
                    days_left=$(( (expiry_epoch - now_epoch) / 86400 ))
                    if [ $days_left -lt 30 ]; then
                        log_and_print "  ⚠️  ADVERTENCIA: Certificado expira en $days_left días"
                    else
                        log_and_print "  ✓ Certificado válido por $days_left días más"
                    fi
                fi
                
                log_and_print "  Archivos:"
                log_and_print "    - fullchain.pem: $(ls -lh "$domain_dir/fullchain.pem" 2>/dev/null | awk '{print $5, $9}')"
                log_and_print "    - privkey.pem: $(ls -lh "$domain_dir/privkey.pem" 2>/dev/null | awk '{print $5, $9}')"
                log_and_print "    - cert.pem: $(ls -lh "$domain_dir/cert.pem" 2>/dev/null | awk '{print $5, $9}' || echo 'No existe')"
                log_and_print "    - chain.pem: $(ls -lh "$domain_dir/chain.pem" 2>/dev/null | awk '{print $5, $9}' || echo 'No existe')"
            fi
            echo "" | tee -a "$REPORT_FILE"
        fi
    done
else
    log_and_print "No se encontró directorio /etc/letsencrypt/live"
fi

log_and_print "=== Otros certificados SSL ==="
if [ -d "/etc/ssl/certs" ]; then
    log_and_print "Certificados del sistema encontrados:"
    find /etc/ssl/certs -name "*.pem" -o -name "*.crt" 2>/dev/null | head -10 | while read cert; do
        log_and_print "  - $cert"
    done
fi

log_and_print "=== Certificados en /etc/nginx ==="
find /etc/nginx -name "*.pem" -o -name "*.crt" -o -name "*.key" 2>/dev/null | while read cert; do
    log_and_print "  - $cert ($(ls -lh "$cert" 2>/dev/null | awk '{print $5}'))"
done

# ============================================
# 3. CONFIGURACIÓN NGINX
# ============================================
print_section "3. CONFIGURACIÓN NGINX"

log_and_print "=== Estado de Nginx ==="
if command -v nginx &> /dev/null; then
    log_and_print "Nginx instalado: ✓"
    log_and_print "Versión: $(nginx -v 2>&1)"
    
    if systemctl is-active --quiet nginx; then
        log_and_print "Estado: ✓ Activo"
    else
        log_and_print "Estado: ✗ Inactivo"
    fi
    
    if systemctl is-enabled --quiet nginx; then
        log_and_print "Habilitado al inicio: ✓"
    else
        log_and_print "Habilitado al inicio: ✗"
    fi
else
    log_and_print "Nginx no está instalado"
fi
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Configuración de Nginx ==="
if [ -d "/etc/nginx" ]; then
    log_and_print "Archivo principal: /etc/nginx/nginx.conf"
    log_and_print "Sitios disponibles:"
    if [ -d "/etc/nginx/sites-available" ]; then
        for site in /etc/nginx/sites-available/*; do
            if [ -f "$site" ]; then
                log_and_print "  - $(basename "$site")"
            fi
        done
    fi
    
    log_and_print "Sitios habilitados:"
    if [ -d "/etc/nginx/sites-enabled" ]; then
        for site in /etc/nginx/sites-enabled/*; do
            if [ -f "$site" ] && [ ! -L "$site" ] || [ -L "$site" ]; then
                log_and_print "  - $(basename "$site")"
                if [ -L "$site" ]; then
                    log_and_print "    → Enlaza a: $(readlink "$site")"
                fi
            fi
        done
    fi
    
    # Guardar configuraciones importantes
    if [ -f "/etc/nginx/nginx.conf" ]; then
        cp /etc/nginx/nginx.conf "$OUTPUT_DIR/nginx.conf" 2>/dev/null || true
    fi
    
    if [ -d "/etc/nginx/sites-enabled" ]; then
        mkdir -p "$OUTPUT_DIR/nginx_sites"
        cp -r /etc/nginx/sites-enabled/* "$OUTPUT_DIR/nginx_sites/" 2>/dev/null || true
    fi
fi

log_and_print "=== Verificación de configuración Nginx ==="
if command -v nginx &> /dev/null; then
    if nginx -t 2>&1 | tee -a "$REPORT_FILE"; then
        log_and_print "✓ Configuración válida"
    else
        log_and_print "✗ ERROR en configuración"
    fi
fi

# ============================================
# 4. SERVICIOS Y PROCESOS
# ============================================
print_section "4. SERVICIOS Y PROCESOS"

log_and_print "=== Servicios del sistema ==="
log_and_print "Servicios activos:"
systemctl list-units --type=service --state=running --no-pager | head -20 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Procesos relacionados con la aplicación ==="
log_and_print "Procesos Python/Streamlit:"
ps aux | grep -E "(streamlit|uvicorn|python.*app|gunicorn)" | grep -v grep | tee -a "$REPORT_FILE" || log_and_print "No se encontraron procesos"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Procesos Nginx ==="
ps aux | grep nginx | grep -v grep | tee -a "$REPORT_FILE" || log_and_print "Nginx no está corriendo"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Procesos Node.js ==="
ps aux | grep -E "(node|npm|pm2)" | grep -v grep | tee -a "$REPORT_FILE" || log_and_print "No se encontraron procesos Node.js"
echo "" | tee -a "$REPORT_FILE"

# ============================================
# 5. PUERTOS Y CONEXIONES DE RED
# ============================================
print_section "5. PUERTOS Y CONEXIONES DE RED"

log_and_print "=== Puertos en escucha ==="
if command -v ss &> /dev/null; then
    ss -tlnp | tee -a "$REPORT_FILE"
else
    netstat -tlnp 2>/dev/null | tee -a "$REPORT_FILE" || log_and_print "No se pudo obtener información de puertos"
fi
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Conexiones activas ==="
if command -v ss &> /dev/null; then
    ss -tn | head -20 | tee -a "$REPORT_FILE"
else
    netstat -tn 2>/dev/null | head -20 | tee -a "$REPORT_FILE" || log_and_print "No se pudo obtener conexiones"
fi
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Interfaces de red ==="
ip addr show | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Tabla de enrutamiento ==="
ip route show | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# ============================================
# 6. RECURSOS DEL SISTEMA
# ============================================
print_section "6. RECURSOS DEL SISTEMA"

log_and_print "=== Uso de disco ==="
df -h | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Espacio en directorios importantes ==="
for dir in /var/www /etc/nginx /etc/letsencrypt /home /root /tmp; do
    if [ -d "$dir" ]; then
        log_and_print "$dir: $(du -sh "$dir" 2>/dev/null | awk '{print $1}')"
    fi
done
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Memoria ==="
free -h | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== CPU ==="
log_and_print "Procesadores: $(nproc)"
log_and_print "Carga promedio: $(uptime | awk -F'load average:' '{print $2}')"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Top procesos por CPU ==="
ps aux --sort=-%cpu | head -10 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Top procesos por memoria ==="
ps aux --sort=-%mem | head -10 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# ============================================
# 7. USUARIOS Y PERMISOS
# ============================================
print_section "7. USUARIOS Y PERMISOS"

log_and_print "=== Usuarios del sistema ==="
log_and_print "Usuarios con shell:"
grep -E "/bin/(bash|sh)$" /etc/passwd | cut -d: -f1,3,6 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Usuarios conectados ==="
who | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Usuario actual ==="
log_and_print "Usuario: $(whoami)"
log_and_print "UID: $(id -u)"
log_and_print "GID: $(id -g)"
log_and_print "Grupos: $(groups)"
echo "" | tee -a "$REPORT_FILE"

# ============================================
# 8. SOFTWARE INSTALADO
# ============================================
print_section "8. SOFTWARE INSTALADO"

log_and_print "=== Versiones de software clave ==="
for cmd in python3 python node npm nginx certbot git curl wget; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd --version 2>&1 | head -1)
        log_and_print "$cmd: $version"
    else
        log_and_print "$cmd: No instalado"
    fi
done
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Paquetes Python instalados ==="
if command -v pip3 &> /dev/null; then
    pip3 list 2>/dev/null | head -30 | tee -a "$REPORT_FILE" || log_and_print "No se pudo obtener lista de paquetes"
else
    log_and_print "pip3 no está instalado"
fi
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Paquetes Node.js instalados globalmente ==="
if command -v npm &> /dev/null; then
    npm list -g --depth=0 2>/dev/null | head -20 | tee -a "$REPORT_FILE" || log_and_print "No se pudo obtener lista de paquetes"
else
    log_and_print "npm no está instalado"
fi
echo "" | tee -a "$REPORT_FILE"

# ============================================
# 9. ARCHIVOS DE CONFIGURACIÓN IMPORTANTES
# ============================================
print_section "9. ARCHIVOS DE CONFIGURACIÓN IMPORTANTES"

log_and_print "=== Archivos de configuración ==="
config_files=(
    "/etc/hosts"
    "/etc/hostname"
    "/etc/resolv.conf"
    "/etc/fstab"
    "/etc/crontab"
)

for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        log_and_print "✓ $file existe"
        cp "$file" "$OUTPUT_DIR/$(basename $file)" 2>/dev/null || true
    else
        log_and_print "✗ $file no existe"
    fi
done
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Tareas programadas (Cron) ==="
log_and_print "Crontab del root:"
crontab -l 2>/dev/null | tee -a "$REPORT_FILE" || log_and_print "No hay crontab para root"
echo "" | tee -a "$REPORT_FILE"

log_and_print "Cron del sistema:"
ls -la /etc/cron.* 2>/dev/null | tee -a "$REPORT_FILE" || log_and_print "No hay cron del sistema"
echo "" | tee -a "$REPORT_FILE"

# ============================================
# 10. LOGS Y ARCHIVOS DE LOG
# ============================================
print_section "10. LOGS Y ARCHIVOS DE LOG"

log_and_print "=== Logs del sistema ==="
log_and_print "Últimas 20 líneas de syslog:"
tail -20 /var/log/syslog 2>/dev/null | tee -a "$REPORT_FILE" || log_and_print "No se pudo leer syslog"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Logs de Nginx ==="
if [ -d "/var/log/nginx" ]; then
    log_and_print "Archivos de log de Nginx:"
    ls -lh /var/log/nginx/ | tee -a "$REPORT_FILE"
    echo "" | tee -a "$REPORT_FILE"
    
    log_and_print "Últimas 20 líneas de error.log:"
    tail -20 /var/log/nginx/error.log 2>/dev/null | tee -a "$REPORT_FILE" || log_and_print "No se pudo leer error.log"
    echo "" | tee -a "$REPORT_FILE"
fi

log_and_print "=== Logs de la aplicación ==="
if [ -d "/var/www/gnv-app/logs" ]; then
    log_and_print "Archivos de log de la aplicación:"
    ls -lh /var/www/gnv-app/logs/ 2>/dev/null | tee -a "$REPORT_FILE" || log_and_print "No hay logs"
    echo "" | tee -a "$REPORT_FILE"
fi

# ============================================
# 11. FIREWALL Y SEGURIDAD
# ============================================
print_section "11. FIREWALL Y SEGURIDAD"

log_and_print "=== Estado del firewall ==="
if command -v ufw &> /dev/null; then
    ufw status verbose | tee -a "$REPORT_FILE"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --list-all | tee -a "$REPORT_FILE"
elif command -v iptables &> /dev/null; then
    log_and_print "Reglas de iptables:"
    iptables -L -n -v | head -30 | tee -a "$REPORT_FILE"
else
    log_and_print "No se encontró firewall configurado"
fi
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Intentos de login fallidos ==="
log_and_print "Últimos intentos fallidos (últimas 10 líneas):"
grep "Failed password" /var/log/auth.log 2>/dev/null | tail -10 | tee -a "$REPORT_FILE" || log_and_print "No se encontraron intentos fallidos"
echo "" | tee -a "$REPORT_FILE"

# ============================================
# 12. INFORMACIÓN DE LA APLICACIÓN
# ============================================
print_section "12. INFORMACIÓN DE LA APLICACIÓN"

if [ -d "/var/www/gnv-app" ]; then
    log_and_print "=== Directorio de la aplicación ==="
    log_and_print "Ruta: /var/www/gnv-app"
    log_and_print "Propietario: $(stat -c '%U:%G' /var/www/gnv-app 2>/dev/null || echo 'No disponible')"
    log_and_print "Permisos: $(stat -c '%a' /var/www/gnv-app 2>/dev/null || echo 'No disponible')"
    log_and_print "Tamaño: $(du -sh /var/www/gnv-app 2>/dev/null | awk '{print $1}')"
    echo "" | tee -a "$REPORT_FILE"
    
    log_and_print "=== Estructura del directorio ==="
    tree -L 2 /var/www/gnv-app 2>/dev/null | head -30 | tee -a "$REPORT_FILE" || \
    find /var/www/gnv-app -maxdepth 2 -type d 2>/dev/null | head -20 | tee -a "$REPORT_FILE"
    echo "" | tee -a "$REPORT_FILE"
    
    log_and_print "=== Información de Git ==="
    if [ -d "/var/www/gnv-app/.git" ]; then
        cd /var/www/gnv-app
        log_and_print "Branch actual: $(git branch --show-current 2>/dev/null || echo 'No disponible')"
        log_and_print "Último commit:"
        git log -1 --pretty=format:"  Hash: %H%n  Autor: %an <%ae>%n  Fecha: %ad%n  Mensaje: %s" --date=iso 2>/dev/null | tee -a "$REPORT_FILE" || log_and_print "No se pudo obtener información de git"
        echo "" | tee -a "$REPORT_FILE"
        
        log_and_print "Estado del repositorio:"
        git status --short 2>/dev/null | head -10 | tee -a "$REPORT_FILE" || log_and_print "No se pudo obtener estado"
    fi
    echo "" | tee -a "$REPORT_FILE"
    
    log_and_print "=== Archivos de configuración de la app ==="
    for config_file in requirements.txt .env config.py settings.py; do
        if [ -f "/var/www/gnv-app/$config_file" ]; then
            log_and_print "✓ $config_file existe"
            cp "/var/www/gnv-app/$config_file" "$OUTPUT_DIR/app_$config_file" 2>/dev/null || true
        fi
    done
else
    log_and_print "El directorio /var/www/gnv-app no existe"
fi

# ============================================
# RESUMEN FINAL
# ============================================
print_section "RESUMEN FINAL"

log_and_print "=== Resumen de hallazgos ==="
log_and_print "Fecha del diagnóstico: $(date)"
log_and_print "Hostname: $(hostname)"
log_and_print "IP: $(hostname -I | awk '{print $1}')"
log_and_print "Uptime: $(uptime -p 2>/dev/null || uptime)"
log_and_print "Espacio en disco disponible: $(df -h / | tail -1 | awk '{print $4}')"
log_and_print "Memoria disponible: $(free -h | grep Mem | awk '{print $7}')"
echo "" | tee -a "$REPORT_FILE"

log_and_print "=== Archivos generados ==="
log_and_print "Reporte completo: $REPORT_FILE"
log_and_print "Directorio de salida: $OUTPUT_DIR"
log_and_print ""
log_and_print "Contenido del directorio:"
ls -lh "$OUTPUT_DIR" | tee -a "$REPORT_FILE"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}DIAGNÓSTICO COMPLETADO${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Reporte guardado en: ${YELLOW}$REPORT_FILE${NC}"
echo -e "Archivos de configuración en: ${YELLOW}$OUTPUT_DIR${NC}"
echo ""
echo "Para ver el reporte completo:"
echo "  cat $REPORT_FILE"
echo ""
echo "Para comprimir todos los archivos:"
echo "  tar -czf $OUTPUT_DIR.tar.gz $OUTPUT_DIR"
echo ""

