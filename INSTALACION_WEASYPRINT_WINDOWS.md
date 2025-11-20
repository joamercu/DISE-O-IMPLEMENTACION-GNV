# Instalación de WeasyPrint en Windows

## Problema

WeasyPrint está instalado pero no puede cargar las librerías necesarias (GTK+) en Windows. El error típico es:
```
OSError: cannot load library 'gobject-2.0-0.dll': error 0xc1
```

## Solución: Instalar GTK+ para Windows

WeasyPrint requiere GTK+ y sus dependencias en Windows. Hay dos métodos principales:

### Método 1: Instalador de GTK+ para Windows (Recomendado)

1. **Descargar el instalador de GTK+ Runtime Environment:**
   - Visita: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
   - Descarga la última versión del instalador (ej: `gtk3-runtime-3.x.x-x64.exe`)

2. **Ejecutar el instalador:**
   - Ejecuta el archivo descargado como administrador
   - Sigue las instrucciones del instalador
   - Asegúrate de que GTK+ se instale en una ruta accesible (por defecto: `C:\Program Files\GTK3-Runtime Win64`)

3. **Agregar GTK+ al PATH (si es necesario):**
   - Abre "Variables de entorno" en Windows
   - Agrega la ruta `C:\Program Files\GTK3-Runtime Win64\bin` a la variable PATH del sistema
   - Reinicia la terminal/PowerShell después de modificar el PATH

4. **Verificar la instalación:**
   ```bash
   python -c "from weasyprint import HTML; print('WeasyPrint funciona correctamente')"
   ```

### Método 2: Usar MSYS2 (Alternativa)

1. **Instalar MSYS2:**
   - Descarga MSYS2 desde: https://www.msys2.org/
   - Instala MSYS2 siguiendo las instrucciones

2. **Instalar GTK+ en MSYS2:**
   ```bash
   pacman -S mingw-w64-x86_64-gtk3
   ```

3. **Configurar el PATH:**
   - Agrega la ruta de MSYS2 al PATH del sistema
   - Ejemplo: `C:\msys64\mingw64\bin`

### Método 3: Usar Chocolatey (Si está disponible)

Si tienes Chocolatey instalado:

```bash
choco install gtkruntime
```

## Verificación

Después de instalar GTK+, verifica que WeasyPrint funcione:

```bash
python -c "from weasyprint import HTML; print('✓ WeasyPrint funciona correctamente')"
```

## Notas Importantes

- **Reiniciar la terminal:** Después de modificar el PATH, cierra y vuelve a abrir la terminal/PowerShell
- **Reiniciar la aplicación:** Si estás ejecutando Streamlit u otra aplicación, reiníciala después de instalar GTK+
- **Versión de Python:** Asegúrate de usar la misma versión de Python donde instalaste weasyprint

## Solución de Problemas

### Error: "cannot load library"
- Verifica que GTK+ esté instalado correctamente
- Verifica que el PATH incluya la ruta a las DLLs de GTK+
- Reinicia la terminal después de modificar el PATH

### Error: "DLL not found"
- Asegúrate de haber instalado la versión correcta (32-bit vs 64-bit) según tu Python
- Verifica que todas las DLLs necesarias estén en el PATH

### Error persistente
- Intenta reinstalar weasyprint: `pip uninstall weasyprint && pip install weasyprint`
- Verifica que no haya conflictos con otras instalaciones de GTK+ (como Graphviz)

## Referencias

- Documentación oficial de WeasyPrint: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation
- GTK+ para Windows: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

