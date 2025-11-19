# 📋 Documentación de Archivos BOM

## Archivos BOM Disponibles

### ✅ Archivo Oficial: `PETROLIQUIDOS_GNV_BOM_v1.xlsx`

**Ubicación:** `outputs/PETROLIQUIDOS_GNV_BOM_v1.xlsx`

**Estado:** ✅ Versión oficial y actualizada

**Características:**
- **5 hojas** con información completa:
  - `Assumptions`: 26 filas con parámetros técnicos detallados
  - `Calculations`: 20 filas con fórmulas operativas para 3 configuraciones
  - `BOM`: 29 ítems con información completa de materiales
  - `Sensitivity`: 25 filas con análisis de sensibilidad (±10%, ±20%)
  - `Summary`: 23 filas con resumen ejecutivo y costos estimados

- **Información detallada por ítem:**
  - Descripción técnica completa
  - Cantidad y unidad
  - Precios unitarios (USD y COP)
  - Totales (USD y COP)
  - Lead Time (semanas)
  - Proveedor sugerido
  - Part Number/URL
  - Notas adicionales

- **Última modificación:** 2025-11-19 09:37:20
- **Tamaño:** 14.0 KB

**Referencias en el código:**
- `src/config.py`: Definido como `DELIVERABLE_XLSX`
- `data/PETROLIQUIDOS_GNV_manifest_v1.json`: Documentado en el manifest del proyecto
- Sistema de descarga de la aplicación Streamlit

---

### ⚠️ Archivo Obsoleto: `BOM_PETROLIQUIDOS_GNV.xlsx`

**Ubicación:** `outputs/BOM_PETROLIQUIDOS_GNV.xlsx`

**Estado:** ⚠️ Versión anterior/simplificada - **NO USAR**

**Características:**
- **3 hojas** con información básica:
  - `BOM`: 12 ítems (versión simplificada)
  - `Summary`: 4 filas (estructura básica)
  - `Assumptions`: 1 fila (parámetros mínimos)

- **Información limitada:**
  - Solo columnas básicas: Item, Qty, Unit_USD, Total_USD, Unit_COP, Total_COP
  - Sin información de proveedores, lead times, o part numbers
  - Sin análisis de sensibilidad
  - Sin cálculos detallados

- **Última modificación:** 2025-11-19 09:19:41
- **Tamaño:** 6.85 KB

**Nota:** Este archivo **NO está referenciado** en el código del proyecto y se mantiene solo para referencia histórica.

---

## Comparación Rápida

| Característica | Archivo Oficial | Archivo Obsoleto |
|---------------|----------------|------------------|
| **Hojas** | 5 | 3 |
| **Ítems en BOM** | 29 | 12 |
| **Columnas en BOM** | 12 | 6 |
| **Análisis de sensibilidad** | ✅ Sí | ❌ No |
| **Cálculos detallados** | ✅ Sí | ❌ No |
| **Proveedores/Lead Times** | ✅ Sí | ❌ No |
| **Part Numbers** | ✅ Sí | ❌ No |
| **Referenciado en código** | ✅ Sí | ❌ No |

---

## Recomendación

**SIEMPRE usar:** `PETROLIQUIDOS_GNV_BOM_v1.xlsx`

Este es el archivo oficial que contiene toda la información actualizada y completa del proyecto. El archivo `BOM_PETROLIQUIDOS_GNV.xlsx` es una versión anterior y no debe utilizarse para trabajo actual.

---

## Script de Comparación

Se ha creado un script `comparar_bom.py` en la raíz del proyecto que permite comparar ambos archivos Excel y generar un reporte detallado de diferencias.

**Uso:**
```bash
python comparar_bom.py
```

---

**Última actualización:** 2025-11-19
**Autor:** Sistema de Documentación Automática

