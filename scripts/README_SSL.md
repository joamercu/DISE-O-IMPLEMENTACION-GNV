# 🔒 Guía de Configuración SSL y Separación de Dominios

Esta guía explica cómo configurar certificados SSL y separar correctamente los dominios `weldtech.cloud` y `gnv.weldtech.cloud`.

## 📋 Problema a Resolver

1. **Certificados SSL expirados o inválidos**: El navegador muestra "conexión no privada" en Android
2. **Dominio incorrecto**: `weldtech.cloud` está mostrando la aplicación Streamlit cuando debería mostrar la aplicación de login
3. **Separación de dominios**: Necesitamos que:
   - `weldtech.cloud` → Aplicación de login (puerto 3000 o el que corresponda)
   - `gnv.weldtech.cloud` → Aplicación Streamlit (puerto 8501)
   - `api-gnv.weldtech.cloud` → API (puerto 8000)

## ✅ Solución Completa

### Opción 1: Configuración Automática Completa (Recomendado)

Ejecuta el script maestro que hace todo automáticamente:

```batch
scripts\configurar_ssl_completo.bat
```

Este script:
1. Instala/renueva certificados SSL para todos los dominios usando Let's Encrypt
2. Configura nginx para separar correctamente los dominios
3. Configura HTTPS con redirección automática de HTTP a HTTPS

### Opción 2: Configuración Paso a Paso

Si prefieres hacerlo paso a paso:

#### Paso 1: Instalar/Renovar Certificados SSL

```batch
scripts\instalar_certificados_ssl.bat
```

Este script:
- Instala certbot (si no está instalado)
- Obtiene/renueva certificados SSL para:
  - `weldtech.cloud`
  - `gnv.weldtech.cloud`
  - `api-gnv.weldtech.cloud`
- Configura renovación automática

**Nota**: Necesitarás proporcionar un email para recibir notificaciones de renovación.

#### Paso 2: Configurar Nginx Completo

```batch
scripts\configurar_nginx_completo_ssl.bat
```

Este script:
- Configura `weldtech.cloud` para apuntar a la aplicación de login
- Configura `gnv.weldtech.cloud` para apuntar a Streamlit
- Configura `api-gnv.weldtech.cloud` para apuntar a la API
- Configura HTTPS con certificados Let's Encrypt
- Redirige HTTP a HTTPS automáticamente

**Nota**: Necesitarás especificar en qué puerto está corriendo la aplicación de login (por defecto: 3000).

### Opción 3: Scripts Individuales

Si necesitas configurar solo una parte:

#### Renovar Certificados Existentes

```batch
scripts\renovar_certificados_ssl.bat
```

Renueva certificados SSL existentes sin reinstalarlos.

#### Configurar Solo weldtech.cloud

```batch
scripts\configurar_weldtech_cloud.bat
```

Configura solo el dominio `weldtech.cloud` para la aplicación de login.

#### Configurar Solo gnv.weldtech.cloud

```batch
scripts\configurar_nginx_https.bat
```

Configura solo el dominio `gnv.weldtech.cloud` con HTTPS.

## 🔍 Verificación

Después de ejecutar los scripts, verifica que todo funcione:

### 1. Verificar Certificados

Conéctate al servidor y ejecuta:

```bash
ssh root@72.61.10.156
certbot certificates
```

Deberías ver los certificados para los tres dominios con fechas de expiración válidas.

### 2. Verificar Configuración de Nginx

```bash
nginx -t
```

Debería mostrar "syntax is ok" y "test is successful".

### 3. Verificar Dominios

- `https://weldtech.cloud` → Debe mostrar la aplicación de login
- `https://gnv.weldtech.cloud` → Debe mostrar la aplicación Streamlit
- `https://api-gnv.weldtech.cloud` → Debe mostrar la API

### 4. Verificar Redirección HTTP → HTTPS

- `http://weldtech.cloud` → Debe redirigir a `https://weldtech.cloud`
- `http://gnv.weldtech.cloud` → Debe redirigir a `https://gnv.weldtech.cloud`

## ⚠️ Solución de Problemas

### Error: "Conexión no privada" en Android

**Causa**: Certificado SSL expirado o inválido.

**Solución**:
1. Ejecuta `scripts\instalar_certificados_ssl.bat` para renovar certificados
2. Verifica que los certificados estén instalados correctamente
3. Asegúrate de que nginx esté usando los certificados correctos

### Error: weldtech.cloud muestra Streamlit

**Causa**: Configuración de nginx incorrecta.

**Solución**:
1. Ejecuta `scripts\configurar_nginx_completo_ssl.bat`
2. Verifica que no haya configuraciones conflictivas en nginx
3. Asegúrate de que `weldtech.cloud` apunte al puerto correcto de la aplicación de login

### Error: Certificado no encontrado

**Causa**: El certificado no está instalado o está en otra ubicación.

**Solución**:
1. Ejecuta `scripts\instalar_certificados_ssl.bat` para instalar certificados
2. Verifica que el dominio apunte correctamente a este servidor
3. Asegúrate de que los puertos 80 y 443 estén abiertos en el firewall

### Error: No se puede conectar al servidor

**Causa**: Problemas de conexión SSH o configuración incorrecta.

**Solución**:
1. Verifica la configuración del servidor: `scripts\config_servidor.bat`
2. Verifica la conexión SSH: `scripts\verificar_ssh.bat`
3. Verifica que la IP del servidor sea correcta

## 📝 Configuración Manual (Si es Necesario)

Si los scripts no funcionan, puedes configurar manualmente:

### 1. Instalar Certbot

```bash
apt-get update
apt-get install -y certbot python3-certbot-nginx
```

### 2. Obtener Certificados

```bash
# Para weldtech.cloud
certbot certonly --nginx -d weldtech.cloud

# Para gnv.weldtech.cloud
certbot certonly --nginx -d gnv.weldtech.cloud

# Para api-gnv.weldtech.cloud
certbot certonly --nginx -d api-gnv.weldtech.cloud
```

### 3. Configurar Nginx

Edita los archivos en `/etc/nginx/sites-available/` y asegúrate de que:
- `weldtech.cloud` apunte al puerto de la aplicación de login
- `gnv.weldtech.cloud` apunte al puerto 8501 (Streamlit)
- `api-gnv.weldtech.cloud` apunte al puerto 8000 (API)

### 4. Recargar Nginx

```bash
nginx -t
systemctl reload nginx
```

## 🔄 Renovación Automática

Los certificados de Let's Encrypt expiran cada 90 días. El script configura la renovación automática, pero puedes verificar el estado con:

```bash
systemctl status certbot.timer
```

Para renovar manualmente:

```bash
certbot renew
```

## 📚 Archivos de Configuración

Los archivos de configuración de nginx se guardan en:
- `/etc/nginx/sites-available/weldtech.cloud`
- `/etc/nginx/sites-available/gnv.weldtech.cloud`

Los certificados SSL se guardan en:
- `/etc/letsencrypt/live/weldtech.cloud/`
- `/etc/letsencrypt/live/gnv.weldtech.cloud/`
- `/etc/letsencrypt/live/api-gnv.weldtech.cloud/`

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs: `scripts\ver_logs_servidor.bat`
2. Verifica el estado del servidor: `scripts\estado_servidor.bat`
3. Verifica la configuración de nginx: `scripts\verificar_nginx.bat`

