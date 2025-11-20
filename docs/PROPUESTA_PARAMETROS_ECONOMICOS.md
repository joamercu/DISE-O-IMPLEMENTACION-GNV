# 💰 Propuesta de Estructura: Parámetros Económicos y Ambientales

## Objetivo

Proponer la estructura de nuevos parámetros económicos y ambientales identificados en la competencia para agregar a `src/config.py` y mejorar la funcionalidad de la aplicación.

---

## 1. Parámetros Económicos Propuestos

### 1.1 Estructura para `src/config.py`

```python
# ============================================
# PARÁMETROS ECONÓMICOS Y AMBIENTALES
# ============================================

# Parámetros de Ahorro Económico
DEFAULT_AHORRO_ECONOMICO = 0.30  # 30% de ahorro frente a combustibles tradicionales
DEFAULT_AHORRO_MIN = 0.10        # 10% mínimo esperado
DEFAULT_AHORRO_MAX = 0.50        # 50% máximo posible

# Parámetros de Beneficios Ambientales
DEFAULT_REDUCCION_CO2 = 0.30     # 30% reducción de CO₂
DEFAULT_REDUCCION_CO2_MIN = 0.20 # 20% mínimo
DEFAULT_REDUCCION_CO2_MAX = 0.40 # 40% máximo

DEFAULT_REDUCCION_MP = 0.99      # 99% reducción de material particulado
DEFAULT_REDUCCION_MP_MIN = 0.95  # 95% mínimo
DEFAULT_REDUCCION_MP_MAX = 1.0  # 100% máximo

DEFAULT_REDUCCION_NOX = 0.90     # 90% reducción de NOx (típico)
DEFAULT_REDUCCION_NOX_MIN = 0.80 # 80% mínimo
DEFAULT_REDUCCION_NOX_MAX = 0.95 # 95% máximo

# Parámetros de Beneficios Tributarios (Colombia)
DEFAULT_BENEFICIO_ARANCEL = 0.05      # 5% arancel máximo
DEFAULT_BENEFICIO_ARANCEL_MIN = 0.0   # 0% mínimo
DEFAULT_BENEFICIO_ARANCEL_MAX = 0.10  # 10% máximo

DEFAULT_DESCUENTO_RENTA = 0.25        # 25% descuento de renta máximo
DEFAULT_DESCUENTO_RENTA_MIN = 0.0    # 0% mínimo
DEFAULT_DESCUENTO_RENTA_MAX = 0.30   # 30% máximo

DEFAULT_EXCLUSION_IVA = True          # Posibilidad de exclusión de IVA
DEFAULT_EXCLUSION_IVA_PORCENTAJE = 1.0 # 100% de exclusión si aplica

# Parámetros de Precios de Combustible (para cálculos económicos)
DEFAULT_PRECIO_DIESEL_COP_LITRO = 4500.0  # Precio diésel en COP por litro
DEFAULT_PRECIO_GNV_COP_M3 = 2500.0        # Precio GNV en COP por m³
DEFAULT_TASA_CAMBIO_USD_COP = 3800.0     # Tasa de cambio USD/COP

# Parámetros de Análisis Económico
DEFAULT_ANOS_ANALISIS = 5              # Años para análisis de ROI
DEFAULT_TASA_DESCUENTO = 0.10          # 10% tasa de descuento (WACC)
DEFAULT_INFLACION_COMBUSTIBLE = 0.05   # 5% inflación anual de combustibles
```

### 1.2 Justificación de Valores

| Parámetro | Valor | Fuente | Justificación |
|-----------|-------|--------|---------------|
| Ahorro Económico | 30% | Competencia | Valor estándar del mercado colombiano |
| Reducción CO₂ | 30% | Competencia | Valor típico para GNV vs diésel |
| Reducción MP | 99% | Competencia | Casi eliminación completa |
| Reducción NOx | 90% | Literatura técnica | Valor típico para GNV |
| Beneficio Arancel | 5% | Competencia | Máximo según normativa colombiana |
| Descuento Renta | 25% | Competencia | Máximo según normativa colombiana |

---

## 2. Estructura de Datos para Cálculos Económicos

### 2.1 Función de Cálculo de Ahorro Económico

```python
def calcular_ahorro_economico(
    consumo_diesel_l_100km,
    precio_diesel_cop_litro,
    precio_gnv_cop_m3,
    ahorro_porcentaje,
    km_anuales,
    anos_analisis=5
):
    """
    Calcula el ahorro económico de la conversión a GNV
    
    Returns:
        dict: Diccionario con resultados del análisis económico
    """
    # Cálculo de consumo anual
    consumo_diesel_anual_l = (consumo_diesel_l_100km * km_anuales) / 100.0
    
    # Costo anual con diésel
    costo_diesel_anual = consumo_diesel_anual_l * precio_diesel_cop_litro
    
    # Costo anual con GNV (considerando ahorro)
    costo_gnv_anual = costo_diesel_anual * (1 - ahorro_porcentaje)
    
    # Ahorro anual
    ahorro_anual = costo_diesel_anual - costo_gnv_anual
    
    # Ahorro total en período de análisis
    ahorro_total = ahorro_anual * anos_analisis
    
    return {
        'consumo_diesel_anual_l': consumo_diesel_anual_l,
        'costo_diesel_anual_cop': costo_diesel_anual,
        'costo_gnv_anual_cop': costo_gnv_anual,
        'ahorro_anual_cop': ahorro_anual,
        'ahorro_total_cop': ahorro_total,
        'ahorro_porcentaje': ahorro_porcentaje,
        'anos_analisis': anos_analisis
    }
```

### 2.2 Función de Cálculo de Beneficios Ambientales

```python
def calcular_beneficios_ambientales(
    consumo_diesel_l_100km,
    km_anuales,
    reduccion_co2,
    reduccion_mp,
    reduccion_nox
):
    """
    Calcula los beneficios ambientales de la conversión a GNV
    
    Returns:
        dict: Diccionario con emisiones evitadas
    """
    # Factores de emisión (kg por litro de diésel)
    FACTOR_EMISION_CO2 = 2.68  # kg CO₂ por litro diésel
    FACTOR_EMISION_MP = 0.001  # kg MP por litro diésel
    FACTOR_EMISION_NOX = 0.05   # kg NOx por litro diésel
    
    # Consumo anual
    consumo_anual_l = (consumo_diesel_l_100km * km_anuales) / 100.0
    
    # Emisiones base (con diésel)
    emisiones_co2_base = consumo_anual_l * FACTOR_EMISION_CO2
    emisiones_mp_base = consumo_anual_l * FACTOR_EMISION_MP
    emisiones_nox_base = consumo_anual_l * FACTOR_EMISION_NOX
    
    # Emisiones con GNV
    emisiones_co2_gnv = emisiones_co2_base * (1 - reduccion_co2)
    emisiones_mp_gnv = emisiones_mp_base * (1 - reduccion_mp)
    emisiones_nox_gnv = emisiones_nox_base * (1 - reduccion_nox)
    
    # Reducciones (emisiones evitadas)
    reduccion_co2_kg = emisiones_co2_base - emisiones_co2_gnv
    reduccion_mp_kg = emisiones_mp_base - emisiones_mp_gnv
    reduccion_nox_kg = emisiones_nox_base - emisiones_nox_gnv
    
    return {
        'emisiones_co2_base_kg': emisiones_co2_base,
        'emisiones_co2_gnv_kg': emisiones_co2_gnv,
        'reduccion_co2_kg': reduccion_co2_kg,
        'emisiones_mp_base_kg': emisiones_mp_base,
        'emisiones_mp_gnv_kg': emisiones_mp_gnv,
        'reduccion_mp_kg': reduccion_mp_kg,
        'emisiones_nox_base_kg': emisiones_nox_base,
        'emisiones_nox_gnv_kg': emisiones_nox_gnv,
        'reduccion_nox_kg': reduccion_nox_kg,
        'reduccion_co2_porcentaje': reduccion_co2,
        'reduccion_mp_porcentaje': reduccion_mp,
        'reduccion_nox_porcentaje': reduccion_nox
    }
```

### 2.3 Función de Cálculo de Beneficios Tributarios

```python
def calcular_beneficios_tributarios(
    costo_sistema_cop,
    beneficio_arancel,
    descuento_renta,
    exclusion_iva
):
    """
    Calcula los beneficios tributarios de la conversión a GNV
    
    Returns:
        dict: Diccionario con beneficios tributarios
    """
    IVA_COLOMBIA = 0.19  # 19% IVA
    
    # Ahorro en arancel
    ahorro_arancel = costo_sistema_cop * beneficio_arancel
    
    # Ahorro en IVA (si aplica exclusión)
    ahorro_iva = costo_sistema_cop * IVA_COLOMBIA if exclusion_iva else 0.0
    
    # Ahorro en renta (sobre el costo del sistema)
    ahorro_renta = costo_sistema_cop * descuento_renta
    
    # Beneficio tributario total
    beneficio_total = ahorro_arancel + ahorro_iva + ahorro_renta
    
    return {
        'costo_sistema_cop': costo_sistema_cop,
        'ahorro_arancel_cop': ahorro_arancel,
        'ahorro_iva_cop': ahorro_iva,
        'ahorro_renta_cop': ahorro_renta,
        'beneficio_tributario_total_cop': beneficio_total,
        'beneficio_arancel_porcentaje': beneficio_arancel,
        'descuento_renta_porcentaje': descuento_renta,
        'exclusion_iva_aplicada': exclusion_iva
    }
```

---

## 3. Actualización Propuesta para `src/config.py`

### 3.1 Sección a Agregar

```python
# ============================================
# PARÁMETROS ECONÓMICOS Y AMBIENTALES
# Basados en análisis de competencia (somosgnv.com)
# ============================================

# Parámetros de Ahorro Económico
DEFAULT_AHORRO_ECONOMICO = 0.30  # 30% de ahorro frente a combustibles tradicionales
DEFAULT_AHORRO_MIN = 0.10        # 10% mínimo esperado
DEFAULT_AHORRO_MAX = 0.50        # 50% máximo posible

# Parámetros de Beneficios Ambientales
DEFAULT_REDUCCION_CO2 = 0.30     # 30% reducción de CO₂
DEFAULT_REDUCCION_CO2_MIN = 0.20 # 20% mínimo
DEFAULT_REDUCCION_CO2_MAX = 0.40 # 40% máximo

DEFAULT_REDUCCION_MP = 0.99      # 99% reducción de material particulado
DEFAULT_REDUCCION_MP_MIN = 0.95  # 95% mínimo
DEFAULT_REDUCCION_MP_MAX = 1.0   # 100% máximo

DEFAULT_REDUCCION_NOX = 0.90     # 90% reducción de NOx
DEFAULT_REDUCCION_NOX_MIN = 0.80 # 80% mínimo
DEFAULT_REDUCCION_NOX_MAX = 0.95 # 95% máximo

# Parámetros de Beneficios Tributarios (Colombia)
DEFAULT_BENEFICIO_ARANCEL = 0.05      # 5% arancel máximo
DEFAULT_BENEFICIO_ARANCEL_MIN = 0.0   # 0% mínimo
DEFAULT_BENEFICIO_ARANCEL_MAX = 0.10  # 10% máximo

DEFAULT_DESCUENTO_RENTA = 0.25        # 25% descuento de renta máximo
DEFAULT_DESCUENTO_RENTA_MIN = 0.0    # 0% mínimo
DEFAULT_DESCUENTO_RENTA_MAX = 0.30   # 30% máximo

DEFAULT_EXCLUSION_IVA = True          # Posibilidad de exclusión de IVA
DEFAULT_EXCLUSION_IVA_PORCENTAJE = 1.0 # 100% de exclusión si aplica

# Parámetros de Precios de Combustible (para cálculos económicos)
# Valores estimados - deben actualizarse según mercado actual
DEFAULT_PRECIO_DIESEL_COP_LITRO = 4500.0  # Precio diésel en COP por litro
DEFAULT_PRECIO_GNV_COP_M3 = 2500.0        # Precio GNV en COP por m³
DEFAULT_TASA_CAMBIO_USD_COP = 3800.0     # Tasa de cambio USD/COP

# Parámetros de Análisis Económico
DEFAULT_ANOS_ANALISIS = 5              # Años para análisis de ROI
DEFAULT_TASA_DESCUENTO = 0.10          # 10% tasa de descuento (WACC)
DEFAULT_INFLACION_COMBUSTIBLE = 0.05   # 5% inflación anual de combustibles

# Factores de Emisión (kg por litro de diésel)
# Fuente: EPA, IPCC, literatura técnica
FACTOR_EMISION_CO2_DIESEL = 2.68  # kg CO₂ por litro diésel
FACTOR_EMISION_MP_DIESEL = 0.001  # kg MP por litro diésel
FACTOR_EMISION_NOX_DIESEL = 0.05  # kg NOx por litro diésel

# IVA Colombia
IVA_COLOMBIA = 0.19  # 19% IVA
```

---

## 4. Actualización Propuesta para `docs/PARAMETROS.md`

### 4.1 Sección a Agregar

```markdown
## Parámetros Económicos y Ambientales

### Ahorro Económico
- **Valor por defecto:** 0.30 (30%)
- **Rango:** 0.10 - 0.50 (10% - 50%)
- **Descripción:** Porcentaje de ahorro en costos de combustible frente a diésel
- **Fuente:** Análisis de mercado colombiano, competencia
- **Consideraciones:** Varía según precio relativo diésel/GNV y eficiencia del sistema

### Reducción de CO₂
- **Valor por defecto:** 0.30 (30%)
- **Rango:** 0.20 - 0.40 (20% - 40%)
- **Descripción:** Porcentaje de reducción de emisiones de CO₂
- **Fuente:** Estudios técnicos, competencia
- **Consideraciones:** Depende de composición del gas natural y eficiencia del motor

### Reducción de Material Particulado
- **Valor por defecto:** 0.99 (99%)
- **Rango:** 0.95 - 1.0 (95% - 100%)
- **Descripción:** Porcentaje de reducción de material particulado
- **Fuente:** Estudios técnicos, competencia
- **Consideraciones:** Casi eliminación completa debido a combustión más limpia

### Reducción de NOx
- **Valor por defecto:** 0.90 (90%)
- **Rango:** 0.80 - 0.95 (80% - 95%)
- **Descripción:** Porcentaje de reducción de óxidos de nitrógeno
- **Fuente:** Estudios técnicos
- **Consideraciones:** Depende de tecnología del motor y sistema de post-tratamiento

### Beneficios Tributarios

#### Arancel
- **Valor por defecto:** 0.05 (5%)
- **Rango:** 0.0 - 0.10 (0% - 10%)
- **Descripción:** Reducción de arancel para importación de componentes GNV
- **Fuente:** Normativa colombiana, competencia
- **Consideraciones:** Aplicable según normativa vigente

#### Descuento de Renta
- **Valor por defecto:** 0.25 (25%)
- **Rango:** 0.0 - 0.30 (0% - 30%)
- **Descripción:** Descuento en impuesto de renta
- **Fuente:** Normativa colombiana, competencia
- **Consideraciones:** Aplicable según normativa vigente

#### Exclusión de IVA
- **Valor por defecto:** True (aplicable)
- **Descripción:** Posibilidad de exclusión de IVA en compra de componentes
- **Fuente:** Normativa colombiana, competencia
- **Consideraciones:** Aplicable según normativa vigente

### Precios de Combustible
- **Precio Diésel:** 4500.0 COP/litro (valor estimado, actualizar según mercado)
- **Precio GNV:** 2500.0 COP/m³ (valor estimado, actualizar según mercado)
- **Tasa de Cambio:** 3800.0 COP/USD (valor estimado, actualizar según mercado)
- **Consideraciones:** Estos valores deben actualizarse regularmente según condiciones de mercado

### Parámetros de Análisis Económico
- **Años de Análisis:** 5 años (default)
- **Tasa de Descuento:** 0.10 (10% WACC)
- **Inflación Combustible:** 0.05 (5% anual)
```

---

## 5. Estructura de Módulo Propuesto

### 5.1 Nuevo Archivo: `src/utils/economic_calculator.py`

```python
"""
Calculadora de beneficios económicos y ambientales para sistemas GNV
"""
from config import (
    DEFAULT_AHORRO_ECONOMICO,
    DEFAULT_REDUCCION_CO2,
    DEFAULT_REDUCCION_MP,
    DEFAULT_REDUCCION_NOX,
    DEFAULT_PRECIO_DIESEL_COP_LITRO,
    DEFAULT_PRECIO_GNV_COP_M3,
    DEFAULT_ANOS_ANALISIS,
    FACTOR_EMISION_CO2_DIESEL,
    FACTOR_EMISION_MP_DIESEL,
    FACTOR_EMISION_NOX_DIESEL
)

def calcular_ahorro_economico(...):
    """Implementación de cálculo de ahorro económico"""
    pass

def calcular_beneficios_ambientales(...):
    """Implementación de cálculo de beneficios ambientales"""
    pass

def calcular_beneficios_tributarios(...):
    """Implementación de cálculo de beneficios tributarios"""
    pass

def calcular_roi(...):
    """Cálculo de retorno de inversión (ROI)"""
    pass

def calcular_payback_period(...):
    """Cálculo de período de recuperación de inversión"""
    pass
```

---

## 6. Plan de Implementación

### Fase 1: Configuración (1-2 días)
1. Agregar parámetros económicos y ambientales a `src/config.py`
2. Actualizar `docs/PARAMETROS.md` con nueva sección
3. Crear `src/utils/economic_calculator.py` con funciones base

### Fase 2: Funcionalidades (3-5 días)
1. Implementar funciones de cálculo económico
2. Implementar funciones de cálculo ambiental
3. Implementar funciones de cálculo tributario
4. Agregar validaciones y manejo de errores

### Fase 3: Integración (2-3 días)
1. Integrar cálculos económicos en interfaz Streamlit
2. Agregar sección de análisis económico en reportes
3. Agregar sección de beneficios ambientales en reportes
4. Actualizar generación de informes HTML/PDF

### Fase 4: Pruebas y Documentación (2-3 días)
1. Pruebas unitarias de funciones económicas
2. Pruebas de integración
3. Actualizar documentación de usuario
4. Crear ejemplos de uso

**Tiempo Total Estimado:** 8-13 días

---

## 7. Consideraciones Importantes

1. **Valores de Mercado:** Los precios de combustible deben actualizarse regularmente
2. **Normativa:** Los beneficios tributarios dependen de normativa vigente en Colombia
3. **Factores de Emisión:** Pueden variar según calidad del combustible y tecnología
4. **Validación:** Todos los cálculos deben validarse con casos reales
5. **Configurabilidad:** Los parámetros deben ser editables desde la interfaz

---

*Documento creado: 2025-11-20*  
*Última actualización: 2025-11-20*

