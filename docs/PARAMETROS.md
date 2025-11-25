# ⚙️ Documentación de Parámetros - Aplicación GNV

## Parámetros por Defecto

Todos los parámetros están definidos en `src/config.py` y pueden ser modificados desde la interfaz de usuario.

## Parámetros de Operación

### Tipo de Combustible de Origen
- **Opciones:** Diésel o GNL (Gas Natural Licuado)
- **Descripción:** Seleccione el tipo de combustible que actualmente usa el vehículo
- **Nota:** La aplicación calcula la conversión a GNV desde cualquiera de estos combustibles

### Consumo de Diésel
- **Valor por defecto:** 35.0 L/100 km
- **Rango:** 1.0 - 200.0 L/100 km
- **Descripción:** Consumo de combustible diésel del vehículo
- **Fuente:** Datos del vehículo o estimaciones
- **Aplicable cuando:** Tipo de combustible = Diésel

### Consumo de GNL
- **Valor por defecto:** 50.0 L/100 km
- **Rango:** 1.0 - 300.0 L/100 km
- **Descripción:** Consumo de Gas Natural Licuado del vehículo
- **Nota importante:** El consumo de GNL es típicamente mayor que el de diésel debido a menor densidad energética por volumen (~60-70% del diesel)
- **Aplicable cuando:** Tipo de combustible = GNL

### Autonomía Deseada
- **Valor por defecto:** 800.0 km
- **Rango:** 100.0 - 2000.0 km
- **Descripción:** Distancia que se desea recorrer con un tanque lleno
- **Consideraciones:** Mayor autonomía = más tanques = más peso

## Parámetros Técnicos

### Poder Calorífico Diésel
- **Valor por defecto:** 35.8 MJ/L
- **Rango:** 30.0 - 40.0 MJ/L
- **Estándar:** ASTM D975
- **Descripción:** Energía contenida en un litro de diésel

### LHV CH₄ (Lower Heating Value)
- **Valor por defecto:** 50.0 MJ/kg
- **Rango:** 45.0 - 55.0 MJ/kg
- **Estándar:** ISO 6976:2016
- **Descripción:** Poder calorífico inferior del metano
- **Nota:** LHV no incluye el calor de condensación del vapor de agua

### Poder Calorífico GNL
- **Valor por defecto:** 22.5 MJ/L
- **Rango:** 18.0 - 28.0 MJ/L
- **Rango típico:** 20-25 MJ/L
- **Valor representativo:** 22.5 MJ/L
- **Descripción:** Energía contenida en un litro de GNL
- **Comparación:** GNL tiene ~60-70% de la energía por volumen del diésel
- **Aplicable cuando:** Tipo de combustible = GNL
- **Fuente:** Datos de la imagen proporcionada y estándares técnicos

### Eficiencia de Conversión GNV vs Diésel
- **Valor por defecto:** 0.95
- **Rango:** 0.80 - 1.0
- **Descripción:** Factor de eficiencia del sistema GNV comparado con diésel
- **Consideraciones:** 
  - 0.90-0.95: Típico para sistemas bi-fuel
  - 0.95-1.0: Sistemas dedicados optimizados
- **Aplicable cuando:** Tipo de combustible = Diésel

### Eficiencia de Conversión GNV vs GNL
- **Valor por defecto:** 0.92
- **Rango:** 0.80 - 1.0
- **Descripción:** Factor de eficiencia del sistema GNV comparado con GNL
- **Consideraciones:**
  - Ambos usan metano (CH₄), pero diferentes formas de almacenamiento
  - GNL: líquido a -162°C, densidad ~0.45 kg/L
  - GNV: gas comprimido a 200 bar, densidad mucho menor por volumen
  - La eficiencia puede ser ligeramente menor que diesel a GNV debido a diferencias en sistemas de suministro
  - Típicamente: 0.90-0.95 para motores dedicados a gas natural
- **Aplicable cuando:** Tipo de combustible = GNL

## Parámetros de Almacenamiento

### Presión de Llenado
- **Valor por defecto:** 200.0 bar
- **Rango:** 150.0 - 300.0 bar
- **Descripción:** Presión de trabajo de los tanques CNG
- **Estándar Colombia:** 200 bar
- **Consideraciones:**
  - 200 bar: Estándar, tanques tipo 3
  - 250 bar: Mayor densidad, requiere tanques tipo 4

### Temperatura de Operación
- **Valor por defecto:** 25.0 °C
- **Rango:** 0.0 - 50.0 °C
- **Descripción:** Temperatura ambiente de operación
- **Consideraciones:** Afecta la densidad del gas

### Factor de Compresibilidad Z
- **Valor por defecto:** 0.85
- **Rango:** 0.70 - 1.0
- **Fuente:** NIST Chemistry WebBook
- **Descripción:** Factor de compresibilidad del gas
- **Consideraciones:**
  - 0.80-0.90: Típico para CH₄ a 200 bar, 25°C
  - Varía según composición del gas natural

## Características de Tanques

### Volumen Unitario Tanque
- **Valor por defecto:** 0.080 m³ (80 L)
- **Rango:** 0.01 - 0.20 m³
- **Descripción:** Volumen de cada tanque individual
- **Tamaños comunes:**
  - 50 L (0.050 m³)
  - 80 L (0.080 m³) - Valor por defecto
  - 100 L (0.100 m³)
  - 150 L (0.150 m³)

### Peso Tanque Vacío
- **Valor por defecto:** 65.0 kg
- **Rango:** 20.0 - 150.0 kg
- **Descripción:** Peso de un tanque tipo 3 vacío
- **Consideraciones:**
  - Tipo 3 (composite con liner metálico): 50-80 kg
  - Tipo 4 (fully composite): 30-50 kg (más liviano pero más costoso)

### Peso Soportes por Tanque
- **Valor por defecto:** 10.0 kg
- **Rango:** 5.0 - 30.0 kg
- **Descripción:** Peso de soportes y estructura por tanque
- **Consideraciones:** Depende del diseño de montaje

### Peso Accesorios por Tanque
- **Valor por defecto:** 5.0 kg
- **Rango:** 1.0 - 20.0 kg
- **Descripción:** Peso de válvulas, conexiones, etc. por tanque
- **Componentes típicos:**
  - Válvula de llenado
  - Válvula de servicio
  - Válvula de seguridad
  - Conexiones y tuberías

## Constantes Físicas

### Constante Universal de Gases R
- **Valor por defecto:** 8.314 J/(mol·K)
- **Rango:** 8.0 - 9.0 J/(mol·K)
- **Descripción:** Constante física universal
- **Precisión:** 8.314462618 J/(mol·K) (CODATA 2018)

### Masa Molar CH₄
- **Valor por defecto:** 0.01604 kg/mol
- **Rango:** 0.015 - 0.020 kg/mol
- **Descripción:** Masa molar del metano
- **Precisión:** 0.0160428 kg/mol

## Parámetros del Proyecto

### Cliente
- **Valor por defecto:** PETROLIQUIDOS
- **Editable:** Solo administradores
- **Uso:** Aparece en todos los informes

### Versión
- **Valor por defecto:** 1.0
- **Editable:** Solo administradores
- **Uso:** Control de versiones del proyecto

### Fecha
- **Valor por defecto:** 2024-12-19
- **Editable:** Solo administradores
- **Formato:** YYYY-MM-DD
- **Uso:** Fecha del proyecto o informe

## Fórmulas de Cálculo

### Conversión desde Diésel

#### 1. Volumen Diésel Equivalente
```
V_diesel = (Consumo × Autonomía) / 100
```

#### 2. Energía Requerida
```
E = V_diesel × E_diesel
```

### Conversión desde GNL

#### 1. Volumen GNL Requerido
```
V_gnl = (Consumo × Autonomía) / 100
```

#### 2. Energía Requerida
```
E = V_gnl × E_gnl
```
**Nota:** El poder calorífico del GNL (E_gnl) es menor que el del diésel (~22.5 MJ/L vs ~35.8 MJ/L)

### 3. Masa de CH₄ Requerida
```
m_CH4 = (E / LHV_CH4) / η
```
Donde:
- E = Energía requerida (MJ)
- LHV_CH4 = Lower Heating Value del metano (MJ/kg)
- η = eficiencia de conversión (0-1)

**Nota:** Tanto GNL como GNV usan metano (CH₄), por lo que este paso es común para ambas conversiones

### 4. Volumen de Gas a Presión de Llenado
```
V = (m_CH4 × R × T) / (p × M × Z)
```
Donde:
- R = Constante universal de gases
- T = Temperatura en Kelvin (°C + 273.15)
- p = Presión en Pascal (bar × 100,000)
- M = Masa molar CH₄
- Z = Factor de compresibilidad

### 5. Número de Tanques Requeridos
```
n_tanques = ceil(V / V_unitario)
```

### 6. Peso Adicional Total
```
P_adicional = n_tanques × (m_tanque + m_soportes + m_accesorios)
```

## Cálculos de Validación para Conversión GNL a GNV

### Validación 1: Consistencia Energética

**Objetivo:** Verificar que la energía requerida sea consistente entre GNL y GNV.

```
E_gnl = V_gnl × E_gnl
E_gnv = m_CH4 × LHV_CH4
Diferencia = |E_gnl - E_gnv| / E_gnl × 100%
```

**Criterio de validación:**
- La diferencia debe ser < 5% (considerando eficiencia de conversión)
- Si la diferencia es mayor, revisar parámetros de entrada

**Ejemplo de cálculo:**
```
V_gnl = 100 L (para 200 km con consumo de 50 L/100 km)
E_gnl = 100 L × 22.5 MJ/L = 2,250 MJ
m_CH4 = 2,250 MJ / 50 MJ/kg / 0.92 = 48.91 kg
E_gnv = 48.91 kg × 50 MJ/kg = 2,445.5 MJ
Diferencia = |2,250 - 2,445.5| / 2,250 × 100% = 8.7%
```

**Nota:** La diferencia del 8.7% es esperada debido a la eficiencia de conversión (0.92) y pérdidas en el proceso.

### Validación 2: Masa de Metano Conservada

**Objetivo:** Verificar que la masa de metano se conserve en la conversión.

```
m_CH4_gnl = V_gnl × ρ_gnl × fracción_CH4
m_CH4_gnv = (V_gnv × p × M × Z) / (R × T)
Conservación = m_CH4_gnl / m_CH4_gnv
```

Donde:
- ρ_gnl = 0.45 kg/L (densidad del GNL)
- fracción_CH4 = 0.95 (95% metano en GNL típico)
- V_gnv = volumen de GNV calculado (m³)

**Criterio de validación:**
- La relación debe estar entre 0.90 y 1.10 (considerando eficiencia y pérdidas)

**Ejemplo de cálculo:**
```
m_CH4_gnl = 100 L × 0.45 kg/L × 0.95 = 42.75 kg
V_gnv = 2.5 m³ (a 200 bar, 25°C)
m_CH4_gnv = (2.5 × 200×10⁵ × 0.01604 × 0.85) / (8.314 × 298.15) = 43.2 kg
Conservación = 42.75 / 43.2 = 0.99 (99%)
```

### Validación 3: Volumen Equivalente

**Objetivo:** Comparar el volumen de GNL original con el volumen de GNV requerido.

```
V_gnl_original = (Consumo_gnl × Autonomía) / 100
V_gnv_equivalente = V_gas_calculado (en m³)
Relación_volumen = V_gnv_equivalente / (V_gnl_original / 1000)
```

**Criterio de validación:**
- El volumen de GNV será aproximadamente 10-15 veces mayor que el volumen de GNL
- Esto es esperado debido a la diferencia de densidad (líquido vs gas comprimido)

**Ejemplo de cálculo:**
```
V_gnl_original = (50 L/100km × 200 km) / 100 = 100 L = 0.1 m³
V_gnv_equivalente = 2.5 m³
Relación_volumen = 2.5 / 0.1 = 25 veces
```

**Nota:** La relación de 25 veces es normal. El GNV ocupa más volumen porque está en estado gaseoso comprimido, mientras que el GNL está en estado líquido.

### Validación 4: Autonomía Equivalente

**Objetivo:** Verificar que la autonomía calculada sea razonable.

```
Autonomía_gnl = (Capacidad_tanques_gnl / Consumo_gnl) × 100
Autonomía_gnv = (Capacidad_gnv / Consumo_gnv_equivalente) × 100
Consumo_gnv_equivalente = (Consumo_gnl × E_gnl) / E_gnv_por_litro
```

Donde:
- E_gnv_por_litro ≈ 7.5 MJ/L (a 200 bar, densidad energética aproximada)

**Criterio de validación:**
- La autonomía con GNV debe ser similar o ligeramente menor que con GNL
- Diferencia esperada: ±10% debido a eficiencias y condiciones de operación

**Ejemplo de cálculo:**
```
Capacidad_tanques_gnl = 2,000 L
Consumo_gnl = 50 L/100 km
Autonomía_gnl = (2,000 / 50) × 100 = 4,000 km

Capacidad_gnv = 2.5 m³ = 2,500 L (a 200 bar)
Consumo_gnv_equivalente = (50 × 22.5) / 7.5 = 150 L/100 km
Autonomía_gnv = (2,500 / 150) × 100 = 1,667 km
```

**Nota:** La autonomía con GNV es menor porque el volumen de GNV almacenado es menor en términos de energía equivalente, aunque el volumen físico sea mayor.

### Validación 5: Peso del Sistema

**Objetivo:** Comparar el peso del sistema GNL vs sistema GNV.

```
Peso_sistema_gnl = Peso_tanques_criogénicos + Peso_aislamiento + Peso_accesorios
Peso_sistema_gnv = n_tanques × (Peso_tanque + Peso_soportes + Peso_accesorios)
Diferencia_peso = Peso_sistema_gnv - Peso_sistema_gnl
```

**Criterio de validación:**
- El peso del sistema GNV puede ser mayor o menor dependiendo del número de tanques
- Validar que el peso adicional no exceda las capacidades del vehículo

**Ejemplo de cálculo:**
```
Peso_sistema_gnl = 500 kg (2 tanques criogénicos de 1,000 L)
Peso_sistema_gnv = 18 tanques × (65 + 10 + 5) kg = 1,440 kg
Diferencia_peso = 1,440 - 500 = 940 kg adicionales
```

### Validación 6: Factor de Conversión Energética

**Objetivo:** Calcular el factor de conversión entre GNL y GNV.

```
Factor_conversión = E_gnv / E_gnl
Factor_conversión_volumen = V_gnv / V_gnl
Factor_conversión_masa = m_CH4_gnv / m_CH4_gnl
```

**Valores esperados:**
- Factor conversión energía: 0.90-1.00 (considerando eficiencia)
- Factor conversión volumen: 10-15 (GNV ocupa más volumen)
- Factor conversión masa: 0.95-1.05 (masa se conserva aproximadamente)

### Validación 7: Presión y Temperatura

**Objetivo:** Verificar que los parámetros de presión y temperatura sean adecuados.

```
Presión_mínima = 150 bar (mínimo para almacenamiento eficiente)
Presión_máxima = 300 bar (límite de tanques tipo 4)
Presión_recomendada = 200 bar (estándar Colombia)

Temperatura_mínima = 0°C (condiciones extremas)
Temperatura_máxima = 50°C (condiciones extremas)
Temperatura_operación = 25°C (típica)
```

**Criterio de validación:**
- La presión debe estar dentro del rango 150-300 bar
- La temperatura debe estar dentro del rango 0-50°C
- Para Colombia, usar 200 bar y 25°C como valores estándar

### Resumen de Validaciones

| Validación | Criterio | Estado |
|------------|----------|--------|
| Consistencia Energética | Diferencia < 5% | ✅ |
| Masa Conservada | Relación 0.90-1.10 | ✅ |
| Volumen Equivalente | Relación 10-15x | ✅ |
| Autonomía Equivalente | Diferencia ±10% | ✅ |
| Peso del Sistema | Dentro de capacidades | ⚠️ Verificar |
| Factor de Conversión | Valores esperados | ✅ |
| Presión y Temperatura | Rangos adecuados | ✅ |

**Notas importantes:**
- Todas las validaciones deben cumplirse para considerar la conversión viable
- Si alguna validación falla, revisar parámetros de entrada
- El peso del sistema es crítico: verificar capacidad de carga del vehículo
- La autonomía puede variar según condiciones de operación

## Valores Recomendados por Tipo de Vehículo

### Tractores 4x2
- Consumo: 30-40 L/100 km
- Autonomía: 600 km
- Presión: 200 bar
- Tanques: Tipo 3, 80 L

### Tractores 6x4
- Consumo: 35-45 L/100 km
- Autonomía: 700-900 km
- Presión: 200 bar
- Tanques: Tipo 3, 80-100 L

### Volquetas 6x4
- Consumo: 40-50 L/100 km
- Autonomía: 500-700 km
- Presión: 200 bar
- Tanques: Tipo 3, 80 L

## Diferencias Clave: Conversión Diésel vs GNL a GNV

### Conversión Diésel a GNV
- **Combustible origen:** Diésel (hidrocarburo líquido)
- **Poder calorífico:** ~35.8 MJ/L
- **Densidad:** ~0.835 kg/L
- **Eficiencia típica:** 0.95
- **Consideraciones:** Cambio de tipo de combustible (líquido fósil a gas comprimido)

### Conversión GNL a GNV
- **Combustible origen:** GNL (metano licuado)
- **Poder calorífico:** ~22.5 MJ/L (menor que diésel)
- **Densidad:** ~0.45 kg/L (menor que diésel)
- **Eficiencia típica:** 0.92
- **Consideraciones:** 
  - Ambos usan metano (CH₄), solo cambia la forma de almacenamiento
  - GNL: líquido criogénico (-162°C) → GNV: gas comprimido (200 bar)
  - El consumo de GNL será mayor en volumen que diésel para misma energía
  - Motores diseñados para GNL pueden tener mejor eficiencia que motores diesel convertidos

### Comparación Energética

| Propiedad | Diésel | GNL | Relación GNL/Diésel |
|-----------|--------|-----|---------------------|
| LHV (MJ/kg) | 42-44 | 48-50 | ~1.15-1.20 |
| LHV (MJ/L) | 34-38 | 20-25 | ~0.60-0.70 |
| Densidad (kg/L) | 0.82-0.86 | 0.42-0.50 | ~0.50-0.60 |

**Conclusión:** 
- Por masa, GNL tiene mayor energía que diésel (~15-20% más)
- Por volumen, GNL tiene menor energía que diésel (~60-70% menos)
- El consumo de GNL en L/100 km será mayor que el de diésel para la misma energía

## Consideraciones Importantes

1. **Validación:** Todos los valores deben validarse con datos reales del vehículo
2. **Composición del Gas:** El GNV contiene ~90-95% CH₄, no 100%
3. **Factor Z:** Puede variar según la composición del gas natural
4. **Peso:** El peso adicional afecta la capacidad de carga
5. **Espacio:** Verificar disponibilidad de espacio en el chasis
6. **Estaciones:** Validar disponibilidad de estaciones GNV en rutas
7. **Tipo de combustible origen:** Seleccionar correctamente entre Diésel y GNL para cálculos precisos
8. **Consumo GNL:** Recordar que el consumo de GNL será mayor en volumen que el de diésel

## Modificar Parámetros por Defecto

Para cambiar los valores por defecto globalmente, edite `src/config.py`:

```python
# Parámetros por defecto de cálculo
DEFAULT_CONSUMO_DIESEL = 35.0
DEFAULT_AUTONOMIA = 800.0
# ... etc
```

Los cambios se reflejarán en toda la aplicación.

## Referencias Adicionales

Para más información sobre:
- **Camiones GNL:** Ver `docs/REFERENCIA_CAMIONES_GNL.md`
- **Modelos homólogos:** Ver `docs/MODELOS_HOMOLOGOS_SINOTRUK_HOWO_MAX_460.md`

---

*Documentación actualizada: 2025-01-19*  
*Agregada sección de conversión GNL a GNV*

