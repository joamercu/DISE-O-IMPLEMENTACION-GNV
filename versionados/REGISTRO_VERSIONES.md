# Registro de Versiones - Archivos PDF y Excel

Este documento registra todos los archivos PDF y Excel que han sido organizados en carpetas de versiones para mantener un historial del proyecto.

**Fecha de organización:** 2025-11-20

---

## 📄 Archivos PDF Versionados

Los siguientes PDFs han sido movidos a `versionados/pdfs/` con timestamps de última modificación:

### PDFs del Proyecto Principal
1. **diagrama gnv_20251120_111006.pdf**
   - Origen: `diagrama gnv.pdf` (raíz)
   - Última modificación: 2025-11-20 11:10:06

2. **output 1_20251119_103542.pdf**
   - Origen: `outputs/output 1.pdf`
   - Última modificación: 2025-11-19 10:35:42

3. **output 2_20251119_103601.pdf**
   - Origen: `outputs/output 2.pdf`
   - Última modificación: 2025-11-19 10:36:01

4. **output 3_20251119_104600.pdf**
   - Origen: `docs/output 3.pdf`
   - Última modificación: 2025-11-19 10:46:00

### PDFs de Documentación
5. **Informe de Cálculo Sistema GNV - PETROLIQUIDOS_20251119_121246.pdf**
   - Origen: `docs/Informe de Cálculo Sistema GNV - PETROLIQUIDOS.pdf`
   - Última modificación: 2025-11-19 12:12:46

6. **Herramienta de Documentos - WeldTech Solutions_20251119_130121.pdf**
   - Origen: `docs/Herramienta de Documentos - WeldTech Solutions.pdf`
   - Última modificación: 2025-11-19 13:01:21

7. **Resolución 957 de 2012 Ministerio de Comercio, Industria y Turismo_20251119_110838.pdf**
   - Origen: `docs/Resolución 957 de 2012 Ministerio de Comercio, Industria y Turismo.pdf`
   - Última modificación: 2025-11-19 11:08:38

---

## 📊 Archivos Excel Versionados

Los siguientes archivos Excel han sido movidos a `versionados/excel/` con timestamps:

1. **BOM_PETROLIQUIDOS_GNV_20251119_091941.xlsx**
   - Origen: `outputs/archivos_antiguos/BOM_PETROLIQUIDOS_GNV.xlsx`
   - Última modificación: 2025-11-19 09:19:41
   - Descripción: Versión antigua del BOM (Bill of Materials)

---

## 📁 Archivos Activos (Versiones Más Recientes)

### En `outputs/` (Para uso en la aplicación principal):
- ✅ **PETROLIQUIDOS_GNV_BOM_v1.xlsx** - Excel BOM más reciente
- ✅ **diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_FINAL.pdf** - PDF del diagrama más reciente

### En raíz del proyecto:
- ✅ **diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.pdf** - PDF del ingeniero (referencia)

---

## 📋 Diagrama XML Más Reciente

- **diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_FINAL.drawio.xml**
  - Ubicación: Raíz del proyecto
  - Descripción: Versión final del diagrama P&ID del sistema GNV

**Nota:** El PDF correspondiente a este XML debe generarse manualmente usando Draw.io Desktop o CLI, ya que la generación automática requiere herramientas adicionales instaladas.

---

## 🔄 Proceso de Versionado

1. Todos los archivos antiguos se copian (no se mueven) a las carpetas de versiones
2. Se agrega un timestamp basado en la fecha de última modificación
3. Los archivos originales se mantienen en su ubicación original
4. Las versiones más recientes se dejan en `outputs/` para uso en la aplicación

---

## 📝 Notas Importantes

- Los archivos en `versionados/` son copias de seguridad con timestamps
- Los archivos activos en `outputs/` son los que usa la aplicación principal
- El PDF del ingeniero se mantiene en la raíz como referencia
- Para generar nuevos PDFs desde XML, usar `generar_pdf_diagrama.py` o Draw.io Desktop/CLI

---

**Última actualización:** 2025-11-20

