# 🔧 Configuración de Nginx para GNV

## ⚠️ Problema Actual

La aplicación GNV está respondiendo en el dominio `weldtech.cloud` cuando **solo debe responder en `gnv.weldtech.cloud`**.

El dominio `weldtech.cloud` debe estar configurado para otra aplicación diferente.

## ✅ Solución

### 1. Verificar configuración actual de Nginx

Conéctate al servidor y revisa los archivos de configuración:

```bash
ssh root@72.61.10.156
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/
```

### 2. Configuración correcta para GNV

Crea o edita el archivo `/etc/nginx/sites-available/gnv.weldtech.cloud` con el siguiente contenido:

```nginx
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
```

### 3. Verificar que NO existe configuración para weldtech.cloud apuntando a GNV

**IMPORTANTE**: Asegúrate de que NO haya un archivo de configuración que tenga:

```nginx
server_name weldtech.cloud;  # ❌ ESTO NO DEBE APUNTAR A GNV
```

Si existe, debe apuntar a otra aplicación diferente.

### 4. Habilitar la configuración

```bash
# Crear enlace simbólico si no existe
ln -s /etc/nginx/sites-available/gnv.weldtech.cloud /etc/nginx/sites-enabled/

# Verificar la configuración
nginx -t

# Recargar nginx
systemctl reload nginx
```

### 5. Verificar configuración del dominio principal

El archivo de configuración para `weldtech.cloud` debe estar en `/etc/nginx/sites-available/weldtech.cloud` y debe apuntar a **otra aplicación**, NO a esta.

## 📝 Comandos Útiles

```bash
# Ver todas las configuraciones activas
nginx -T | grep server_name

# Ver logs de nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Verificar qué dominio está respondiendo
curl -H "Host: weldtech.cloud" http://72.61.10.156
curl -H "Host: gnv.weldtech.cloud" http://72.61.10.156
```

## 🚀 Configuración Automática desde Windows

### Opción 1: Script Automático (Recomendado)

Ejecuta el script que configura nginx automáticamente vía SSH:

```batch
scripts\configurar_nginx.bat
```

Este script:
1. Se conecta al servidor vía SSH
2. Sube el script de configuración
3. Ejecuta la configuración en el servidor
4. Verifica que todo esté correcto

### Opción 2: Verificar Configuración

Para verificar la configuración actual:

```batch
scripts\verificar_nginx.bat
```

## 🔍 Verificación

Después de aplicar los cambios:

1. ✅ `http://gnv.weldtech.cloud` debe mostrar la aplicación GNV
2. ✅ `http://api-gnv.weldtech.cloud` debe mostrar la API
3. ✅ `http://weldtech.cloud` debe mostrar **otra aplicación** (no GNV)

## 📋 Archivos de Referencia

- `scripts/nginx_gnv.conf` - Archivo de configuración completo
- `scripts/configurar_nginx.bat` - Script para configurar desde Windows
- `scripts/configurar_nginx_servidor.sh` - Script que se ejecuta en el servidor
- `scripts/verificar_nginx.bat` - Script para verificar la configuración

