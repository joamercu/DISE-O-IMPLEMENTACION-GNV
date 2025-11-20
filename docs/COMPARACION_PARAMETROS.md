# 🔍 Comparación de Parámetros: Competencia vs Aplicación Actual

## Resumen Ejecutivo

Este documento compara los parámetros identificados en el sitio web de la competencia (somosgnv.com) con los parámetros actualmente implementados en la aplicación de cálculos GNV.

---

## 1. Parámetros Técnicos de Cálculo

### 1.1 Parámetros Existentes en la Aplicación

| Parámetro | Valor por Defecto | Rango | Estado |
|-----------|-------------------|-------|--------|
| Consumo Diésel | 35.0 L/100 km | 1.0 - 200.0 | ✅ Implementado |
| Autonomía Deseada | 800.0 km | 100.0 - 2000.0 | ✅ Implementado |
| Poder Calorífico Diésel | 35.8 MJ/L | 30.0 - 40.0 | ✅ Implementado |
| LHV CH₄ | 50.0 MJ/kg | 45.0 - 55.0 | ✅ Implementado |
| Eficiencia de Conversión | 0.95 | 0.80 - 1.0 | ✅ Implementado |
| Presión de Llenado | 200.0 bar | 150.0 - 300.0 | ✅ Implementado |
| Temperatura de Operación | 25.0 °C | 0.0 - 50.0 | ✅ Implementado |
| Factor de Compresibilidad Z | 0.85 | 0.70 - 1.0 | ✅ Implementado |
| Volumen Unitario Tanque | 0.080 m³ | 0.01 - 0.20 | ✅ Implementado |
| Peso Tanque Vacío | 65.0 kg | 20.0 - 150.0 | ✅ Implementado |
| Peso Soportes | 10.0 kg | 5.0 - 30.0 | ✅ Implementado |
| Peso Accesorios | 5.0 kg | 1.0 - 20.0 | ✅ Implementado |

**Conclusión:** Los parámetros técnicos de cálculo están completamente implementados y son más detallados que lo que muestra la competencia.

---

## 2. Parámetros Económicos y Ambientales

### 2.1 Parámetros Faltantes (Identificados en Competencia)

| Parámetro | Valor Competencia | Estado Actual | Prioridad |
|-----------|-------------------|---------------|-----------|
| **Ahorro Económico** | 30% | ❌ No implementado | 🔴 ALTA |
| **Reducción CO₂** | 30% | ❌ No implementado | 🔴 ALTA |
| **Reducción Material Particulado** | ~100% | ❌ No implementado | 🔴 ALTA |
| **Beneficio Tributario - Arancel** | 5% | ❌ No implementado | 🟡 MEDIA |
| **Descuento Renta** | 25% | ❌ No implementado | 🟡 MEDIA |
| **Exclusión IVA** | Posible | ❌ No implementado | 🟡 MEDIA |

**Análisis:**
- La aplicación actual se enfoca en cálculos técnicos (dimensionamiento, peso, tanques)
- No incluye análisis económico ni beneficios ambientales
- Estos parámetros son críticos para la justificación de inversión

---

## 3. Categorías de Vehículos

### 3.1 Categorías Implementadas

| Categoría | Estado | Parámetros por Defecto |
|-----------|--------|------------------------|
| Tractores 4x2 | ✅ Implementado | Consumo: 30-40 L/100 km, Autonomía: 600 km |
| Tractores 6x4 | ✅ Implementado | Consumo: 35-45 L/100 km, Autonomía: 700-900 km |
| Volquetas 6x4 | ✅ Implementado | Consumo: 40-50 L/100 km, Autonomía: 500-700 km |

### 3.2 Categorías Faltantes (Identificadas en Competencia)

| Categoría | Especificaciones Competencia | Estado Actual | Prioridad |
|-----------|------------------------------|---------------|-----------|
| **Buses** | 7-27 metros, dedicados 100% GNV | ❌ No implementado | 🟡 MEDIA |
| **Compactadoras** | Europeas/Norteamericanas, eje sencillo/dobletroque | ❌ No implementado | 🟢 BAJA |
| **Furgones/Última Milla** | 1.5-10.5 toneladas PBV | ❌ No implementado | 🟢 BAJA |
| **Tractocamiones Sencillos** | >10.5 toneladas | ⚠️ Parcial (cubierto por Tractores) | 🟢 BAJA |
| **Tractocamiones Doble Troque** | >10.5 toneladas | ⚠️ Parcial (cubierto por Tractores) | 🟢 BAJA |
| **Tractocamiones Minimulas** | >10.5 toneladas | ⚠️ Parcial (cubierto por Tractores) | 🟢 BAJA |
| **Volquetas Eje Sencillo** | Dedicadas 100% GNV | ❌ No implementado | 🟢 BAJA |

**Análisis:**
- La aplicación cubre los casos de uso principales (Tractores y Volquetas)
- Las categorías faltantes son nichos específicos
- Prioridad media para Buses (aplicación común)
- Prioridad baja para otras categorías (casos de uso menos frecuentes)

---

## 4. Funcionalidades Adicionales

### 4.1 Funcionalidades Implementadas

| Funcionalidad | Estado | Detalles |
|---------------|--------|----------|
| Cálculos Técnicos | ✅ Completo | Dimensionamiento, peso, tanques |
| Análisis de Sensibilidad | ✅ Implementado | Variación de consumo y autonomía |
| Gestión de Datos Cliente | ✅ Implementado | Formularios y exportación JSON |
| Generación de Informes | ✅ Implementado | HTML, PDF, Excel |
| API REST | ✅ Implementado | Endpoint de datos de salida |
| Autenticación | ✅ Implementado | Roles Admin/Cliente |

### 4.2 Funcionalidades Faltantes (Identificadas en Competencia)

| Funcionalidad | Descripción Competencia | Estado Actual | Prioridad |
|---------------|-------------------------|---------------|-----------|
| **Mapa de Estaciones GNV** | Mapa interactivo con ubicaciones EDS | ❌ No implementado | 🟡 MEDIA |
| **Calculadora Económica** | Ahorro, ROI, payback | ❌ No implementado | 🔴 ALTA |
| **Análisis Ambiental** | Reducción emisiones, impacto | ❌ No implementado | 🔴 ALTA |
| **Catálogo de Vehículos** | PDF con especificaciones | ❌ No implementado | 🟢 BAJA |
| **Casos de Éxito** | Testimonios y experiencias | ❌ No implementado | 🟢 BAJA |
| **Noticias del Sector** | Actualizaciones GNV | ❌ No implementado | 🟢 BAJA |
| **Selección Geográfica** | Departamentos Colombia | ⚠️ No en formulario cliente | 🟡 MEDIA |

**Análisis:**
- Funcionalidades de contenido (noticias, casos de éxito) son informativas pero no críticas
- Calculadora económica y análisis ambiental son complementos importantes para justificación
- Mapa de estaciones es útil pero requiere integración externa

---

## 5. Matriz de Gaps Identificados

### 5.1 Gaps Críticos (Alta Prioridad)

| Gap | Impacto | Esfuerzo | Recomendación |
|-----|---------|----------|---------------|
| Parámetros económicos | Alto - Justificación inversión | Medio | Implementar módulo de análisis económico |
| Parámetros ambientales | Alto - Reportes sostenibilidad | Bajo | Agregar sección de beneficios ambientales |
| Calculadora de ahorro | Alto - Toma de decisiones | Medio | Crear módulo de cálculo económico |

### 5.2 Gaps Importantes (Media Prioridad)

| Gap | Impacto | Esfuerzo | Recomendación |
|-----|---------|----------|---------------|
| Categoría Buses | Medio - Caso de uso común | Medio | Agregar tipo de vehículo con parámetros específicos |
| Mapa de estaciones | Medio - Planificación rutas | Alto | Integración opcional con API de mapas |
| Selección geográfica | Medio - Segmentación | Bajo | Agregar campo departamento en datos cliente |

### 5.3 Gaps Opcionales (Baja Prioridad)

| Gap | Impacto | Esfuerzo | Recomendación |
|-----|---------|----------|---------------|
| Categorías adicionales | Bajo - Nichos específicos | Medio | Agregar según demanda |
| Catálogo vehículos | Bajo - Referencia | Bajo | Sección de documentos o enlaces |
| Casos de éxito | Bajo - Marketing | Bajo | Sección informativa opcional |
| Noticias sector | Bajo - Actualización | Bajo | Enlaces externos o RSS |

---

## 6. Resumen de Parámetros por Categoría

### 6.1 Parámetros Técnicos
- **Estado:** ✅ Completamente implementado
- **Cobertura:** 100% de parámetros técnicos necesarios
- **Ventaja:** Más detallado que la competencia

### 6.2 Parámetros Económicos
- **Estado:** ❌ No implementado
- **Cobertura:** 0% de parámetros económicos
- **Gap:** Falta análisis económico completo

### 6.3 Parámetros Ambientales
- **Estado:** ❌ No implementado
- **Cobertura:** 0% de parámetros ambientales
- **Gap:** Falta cuantificación de beneficios ambientales

### 6.4 Categorías de Vehículos
- **Estado:** ⚠️ Parcialmente implementado
- **Cobertura:** ~60% (3 de 5 categorías principales)
- **Gap:** Faltan Buses y categorías especializadas

### 6.5 Funcionalidades Adicionales
- **Estado:** ⚠️ Parcialmente implementado
- **Cobertura:** ~70% (cálculos técnicos completos, faltan económicos/ambientales)
- **Gap:** Falta análisis económico y ambiental

---

## 7. Recomendaciones Prioritarias

### Prioridad 1: Parámetros Económicos y Ambientales
1. Agregar parámetros de ahorro económico (30%)
2. Agregar parámetros de reducción de emisiones (CO₂: 30%, MP: ~100%)
3. Implementar cálculo de ahorro económico en reportes
4. Agregar sección de beneficios ambientales en informes

### Prioridad 2: Expansión de Categorías
1. Agregar categoría Buses con parámetros específicos
2. Considerar agregar otras categorías según demanda

### Prioridad 3: Funcionalidades Complementarias
1. Agregar campo de departamento en datos del cliente
2. Considerar integración de mapa de estaciones (opcional)
3. Agregar referencias a normativas y catálogos

---

## 8. Conclusión

La aplicación actual tiene una **base técnica sólida y completa** que supera a la competencia en detalle de cálculos técnicos. Sin embargo, presenta **gaps importantes en análisis económico y ambiental**, que son críticos para la justificación de inversión en sistemas GNV.

**Fortalezas:**
- Cálculos técnicos detallados y precisos
- Análisis de sensibilidad
- Gestión completa de datos del cliente
- Generación de informes profesionales

**Oportunidades de Mejora:**
- Análisis económico (ahorro, ROI, payback)
- Cuantificación de beneficios ambientales
- Expansión de categorías de vehículos (especialmente Buses)
- Funcionalidades complementarias (mapa, catálogo)

---

*Documento creado: 2025-11-20*  
*Última actualización: 2025-11-20*

