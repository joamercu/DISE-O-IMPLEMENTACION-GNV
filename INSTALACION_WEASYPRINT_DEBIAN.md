# Instalación de WeasyPrint en Debian/Ubuntu

## Problema

WeasyPrint está instalado pero no puede cargar las librerías necesarias porque faltan las dependencias del sistema.

## Solución: Instalar Dependencias del Sistema

En Debian/Ubuntu, WeasyPrint requiere varias librerías del sistema que deben instalarse con `apt-get` antes de instalar el paquete Python.

### Instalación Completa (Recomendado)

Ejecuta estos comandos en el servidor Debian:

```bash
# Actualizar lista de paquetes
sudo apt-get update

# Instalar dependencias del sistema para WeasyPrint
# Nota: En Debian 13+ usar libgdk-pixbuf-xlib-2.0-0 en lugar de libgdk-pixbuf2.0-0

# Para Debian 13+:
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    shared-mime-info

# Para Debian 11/12 o Ubuntu:
# sudo apt-get install -y \
#     build-essential \
#     python3-dev \
#     python3-pip \
#     python3-setuptools \
#     python3-wheel \
#     python3-cffi \
#     libcairo2 \
#     libpango-1.0-0 \
#     libpangocairo-1.0-0 \
#     libgdk-pixbuf2.0-0 \
#     libffi-dev \
#     shared-mime-info

# Instalar WeasyPrint con pip
# NOTA: En Debian 13+ (Python 3.13) se requiere --break-system-packages
pip3 install weasyprint --break-system-packages

# O si usas un entorno virtual (recomendado):
# source venv/bin/activate
# pip install weasyprint  # Sin --break-system-packages en venv
```

### Si usas un Entorno Virtual

Si estás usando un entorno virtual (recomendado):

```bash
# Activar entorno virtual
source venv/bin/activate  # o el nombre de tu venv

# Instalar dependencias del sistema (fuera del venv)
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

# Instalar WeasyPrint dentro del venv
pip install weasyprint
```

### Script de Instalación Automática

Puedes usar el script incluido:

```bash
# Dar permisos de ejecución
chmod +x scripts/instalar_weasyprint_debian.sh

# Ejecutar
sudo ./scripts/instalar_weasyprint_debian.sh
```

## Verificación

Después de instalar, verifica que WeasyPrint funcione:

```bash
python3 -c "from weasyprint import HTML; print('✓ WeasyPrint funciona correctamente')"
```

O desde Python:

```python
from weasyprint import HTML
print("WeasyPrint importado correctamente")
```

## Dependencias Explicadas

- **build-essential**: Herramientas de compilación (gcc, make, etc.)
- **python3-dev**: Headers de desarrollo de Python
- **libcairo2**: Librería de renderizado 2D
- **libpango-1.0-0**: Motor de layout de texto
- **libpangocairo-1.0-0**: Integración Pango-Cairo
- **libgdk-pixbuf2.0-0**: Carga y manipulación de imágenes
- **libffi-dev**: Foreign Function Interface
- **shared-mime-info**: Base de datos MIME

## Solución de Problemas

### Error: "Package not found"
```bash
# Actualizar lista de paquetes
sudo apt-get update
```

### Error: "Permission denied"
Asegúrate de usar `sudo` para instalar paquetes del sistema.

### Error: "pip: command not found"
```bash
# Instalar pip si no está disponible
sudo apt-get install python3-pip
```

### Error después de instalar dependencias
```bash
# Reinstalar weasyprint
pip uninstall weasyprint
pip install weasyprint
```

### Verificar versiones instaladas
```bash
# Verificar dependencias del sistema
dpkg -l | grep -E "libcairo2|libpango|libgdk-pixbuf"

# Verificar weasyprint
pip show weasyprint
```

## Instalación en Servidor de Producción

Para un servidor de producción, considera:

1. **Usar un entorno virtual** para aislar dependencias
2. **Documentar la instalación** en tu proceso de despliegue
3. **Incluir en el script de despliegue** la instalación de dependencias

Ejemplo para incluir en tu script de despliegue:

```bash
# En tu script de despliegue (deploy_app.sh o similar)
echo "Instalando dependencias de WeasyPrint..."
sudo apt-get update -qq
sudo apt-get install -y \
    build-essential \
    python3-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info > /dev/null 2>&1

echo "Instalando WeasyPrint..."
pip install weasyprint > /dev/null 2>&1
```

## Referencias

- Documentación oficial de WeasyPrint: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation
- Guía de instalación en Linux: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#linux

