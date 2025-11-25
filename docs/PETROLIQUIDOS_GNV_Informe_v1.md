# Informe Técnico: Sistema GNV para Vehículos Pesados
## CLIENTE: PETROLIQUIDOS
DESARROLLO: WELDTECH SOLUTION
VERSION: PROPUESTA TECNICA
REVISION: 0 (PROPUESTA PREELIMINAR)
DESARROLLO: WELDTECH SOLUTION
VERSION: PROPUESTA TECNICA
REVISION: 0 (PROPUESTA PREELIMINAR)
## Versión: 1.0
## Fecha: 2024-12-19

---

## 1. Introducción y Relevancia

### 1.1 Contexto
Este informe presenta el diseño e implementación de sistemas de Gas Natural Vehicular (GNV) para vehículos pesados, específicamente adaptado al mercado colombiano y cumpliendo con las normativas nacionales e internacionales aplicables.

### 1.2 Justificación Técnica y Económica
La conversión a GNV ofrece ventajas significativas:
- **Reducción de emisiones**: Hasta 30% menos CO₂, 90% menos NOx y eliminación de material particulado comparado con diésel
- **Ahorro económico**: Reducción de costos de combustible del 30-50% (dependiendo de precios relativos)
- **Disponibilidad**: Infraestructura de abastecimiento en crecimiento en Colombia
- **Rendimiento**: Mantiene potencia y torque del motor original

### 1.3 Alcance del Proyecto
- Diseño de sistema GNV para vehículos pesados (tractores y volquetas)
- Especificación técnica de componentes
- Análisis de costos y viabilidad económica
- Plan de implementación y pruebas
- Evaluación de migración futura a GNL

---

## 2. Alcance y Supuestos

### 2.1 Alcance Técnico
- **Tipo de vehículos**: Tractores 4x2, 6x4 y volquetas 6x4
- **Sistema**: Bi-fuel (GNV + diésel) o dedicado GNV
- **Presión de almacenamiento**: 200-250 bar (tanques tipo 3 o 4)
- **Regulación**: Dos etapas (200-250 bar → 20-40 bar → 7-10 bar)
- **Autonomía objetivo**: 600-800 km según tipo de vehículo

### 2.2 Supuestos Críticos

#### 2.2.1 Supuestos de Operación
| Parámetro | Valor | Unidad | Confianza | Fuente |
|-----------|-------|--------|-----------|--------|
| Consumo diésel (Tractor 4x2) | 35 | L/100 km | Media | Estimación basada en vehículos similares |
| Consumo diésel (Tractor 6x4) | 40 | L/100 km | Media | Estimación basada en vehículos similares |
| Consumo diésel (Volqueta 6x4) | 45 | L/100 km | Media | Estimación basada en vehículos similares |
| Autonomía deseada (Tractor 4x2) | 800 | km | Baja | **ASUNTO: SUPUESTO** - Requiere validación cliente |
| Autonomía deseada (Tractor 6x4) | 700 | km | Baja | **ASUNTO: SUPUESTO** - Requiere validación cliente |
| Autonomía deseada (Volqueta 6x4) | 600 | km | Baja | **ASUNTO: SUPUESTO** - Requiere validación cliente |
| Altitud operativa típica | 0-2000 | m | Media | Colombia - zonas principales |
| Temperatura ambiente | 15-35 | °C | Alta | Clima colombiano |

#### 2.2.2 Supuestos Técnicos
| Parámetro | Valor | Unidad | Confianza | Fuente |
|-----------|-------|--------|-----------|--------|
| Poder calorífico diésel | 35.8 | MJ/L | Alta | ASTM D975 |
| LHV CH₄ (poder calorífico inferior) | 50.0 | MJ/kg | Alta | ISO 6976:2016 |
| Presión de llenado tanques | 200 | bar | Alta | UNECE R110 estándar |
| Temperatura de operación | 298 | K (25°C) | Alta | Condiciones estándar |
| Factor de compresibilidad Z (CH₄ a 200 bar, 25°C) | 0.85 | - | Media | NIST Chemistry WebBook |
| Masa molar CH₄ | 16.04 | g/mol | Alta | Constante física |
| Constante universal gases R | 8.314 | J/(mol·K) | Alta | Constante física |
| Eficiencia conversión GNV vs diésel | 0.95 | - | Media | **ASUNTO: SUPUESTO** - Depende del sistema |

#### 2.2.3 Supuestos de Componentes
| Parámetro | Valor | Unidad | Confianza | Fuente |
|-----------|-------|--------|-----------|--------|
| Volumen unitario tanque tipo 3 | 0.080 | m³ | Media | Proveedores colombianos típicos |
| Peso unitario tanque tipo 3 (vacío) | 65 | kg | Media | **ASUNTO: SUPUESTO** - Varía por fabricante |
| Peso soportes y accesorios (por tanque) | 15 | kg | Baja | **ASUNTO: SUPUESTO** - Requiere diseño específico |

### 2.3 Limitaciones y Exclusiones
- No incluye costos de estación de servicio GNV
- No incluye costos de capacitación de operadores (estimado aparte)
- No incluye costos de mantenimiento preventivo (estimado aparte)
- No incluye costos de homologación vehicular (estimado aparte)
- Asume disponibilidad de estaciones de servicio GNV en rutas operativas

---

## 3. Análisis Técnico

### 3.1 Regulación de Presión en Dos Etapas

#### 3.1.1 Justificación de Rangos de Presión

**Tanques de almacenamiento CNG:**
- **Presión de servicio máxima**: 200 bar (≈2,900 psi)
- **Presión de llenado**: 200-250 bar (≈2,900-3,625 psi)
- **Justificación**: Cumple con UNECE R110, norma internacional para componentes de vehículos CNG. La presión de 200 bar es estándar en Colombia, mientras que 250 bar permite mayor densidad energética pero requiere tanques tipo 4 (composite) más costosos.

**Primera etapa de regulación:**
- **Entrada**: 200-250 bar
- **Salida**: 20-40 bar (≈290-580 psi)
- **Justificación**: Reducción inicial necesaria para proteger componentes aguas abajo. El rango 20-40 bar es estándar en reguladores de primera etapa para vehículos pesados.

**Segunda etapa de regulación:**
- **Entrada**: 20-40 bar
- **Salida**: 7-10 bar (≈100-145 psi)
- **Justificación**: Presión adecuada para sistemas de inyección de gas en motores diésel convertidos. Para inyección directa, puede requerirse hasta 20 bar (caso especial).

**Excepciones:**
- Sistemas de inyección directa de gas pueden requerir presiones de inyección de 15-25 bar
- Motores dedicados GNV pueden operar con presiones ligeramente diferentes según especificaciones del fabricante

#### 3.1.2 Componentes del Sistema de Regulación

1. **Válvula de cierre rápido (Shut-off valve)**: Ubicada en salida de tanques, cierra automáticamente en caso de emergencia
2. **Regulador de primera etapa**: Reduce presión de 200-250 bar a 20-40 bar, incluye calentador de gas (vaporizador)
3. **Filtro de gas**: Protege componentes aguas abajo de impurezas
4. **Regulador de segunda etapa**: Reduce presión a 7-10 bar para inyección
5. **ECU (Engine Control Unit)**: Controla mezcla aire-combustible y sincronización
6. **Inyectores/mezclador**: Suministra gas al motor

### 3.2 Equipamiento Principal

#### 3.2.1 Tanques de Almacenamiento

**Tipo 3 (Composite con liner metálico):**
- Material: Liner de aluminio + envoltura de fibra de carbono/epoxy
- Presión de trabajo: 200 bar (opcional 250 bar)
- Volumen típico: 60-100 L (0.06-0.10 m³)
- Peso: 50-80 kg (vacío)
- Vida útil: 15-20 años o 15,000 ciclos de llenado
- Certificación: UNECE R110, ISO 11439

**Tipo 4 (Fully composite):**
- Material: Liner de polímero + envoltura de fibra de carbono/epoxy
- Presión de trabajo: 200-250 bar
- Volumen típico: 60-120 L
- Peso: 40-70 kg (vacío) - más liviano que tipo 3
- Vida útil: Similar a tipo 3
- Certificación: UNECE R110, ISO 11439
- **Ventaja**: Menor peso, mayor resistencia a corrosión
- **Desventaja**: Mayor costo (20-30% más que tipo 3)

**Recomendación**: Tipo 3 para aplicaciones estándar, Tipo 4 si el peso es crítico.

#### 3.2.2 Sistema de Regulación

**Regulador de primera etapa:**
- Tipo: Presión reducida con calentador integrado
- Rango entrada: 200-250 bar
- Rango salida: 20-40 bar (ajustable)
- Flujo máximo: 200-300 m³/h (NTP)
- Calentador: Eléctrico o por refrigerante del motor
- Certificación: UNECE R110

**Regulador de segunda etapa:**
- Tipo: Presión reducida
- Rango entrada: 20-40 bar
- Rango salida: 7-10 bar (ajustable)
- Flujo máximo: 200-300 m³/h (NTP)
- Certificación: UNECE R110

#### 3.2.3 Sistema de Inyección

**Opción A - Mezclador (Venturi):**
- Tipo: Mezclador aire-gas antes del turbo
- Ventajas: Bajo costo, simplicidad
- Desventajas: Menor eficiencia, pérdida de potencia
- Aplicación: Conversiones económicas

**Opción B - Inyección secuencial:**
- Tipo: Inyectores de gas en múltiple de admisión
- Ventajas: Mejor control, mayor eficiencia
- Desventajas: Mayor costo, más complejo
- Aplicación: Conversiones profesionales

**Opción C - Inyección directa:**
- Tipo: Inyección de gas directamente en cámara de combustión
- Ventajas: Máxima eficiencia, menor emisiones
- Desventajas: Mayor costo, requiere motor dedicado o modificación significativa
- Aplicación: Sistemas de alta gama

**Recomendación**: Opción B (inyección secuencial) para balance costo-beneficio.

#### 3.2.4 ECU y Sensores

- **ECU**: Controla inyección de gas, sincronización, mezcla aire-combustible
- **Sensores**: Presión, temperatura, lambda (O₂), posición del acelerador
- **Válvulas de seguridad**: Shut-off automático, válvulas de alivio de presión

### 3.3 Diagrama de Flujo del Sistema (P&ID)

Ver archivo: `PETROLIQUIDOS_GNV_PID_v1.drawio.xml`

**Descripción simplificada del flujo:**

```
Tanques CNG (200-250 bar)
    ↓
Válvula shut-off
    ↓
Regulador 1ra etapa (200-250 bar → 20-40 bar) + Calentador
    ↓
Filtro de gas
    ↓
Regulador 2da etapa (20-40 bar → 7-10 bar)
    ↓
ECU (control)
    ↓
Inyectores/Mezclador
    ↓
Motor
```

---

## 4. Cálculos Técnicos

### 4.1 Fórmulas Implementadas

#### 4.1.1 Conversión Diésel a GNV - Energía Requerida
\[ E \, (\text{MJ}) = V_{\text{diesel}} \, (\text{L}) \times E_{\text{diesel}} \, (\text{MJ/L}) \]

Donde:
- \( E_{\text{diesel}} = 35.8 \, \text{MJ/L} \) (poder calorífico diésel según ASTM D975)

#### 4.1.2 Conversión Diésel a GNV - Masa de CH₄ Requerida
\[ m_{\text{CH}_4} \, (\text{kg}) = \frac{E \, (\text{MJ})}{\text{LHV}_{\text{CH}_4} \, (\text{MJ/kg}) \times \eta} \]

Donde:
- \( \text{LHV}_{\text{CH}_4} = 50.0 \, \text{MJ/kg} \) (poder calorífico inferior metano según ISO 6976:2016)
- \( \eta = 0.95 \) (eficiencia de conversión GNV vs diésel, típicamente 0.90-0.95)

#### 4.1.3 Conversión GNL a GNV - Energía Requerida
\[ E \, (\text{MJ}) = V_{\text{GNL}} \, (\text{L}) \times E_{\text{GNL}} \, (\text{MJ/L}) \]

Donde:
- \( E_{\text{GNL}} = 22.5 \, \text{MJ/L} \) (poder calorífico GNL, rango típico: 20-25 MJ/L)

**Nota**: El GNL tiene menor densidad energética por volumen que el diésel, pero tanto GNL como GNV usan metano (CH₄) como combustible base. La diferencia principal está en el método de almacenamiento (líquido criogénico vs gas comprimido).

#### 4.1.4 Conversión GNL a GNV - Masa de CH₄ Requerida
\[ m_{\text{CH}_4} \, (\text{kg}) = \frac{E \, (\text{MJ})}{\text{LHV}_{\text{CH}_4} \, (\text{MJ/kg}) \times \eta_{\text{GNL→GNV}}} \]

Donde:
- \( \text{LHV}_{\text{CH}_4} = 50.0 \, \text{MJ/kg} \) (poder calorífico inferior metano)
- \( \eta_{\text{GNL→GNV}} = 0.92 \) (eficiencia de conversión GNL a GNV, típicamente 0.90-0.95)

**Nota**: La eficiencia de conversión GNL→GNV es ligeramente menor que Diésel→GNV debido a pérdidas en el cambio de sistema de almacenamiento (criogénico a comprimido).

#### 4.1.5 Volumen de Gas a Presión de Llenado
Utilizando ecuación de estado de gases reales:

\[ pV = Z \frac{mRT}{M} \]

Despejando volumen:

\[ V \, (\text{m}^3) = \frac{m_{\text{CH}_4} \times R \times T}{p \times M \times Z} \]

Donde:
- \( p = 200 \times 10^5 \, \text{Pa} = 20,000,000 \, \text{Pa} \) (200 bar, o 250 bar para alta presión)
- \( R = 8.314 \, \text{J/(mol·K)} \) (constante universal de gases)
- \( T = 298 \, \text{K} \) (25°C, temperatura de operación)
- \( M = 16.04 \times 10^{-3} \, \text{kg/mol} = 0.01604 \, \text{kg/mol} \) (masa molar del metano)
- \( Z = 0.85 \) (factor de compresibilidad, típicamente 0.80-0.90 para CH₄ a 200 bar, 25°C)

**Simplificación**: Se asume CH₄ puro. En realidad, el gas natural vehicular contiene ~90-95% CH₄, 3-5% etano y trazas de otros hidrocarburos. El factor Z puede variar ligeramente según la composición.

#### 4.1.6 Número de Tanques Requeridos (con flexibilidad de tamaño)
\[ n_{\text{tanques}} = \left\lceil \frac{V_{\text{requerido}} \, (\text{m}^3)}{V_{\text{unitario}} \, (\text{m}^3)} \right\rceil \]

**Importante**: Los cilindros pueden tener diferentes capacidades según las necesidades del proyecto. **No se limita a opciones predefinidas**. El volumen unitario puede variar desde 0.028 m³ (28L) hasta 0.200 m³ (200L) o más, dependiendo de las restricciones de espacio, peso y disponibilidad.

Redondeando hacia arriba (siempre se requiere número entero de tanques).

#### 4.1.7 Peso Adicional Estimado
\[ P_{\text{adicional}} \, (\text{kg}) = n_{\text{tanques}} \times (m_{\text{tanque}} + m_{\text{soportes}} + m_{\text{accesorios}}) \]

Donde:
- \( m_{\text{tanque}} = 30-80 \, \text{kg} \) (peso del tanque vacío, varía según capacidad y tipo: Tipo 3 o Tipo 4)
- \( m_{\text{soportes}} = 10-15 \, \text{kg} \) (peso de soportes y estructura por tanque)
- \( m_{\text{accesorios}} = 5-10 \, \text{kg} \) (peso de válvulas, conexiones, etc. por tanque)

### 4.2 Cálculos para Configuraciones Representativas

#### 4.2.1 Tractor 4x2 (Carretera)

**Parámetros de entrada:**
- Consumo diésel: 35 L/100 km
- Autonomía deseada: 800 km
- Volumen diésel equivalente: \( 35 \times 8 = 280 \, \text{L} \)

**Cálculos:**

1. **Energía requerida:**
   \[ E = 280 \, \text{L} \times 35.8 \, \text{MJ/L} = 10,024 \, \text{MJ} \]

2. **Masa de CH₄ requerida:**
   \[ m_{\text{CH}_4} = \frac{10,024 \, \text{MJ}}{50.0 \, \text{MJ/kg}} = 200.5 \, \text{kg} \]

3. **Volumen de gas a 200 bar:**
   \[ V = \frac{200.5 \times 8.314 \times 298}{20,000,000 \times 0.01604 \times 0.85} = \frac{497,000}{272,680} = 1.82 \, \text{m}^3 \]

4. **Número de tanques (asumiendo tanques de 0.080 m³):**
   \[ n_{\text{tanques}} = \frac{1.82}{0.080} = 22.75 \rightarrow 23 \, \text{tanques} \]

5. **Peso adicional:**
   \[ P_{\text{adicional}} = 23 \times (65 + 10 + 5) = 23 \times 80 = 1,840 \, \text{kg} \]

**Resumen Tractor 4x2:**
- Volumen total requerido: 1.82 m³ (1,820 L)
- Número de tanques: 23 unidades
- Peso adicional: 1,840 kg
- **ASUNTO**: El peso adicional es significativo y puede afectar capacidad de carga

#### 4.2.2 Tractor 6x4 (Mixto)

**Parámetros de entrada:**
- Consumo diésel: 40 L/100 km
- Autonomía deseada: 700 km
- Volumen diésel equivalente: \( 40 \times 7 = 280 \, \text{L} \)

**Cálculos:**

1. **Energía requerida:**
   \[ E = 280 \, \text{L} \times 35.8 \, \text{MJ/L} = 10,024 \, \text{MJ} \]

2. **Masa de CH₄ requerida:**
   \[ m_{\text{CH}_4} = \frac{10,024 \, \text{MJ}}{50.0 \, \text{MJ/kg}} = 200.5 \, \text{kg} \]

3. **Volumen de gas a 200 bar:**
   \[ V = 1.82 \, \text{m}^3 \] (mismo cálculo que Tractor 4x2)

4. **Número de tanques:**
   \[ n_{\text{tanques}} = 23 \, \text{tanques} \]

5. **Peso adicional:**
   \[ P_{\text{adicional}} = 1,840 \, \text{kg} \]

**Resumen Tractor 6x4:**
- Volumen total requerido: 1.82 m³
- Número de tanques: 23 unidades
- Peso adicional: 1,840 kg

#### 4.2.3 Volqueta 6x4 (Obra)

**Parámetros de entrada:**
- Consumo diésel: 45 L/100 km
- Autonomía deseada: 600 km
- Volumen diésel equivalente: \( 45 \times 6 = 270 \, \text{L} \)

**Cálculos:**

1. **Energía requerida:**
   \[ E = 270 \, \text{L} \times 35.8 \, \text{MJ/L} = 9,666 \, \text{MJ} \]

2. **Masa de CH₄ requerida:**
   \[ m_{\text{CH}_4} = \frac{9,666 \, \text{MJ}}{50.0 \, \text{MJ/kg}} = 193.3 \, \text{kg} \]

3. **Volumen de gas a 200 bar:**
   \[ V = \frac{193.3 \times 8.314 \times 298}{20,000,000 \times 0.01604 \times 0.85} = 1.76 \, \text{m}^3 \]

4. **Número de tanques:**
   \[ n_{\text{tanques}} = \frac{1.76}{0.080} = 22.0 \rightarrow 22 \, \text{tanques} \]

5. **Peso adicional:**
   \[ P_{\text{adicional}} = 22 \times 80 = 1,760 \, \text{kg} \]

**Resumen Volqueta 6x4:**
- Volumen total requerido: 1.76 m³
- Número de tanques: 22 unidades
- Peso adicional: 1,760 kg

### 4.3 Tabla Resumen de Cálculos - Conversión Diésel a GNV

| Configuración | Consumo (L/100km) | Autonomía (km) | Energía (MJ) | Masa CH₄ (kg) | Volumen (m³) | N° Tanques | Peso Adicional (kg) |
|---------------|-------------------|----------------|--------------|---------------|--------------|------------|---------------------|
| Tractor 4x2 | 35 | 800 | 10,024 | 200.5 | 1.82 | 23 | 1,840 |
| Tractor 6x4 | 40 | 700 | 10,024 | 200.5 | 1.82 | 23 | 1,840 |
| Volqueta 6x4 | 45 | 600 | 9,666 | 193.3 | 1.76 | 22 | 1,760 |

---

### 4.4 Análisis de Pérdida de Autonomía en Conversión GNL→GNV

#### 4.4.1 Comparación Técnica de Densidades Energéticas

La conversión de GNL a GNV resulta en una reducción significativa de autonomía debido a la diferencia en densidad energética por volumen:

| Combustible | Densidad Energética | Estado | Temperatura/Presión |
|-------------|---------------------|--------|---------------------|
| GNL | ~22.5 MJ/L | Líquido criogénico | -162°C, presión atmosférica |
| GNV (200 bar) | ~7.5 MJ/m³ ≈ 7.5 MJ/L | Gas comprimido | Ambiente, 200 bar |
| GNV (250 bar) | ~9.4 MJ/m³ ≈ 9.4 MJ/L | Gas comprimido | Ambiente, 250 bar |

**Factor de conversión volumétrico**: Se requiere aproximadamente **3 veces más volumen** de GNV (a 200 bar) para almacenar la misma energía que GNL.

#### 4.4.2 Cálculo de Reducción Porcentual de Autonomía

La reducción de autonomía se puede estimar comparando las capacidades energéticas:

\[ \text{Reducción} = 1 - \frac{E_{\text{GNV}} / V_{\text{GNV}}}{E_{\text{GNL}} / V_{\text{GNL}}} \]

**Ejemplo práctico**: Vehículo con sistema GNL actual

- **Capacidad GNL**: 2,000 L
- **Consumo GNL**: 50 L/100 km
- **Autonomía GNL**: (2,000 / 50) × 100 = **4,000 km teóricos** (~1,800-2,000 km reales considerando reserva)

Para equivalente energético con GNV:
- **Energía almacenada GNL**: 2,000 L × 22.5 MJ/L = 45,000 MJ
- **Volumen GNV requerido** (a 200 bar): ~6,000 m³ (equivalente energético)
- **Autonomía GNV estimada**: ~230-355 km (según configuración de cilindros)

**Reducción típica: 55-85%** comparado con GNL

#### 4.4.3 Impacto Operativo de la Reducción de Autonomía

La reducción significativa de autonomía tiene implicaciones operativas importantes:

1. **Frecuencia de recarga**: De 1 recarga cada 1,800 km (GNL) a 1 recarga cada 230-355 km (GNV)
2. **Planificación de rutas**: Requiere mapeo detallado de estaciones GNV disponibles
3. **Tiempo de operación**: Más paradas para recarga afectan eficiencia operativa
4. **Costo operativo**: Mayor número de recargas puede incrementar costos

#### 4.4.4 Estrategias de Mitigación

Para reducir el impacto de la pérdida de autonomía, se pueden considerar las siguientes estrategias:

1. **Cilindros de mayor capacidad**: Usar cilindros de 100L, 150L o 200L en lugar de 80L para maximizar capacidad en mismo espacio
2. **Mayor presión de trabajo**: Operar a 250 bar en lugar de 200 bar (requiere tanques tipo 4 certificados, mayor costo)
3. **Optimización de espacio**: Maximizar número de cilindros según espacio disponible en chasis
4. **Sistema híbrido**: Considerar mantener GNL como sistema principal con GNV complementario para flexibilidad
5. **Reducción de autonomía objetivo**: Si operativamente es aceptable, reducir autonomía objetivo puede optimizar costo y peso

---

### 4.5 Flexibilidad en Configuración de Cilindros

#### 4.5.1 Rango de Capacidades Disponibles

Los cilindros GNV están disponibles en un amplio rango de capacidades, **no limitándose a opciones predefinidas**. La selección debe basarse en las necesidades específicas del proyecto:

| Capacidad | Volumen (m³) | Aplicación Típica | Peso Aprox. (kg) | Longitud Aprox. (mm) | Diámetro Aprox. (mm) |
|-----------|--------------|-------------------|------------------|----------------------|---------------------|
| 28 L | 0.028 | Motocicletas, vehículos pequeños | 31 | 850 | 230 |
| 40 L | 0.040 | Automóviles, camionetas pequeñas | 45 | 870 | 250 |
| 55 L | 0.055 | Camionetas, vehículos medianos | 62 | 890 | 280 |
| 65 L | 0.065 | Vehículos medianos-grandes | 70 | 950 | 300 |
| 80 L | 0.080 | Vehículos pesados, buses pequeños | 65-80 | 1000 | 320 |
| 95 L | 0.095 | Buses, camiones | 100 | 1040 | 350 |
| 100 L | 0.100 | Camiones, tractores | 110 | 1050 | 360 |
| 150 L | 0.150 | Vehículos pesados grandes | 130-150 | 1200 | 400 |
| 200 L+ | 0.200+ | Aplicaciones especiales | 180-220 | 1400+ | 450+ |

**Nota**: Las capacidades pueden variar según fabricante y normativas locales. Se recomienda consultar con proveedores para opciones específicas y disponibilidad. Los cilindros pueden ser personalizados según necesidades del proyecto.

#### 4.5.2 Criterios de Selección Óptima

Al seleccionar la configuración de cilindros, considerar los siguientes criterios:

1. **Requerimientos energéticos**: 
   - Autonomía deseada
   - Consumo del vehículo
   - Perfil de operación (carretera vs urbano)

2. **Restricciones de espacio**: 
   - Dimensiones disponibles en el chasis
   - Altura máxima permitida
   - Ancho y largo disponibles

3. **Restricciones de peso**: 
   - Capacidad de carga del vehículo
   - Peso máximo permitido por eje
   - Impacto en capacidad de carga útil

4. **Disponibilidad de estaciones**: 
   - Presión de llenado disponible (200 bar estándar vs 250 bar)
   - Cobertura de estaciones en rutas operativas

5. **Costo vs beneficio**: 
   - Balance entre número de cilindros, capacidad y costo total
   - Costo de instalación y mantenimiento

6. **Flexibilidad futura**: 
   - Posibilidad de agregar o modificar cilindros posteriormente
   - Compatibilidad con futuras expansiones

#### 4.5.3 Comparación de Configuraciones Alternativas

Para un mismo requerimiento energético, se pueden considerar múltiples configuraciones. A continuación se presenta un ejemplo comparativo:

**Requerimiento**: 1.33 m³ de GNV (a 200 bar) para autonomía de 800 km equivalente (conversión GNL a GNV)

| Configuración | Cilindros | Capacidad Total | N° Cilindros | Peso Aprox. (kg) | Ventajas | Desventajas |
|---------------|-----------|----------------|--------------|------------------|----------|-------------|
| **Opción A** | 80 L | 1.36 m³ | 17 | 1,360 | Flexibilidad, fácil mantenimiento | Mayor número de conexiones |
| **Opción B** | 100 L | 1.40 m³ | 14 | 1,120 | Menos cilindros, menor peso total | Menos flexibilidad |
| **Opción C** | 150 L | 1.35 m³ | 9 | 1,350 | Mínimo número de cilindros | Menos flexibilidad, cilindros más pesados |
| **Opción D** | 95 L @ 250 bar | 1.33 m³ | 14 | 1,680 | Menor volumen, menos cilindros | Requiere estaciones 250 bar, mayor costo |

Cada opción tiene ventajas y desventajas en términos de espacio, peso, costo y flexibilidad. La selección debe basarse en las prioridades específicas del proyecto.

#### 4.5.4 Consideraciones de Presión (200 bar vs 250 bar)

| Aspecto | 200 bar (Estándar) | 250 bar (Alta Presión) |
|---------|---------------------|-------------------------|
| **Densidad energética** | ~7.5 MJ/m³ | ~9.4 MJ/m³ (+25%) |
| **Disponibilidad estaciones** | Alta (estándar Colombia) | Media (menos común) |
| **Tipo de tanques** | Tipo 3 o 4 | Principalmente Tipo 4 |
| **Costo tanques** | Estándar | 20-30% mayor |
| **Seguridad** | Estándar | Requiere mayor cuidado y certificaciones |
| **Reducción volumen** | Base | -15% a -20% vs 200 bar |
| **Certificaciones** | UNECE R110 estándar | UNECE R110 para alta presión |

**Recomendación**: Evaluar disponibilidad de estaciones de 250 bar en rutas operativas antes de seleccionar esta opción. La mayoría de estaciones en Colombia operan a 200 bar.

---

### 4.6 Ejemplo de Cálculo Completo - Conversión GNL a GNV con Múltiples Configuraciones

#### 4.6.1 Caso de Estudio: Tractor con Motor Weichai WP13NG460E62

**Parámetros de entrada:**
- Motor: Weichai WP13NG460E62 (dedicado GNL)
- Consumo GNL: 50 L/100 km
- Autonomía actual GNL: ~1,800 km (con 2,000 L de GNL)
- Autonomía deseada equivalente: 800 km
- Presión de llenado: 200 bar (estándar) o 250 bar (opción)
- Temperatura: 25°C

#### 4.6.2 Cálculo de Sistema GNV Equivalente

**Paso 1: Volumen GNL requerido para autonomía deseada**
\[ V_{\text{GNL}} = \frac{50 \times 800}{100} = 400 \, \text{L} \]

**Paso 2: Energía requerida**
\[ E = 400 \, \text{L} \times 22.5 \, \text{MJ/L} = 9,000 \, \text{MJ} \]

**Paso 3: Masa de CH₄ requerida (η = 0.92)**
\[ m_{\text{CH}_4} = \frac{9,000 \, \text{MJ}}{50.0 \, \text{MJ/kg} \times 0.92} = 195.7 \, \text{kg} \]

**Paso 4: Volumen de gas a 200 bar**
\[ V = \frac{195.7 \times 8.314 \times 298}{20,000,000 \times 0.01604 \times 0.85} = 1.33 \, \text{m}^3 \]

#### 4.6.3 Comparación de Configuraciones Alternativas

**Opción 1: Cilindros de 80L (Configuración Estándar)**
- Número de cilindros: 17 × 80L = 1.36 m³
- Peso adicional: 17 × 80 kg = 1,360 kg
- **Ventajas**: Flexibilidad, fácil mantenimiento, amplia disponibilidad
- **Desventajas**: Mayor número de conexiones, más puntos de falla potenciales
- **Autonomía estimada**: ~230-280 km

**Opción 2: Cilindros de 100L (Configuración Balanceada)**
- Número de cilindros: 14 × 100L = 1.40 m³
- Peso adicional: 14 × 80 kg = 1,120 kg
- **Ventajas**: Menos cilindros, menor peso total, menor número de conexiones
- **Desventajas**: Menos flexibilidad para futuras modificaciones
- **Autonomía estimada**: ~240-290 km

**Opción 3: Cilindros de 150L (Configuración Compacta)**
- Número de cilindros: 9 × 150L = 1.35 m³
- Peso adicional: 9 × 150 kg = 1,350 kg
- **Ventajas**: Mínimo número de cilindros, máximo aprovechamiento de espacio
- **Desventajas**: Menos flexibilidad, cilindros más pesados, puede requerir refuerzos estructurales
- **Autonomía estimada**: ~230-280 km

**Opción 4: Cilindros de 95L a 250 bar (Alta Presión)**
- Volumen requerido a 250 bar: ~1.06 m³ (menor por mayor densidad energética)
- Número de cilindros: 12 × 95L = 1.14 m³
- Peso adicional: 12 × 100 kg = 1,200 kg
- **Ventajas**: Menor volumen, menos cilindros, mayor densidad energética
- **Desventajas**: Requiere estaciones de 250 bar (menos disponibles), mayor costo de tanques tipo 4, mayor complejidad
- **Autonomía estimada**: ~230-280 km

#### 4.6.4 Comparación de Resultados

| Configuración | N° Cilindros | Volumen (m³) | Peso (kg) | Autonomía (km) | Reducción vs GNL | Costo Relativo |
|---------------|--------------|--------------|-----------|----------------|------------------|----------------|
| **GNL Actual** | 2 × 1,000L | 2,000 L | ~500 | 1,800 | Base | Base |
| **Opción 1 (80L)** | 17 | 1.36 | 1,360 | 230-280 | 84-87% | ⭐⭐⭐ |
| **Opción 2 (100L)** | 14 | 1.40 | 1,120 | 240-290 | 84-87% | ⭐⭐⭐ |
| **Opción 3 (150L)** | 9 | 1.35 | 1,350 | 230-280 | 84-87% | ⭐⭐⭐⭐ |
| **Opción 4 (95L @ 250 bar)** | 12 | 1.14 | 1,200 | 230-280 | 84-87% | ⭐⭐⭐⭐⭐ |

**Conclusión**: Todas las opciones resultan en una reducción significativa de autonomía (84-87%) comparado con el sistema GNL actual. La selección debe basarse en:
- Disponibilidad de espacio en chasis
- Restricciones de peso
- Disponibilidad de estaciones (200 bar vs 250 bar)
- Presupuesto disponible
- Flexibilidad operativa requerida

---

## 5. Análisis de Sensibilidad

### 5.1 Variación de Consumo de Combustible (±10%, ±20%)

**Tractor 4x2 - Autonomía 800 km:**

| Variación | Consumo (L/100km) | Energía (MJ) | Masa CH₄ (kg) | Volumen (m³) | N° Tanques | Peso (kg) |
|-----------|-------------------|--------------|---------------|--------------|------------|-----------|
| -20% | 28.0 | 8,019 | 160.4 | 1.46 | 19 | 1,520 |
| -10% | 31.5 | 9,021 | 180.4 | 1.64 | 21 | 1,680 |
| Base | 35.0 | 10,024 | 200.5 | 1.82 | 23 | 1,840 |
| +10% | 38.5 | 11,026 | 220.5 | 2.01 | 26 | 2,080 |
| +20% | 42.0 | 12,029 | 240.6 | 2.19 | 28 | 2,240 |

**Impacto**: Un aumento del 20% en consumo requiere 5 tanques adicionales (+22%) y 400 kg más de peso.

### 5.2 Variación de Autonomía (±10%, ±20%)

**Tractor 4x2 - Consumo 35 L/100km:**

| Variación | Autonomía (km) | Energía (MJ) | Masa CH₄ (kg) | Volumen (m³) | N° Tanques | Peso (kg) |
|-----------|----------------|--------------|---------------|--------------|------------|-----------|
| -20% | 640 | 8,019 | 160.4 | 1.46 | 19 | 1,520 |
| -10% | 720 | 9,021 | 180.4 | 1.64 | 21 | 1,680 |
| Base | 800 | 10,024 | 200.5 | 1.82 | 23 | 1,840 |
| +10% | 880 | 11,026 | 220.5 | 2.01 | 26 | 2,080 |
| +20% | 960 | 12,029 | 240.6 | 2.19 | 28 | 2,240 |

**Impacto**: Similar al consumo. Reducir autonomía en 20% ahorra 4 tanques y 320 kg.

### 5.3 Variación de Presión de Llenado

**Tractor 4x2 - Masa CH₄ 200.5 kg:**

| Presión (bar) | Presión (psi) | Factor Z | Volumen (m³) | N° Tanques | Reducción vs 200 bar |
|---------------|---------------|----------|--------------|------------|---------------------|
| 200 | 2,900 | 0.85 | 1.82 | 23 | Base |
| 250 | 3,625 | 0.80 | 1.55 | 20 | -13% volumen, -3 tanques |

**Impacto**: Aumentar presión a 250 bar reduce volumen en ~15% pero requiere tanques tipo 4 más costosos.

### 5.4 Variación de Temperatura

**Tractor 4x2 - Masa CH₄ 200.5 kg, Presión 200 bar:**

| Temperatura (°C) | Temperatura (K) | Factor Z | Volumen (m³) | N° Tanques | Variación vs 25°C |
|------------------|-----------------|----------|--------------|------------|-------------------|
| 15 | 288 | 0.87 | 1.77 | 23 | -2.7% |
| 25 | 298 | 0.85 | 1.82 | 23 | Base |
| 35 | 308 | 0.83 | 1.87 | 24 | +2.7% |

**Impacto**: Menor que otras variables. La temperatura afecta principalmente durante el llenado.

### 5.5 Conclusiones del Análisis de Sensibilidad

1. **Consumo y autonomía** son los factores más críticos. Reducir autonomía objetivo puede reducir significativamente costo y peso.
2. **Presión de llenado** a 250 bar ofrece ahorro de espacio pero mayor costo de tanques.
3. **Temperatura** tiene impacto menor en el diseño final.
4. **Recomendación**: Validar con cliente consumo real y autonomía mínima aceptable antes de dimensionar definitivamente.

---

## 6. Comparativa GNV vs GNL

### 6.1 Comparativa Técnica

| Aspecto | GNV (CNG) | GNL (LNG) |
|---------|-----------|-----------|
| **Estado de almacenamiento** | Gas comprimido (200-250 bar) | Líquido criogénico (-162°C) |
| **Densidad energética** | ~8-10 MJ/L (a 200 bar) | ~22 MJ/L |
| **Tipo de tanques** | Tipo 3 o 4 (composite) | Tanques criogénicos (doble pared, vacío) |
| **Peso sistema** | Alto (tanques pesados) | Medio (tanques livianos pero aislados) |
| **Volumen requerido** | Alto (más tanques) | Bajo (menos tanques) |
| **Presión operativa** | 200-250 bar | Presión atmosférica (con presión interna baja) |
| **Temperatura operativa** | Ambiente | -162°C (requiere aislamiento) |
| **Autonomía equivalente** | Menor (más volumen) | Mayor (menos volumen) |
| **Infraestructura** | Estaciones de compresión | Estaciones de licuefacción/regasificación |
| **Disponibilidad en Colombia** | Mayor (más estaciones) | Menor (pocas estaciones) |
| **Costo de conversión** | Menor | Mayor (20-30% más) |
| **Mantenimiento** | Moderado | Mayor (sistemas criogénicos) |
| **Vida útil tanques** | 15-20 años | 10-15 años |

### 6.2 Comparativa Económica

**Supuestos:**
- Precio GNV: $1.50 USD/m³ (equivalente energético a diésel)
- Precio GNL: $1.40 USD/m³ (equivalente energético)
- Precio diésel: $1.00 USD/L
- Consumo: 35 L/100 km (diésel)
- Distancia anual: 100,000 km

**Cálculo anual (Tractor 4x2):**

| Concepto | Diésel | GNV | GNL |
|----------|--------|-----|-----|
| Consumo anual | 35,000 L | 28,000 m³ | 12,700 L (equivalente) |
| Costo combustible | $35,000 | $42,000 | $17,780 |
| **Ahorro vs diésel** | - | -$7,000 | +$17,220 |

**Nota**: Los precios son ilustrativos y deben validarse con mercado colombiano actual.

### 6.3 Migración GNV → GNL

**Cambios mínimos y críticos:**

1. **Tanques**: Reemplazar tanques CNG por tanques criogénicos (costo: +$15,000-25,000 USD por vehículo)
2. **Sistema de vaporización**: Agregar vaporizador (costo: +$2,000-3,000 USD)
3. **Bombas**: Agregar bomba de transferencia (costo: +$1,000-2,000 USD)
4. **Aislamiento**: Mejorar aislamiento térmico (costo: +$1,000 USD)
5. **Certificaciones**: Nueva homologación (costo: +$2,000-5,000 USD)

**CAPEX incremental estimado**: 30-40% adicional sobre sistema GNV base.

**Ventaja**: Los sistemas de regulación e inyección pueden reutilizarse parcialmente.

**Recomendación**: Si se planea migración futura a GNL, considerar diseño modular desde el inicio.

---

## 7. Regulaciones y Certificaciones Aplicables

### 7.1 Normativas Nacionales (Colombia)

#### 7.1.1 Resolución 957 de 2012 (MinComercio)
- **Título**: Reglamento Técnico para talleres, equipos y procesos de conversión a gas natural comprimido para uso vehicular
- **Alcance**: Establece requisitos para talleres de conversión, equipos y procesos
- **Requisitos clave**:
  - Talleres deben estar certificados
  - Equipos deben cumplir UNECE R110 o equivalentes
  - Inspección técnica vehicular post-conversión
- **Fuente**: Ministerio de Comercio, Industria y Turismo

#### 7.1.2 Resolución 180540 de 2010 (MinTransporte)
- **Título**: Reglamento para la conversión de vehículos a gas natural
- **Alcance**: Requisitos técnicos y de seguridad para vehículos convertidos
- **Requisitos clave**:
  - Certificación de componentes
  - Inspección técnica vehicular
  - Registro en RUNT (Registro Único Nacional de Tránsito)

#### 7.1.3 NTC 3949
- **Título**: Estaciones de regulación de presión, líneas de transporte y líneas primarias de redes de distribución de gas combustible
- **Alcance**: Aplicable a estaciones de servicio GNV
- **Relevancia**: Indirecta (infraestructura de abastecimiento)

#### 7.1.4 RETIE (Reglamento Técnico de Instalaciones Eléctricas)
- **Alcance**: Instalaciones eléctricas asociadas a sistemas GNV (ECU, sensores, calentadores)
- **Requisitos clave**:
  - Protecciones eléctricas adecuadas
  - Certificación de instalaciones eléctricas

### 7.2 Normativas Internacionales

#### 7.2.1 UNECE R110
- **Título**: Uniform provisions concerning the approval of:
  - I. Specific components of motor vehicles using compressed natural gas (CNG) in their propulsion system
  - II. Vehicles with regard to the installation of specific components for the use of compressed natural gas (CNG) in their propulsion system
- **Alcance**: Componentes y vehículos CNG
- **Requisitos clave**:
  - Certificación de tanques (tipo 3 o 4)
  - Certificación de reguladores
  - Certificación de válvulas de seguridad
  - Pruebas de presión y fatiga
- **Vida útil tanques**: 15-20 años o 15,000 ciclos
- **Fuente**: United Nations Economic Commission for Europe

#### 7.2.2 ISO 11439
- **Título**: Gas cylinders — High pressure cylinders for the on-board storage of natural gas as a fuel for automotive vehicles
- **Alcance**: Especificaciones técnicas para tanques CNG
- **Relevancia**: Complementa UNECE R110

#### 7.2.3 ISO 15500 (series)
- **Título**: Road vehicles — Compressed natural gas (CNG) fuel systems
- **Alcance**: Componentes de sistemas CNG (reguladores, válvulas, etc.)
- **Relevancia**: Especificaciones técnicas de componentes

#### 7.2.4 SAE J1616
- **Título**: Recommended Practice for Compressed Natural Gas Vehicle Fuel
- **Alcance**: Especificaciones de calidad de gas natural vehicular
- **Relevancia**: Calidad del combustible

### 7.3 Certificaciones Requeridas

1. **Tanques CNG**: Certificación UNECE R110 o equivalente
2. **Reguladores**: Certificación UNECE R110
3. **Válvulas de seguridad**: Certificación UNECE R110
4. **Taller de conversión**: Certificación según Resolución 957/2012
5. **Vehículo convertido**: Inspección técnica vehicular y registro en RUNT

### 7.4 Checklist de Cumplimiento

- [ ] Todos los tanques tienen certificación UNECE R110
- [ ] Reguladores certificados UNECE R110
- [ ] Válvulas de seguridad certificadas
- [ ] Taller de conversión certificado
- [ ] Instalación eléctrica cumple RETIE
- [ ] Inspección técnica vehicular programada
- [ ] Registro en RUNT actualizado
- [ ] Manual de operación y mantenimiento disponible

---

## 8. Riesgos, Plan de Pruebas y Cronograma

### 8.1 Matriz de Riesgos

| Riesgo | Probabilidad | Impacto | Severidad | Mitigación |
|--------|--------------|---------|-----------|------------|
| **Falta de disponibilidad de estaciones GNV en rutas** | Media | Alto | Alta | Mapear rutas y estaciones antes de conversión; considerar estación propia |
| **Sobredimensionamiento de sistema (más tanques de los necesarios)** | Alta | Medio | Media | Validar consumo y autonomía real con cliente antes de dimensionar |
| **Peso adicional afecta capacidad de carga** | Alta | Alto | Alta | Evaluar impacto en capacidad de carga; considerar tanques tipo 4 (más livianos) |
| **Fallo de componentes (tanques, reguladores)** | Baja | Muy Alto | Alta | Usar solo componentes certificados UNECE R110; mantenimiento preventivo |
| **No cumplimiento normativo** | Baja | Muy Alto | Alta | Verificar certificaciones antes de compra; asesoría legal/regulatoria |
| **Retrasos en entrega de componentes** | Media | Medio | Media | Incluir contingencia en cronograma; múltiples proveedores |
| **Variación de precios de componentes** | Media | Medio | Media | Cotizar múltiples proveedores; incluir contingencia en presupuesto |
| **Incompatibilidad con motor específico** | Baja | Alto | Media | Validar compatibilidad con fabricante motor antes de conversión |
| **Dificultad en homologación** | Baja | Alto | Media | Asesoría con taller certificado; documentación completa |

### 8.2 Plan de Pruebas

#### 8.2.1 Pruebas en Banco (Pre-instalación)

**Objetivo**: Validar componentes antes de instalación en vehículo.

| Prueba | Criterio de Aceptación | Método |
|--------|------------------------|--------|
| **Prueba de presión tanques** | Sin fugas a 1.5x presión de trabajo (300 bar) | Presurizar y monitorear caída de presión |
| **Prueba de flujo reguladores** | Flujo ≥ 200 m³/h a presión nominal | Medición con flujómetro |
| **Prueba de calentador** | Temperatura salida ≥ 0°C a flujo máximo | Medición con termómetro |
| **Prueba de válvulas de seguridad** | Activación a presión correcta (±5%) | Presurizar hasta activación |
| **Prueba de hermeticidad** | Sin fugas detectables (burbujeo) | Prueba con solución jabonosa |

#### 8.2.2 Pruebas en Campo (Post-instalación)

**Objetivo**: Validar funcionamiento del sistema completo en condiciones reales.

| Prueba | Criterio de Aceptación | Método |
|--------|------------------------|--------|
| **Prueba de autonomía** | Autonomía ≥ 90% de autonomía objetivo | Prueba de ruta con tanque lleno hasta agotamiento |
| **Prueba de consumo** | Consumo GNV ≤ 1.1x consumo diésel equivalente | Medición en ruta de 500 km |
| **Prueba de potencia** | Potencia ≥ 95% de potencia original | Dinamómetro |
| **Prueba de emisiones** | Emisiones dentro de límites normativos | Análisis de gases de escape |
| **Prueba de seguridad** | Sin fugas, válvulas funcionan correctamente | Inspección visual y funcional |
| **Prueba de vibraciones** | Sin daños después de 1,000 km | Inspección post-prueba |

#### 8.2.3 Criterios de Aceptación Cuantitativos

- **Autonomía**: ≥ 90% de autonomía objetivo
- **Consumo**: ≤ 110% de consumo diésel equivalente (energético)
- **Potencia**: ≥ 95% de potencia original
- **Emisiones NOx**: ≤ 80% de emisiones diésel original
- **Emisiones CO**: ≤ 50% de emisiones diésel original
- **Fugas**: Cero fugas detectables
- **Temperatura operativa**: -10°C a +50°C sin fallos

### 8.3 Cronograma Propuesto

**Fase 1: Estudio y Diseño (4-6 semanas)**
- Semana 1-2: Validación de requerimientos con cliente
- Semana 3-4: Diseño detallado y especificaciones
- Semana 5-6: Revisión y aprobación de diseño

**Fase 2: Adquisición (6-8 semanas)**
- Semana 7-8: Cotización y selección de proveedores
- Semana 9-12: Orden de compra y fabricación/importación
- Semana 13-14: Recepción y verificación de componentes

**Fase 3: Instalación (2-3 semanas)**
- Semana 15: Preparación de vehículo y montaje de tanques
- Semana 16: Instalación de sistema de regulación e inyección
- Semana 17: Cableado, sensores y ECU

**Fase 4: Pruebas y Homologación (3-4 semanas)**
- Semana 18: Pruebas en banco
- Semana 19-20: Pruebas en campo
- Semana 21: Ajustes y optimización
- Semana 22: Homologación e inspección técnica vehicular

**Total estimado**: 22 semanas (5.5 meses) desde inicio hasta vehículo homologado.

**Hitos críticos:**
1. Aprobación de diseño (Semana 6)
2. Orden de compra componentes (Semana 8)
3. Recepción componentes (Semana 14)
4. Instalación completa (Semana 17)
5. Pruebas exitosas (Semana 20)
6. Homologación (Semana 22)

---

## 9. Decisiones Pendientes / Checklist para Cliente

### 9.1 Preguntas Prioritarias (ALTA PRIORIDAD)

1. **Modelos específicos de vehículos**
   - ¿Marca, modelo y año de los vehículos a convertir?
   - ¿Potencia y torque del motor?
   - ¿Normativa de emisiones que cumple actualmente (Euro IV, V, VI)?

2. **Presupuesto**
   - ¿Presupuesto máximo por unidad (COP o USD)?
   - ¿Rango de inversión total para la flota?

3. **Perfil operativo real**
   - ¿Kilómetros recorridos por día/por mes?
   - ¿Porcentaje de operación en carretera vs urbano?
   - ¿Altitud típica de operación?

4. **Tipo de conversión**
   - ¿Bi-fuel (GNV + diésel) o dedicado GNV?
   - ¿Exigencia de compatibilidad inmediata con GNL?

5. **Plazos**
   - ¿Plazo objetivo para primera unidad piloto?
   - ¿Plazo objetivo para conversión de flota completa?

### 9.2 Validaciones Requeridas (MEDIA PRIORIDAD)

- [ ] Validar consumo real de combustible (no estimado)
- [ ] Validar autonomía mínima aceptable
- [ ] Validar disponibilidad de estaciones GNV en rutas operativas
- [ ] Validar impacto de peso adicional en capacidad de carga
- [ ] Validar preferencia por tanques tipo 3 vs tipo 4
- [ ] Validar preferencia por sistema de inyección (mezclador vs secuencial)
- [ ] Validar disponibilidad de taller certificado para instalación
- [ ] Validar requisitos de mantenimiento y disponibilidad de repuestos

### 9.3 Supuestos que Requieren Confirmación

| Supuesto | Valor Asumido | Confianza | Acción Requerida |
|----------|---------------|-----------|------------------|
| Consumo diésel Tractor 4x2 | 35 L/100 km | Media | Validar con datos reales |
| Consumo diésel Tractor 6x4 | 40 L/100 km | Media | Validar con datos reales |
| Consumo diésel Volqueta 6x4 | 45 L/100 km | Media | Validar con datos reales |
| Autonomía deseada | 600-800 km | Baja | **VALIDAR CON CLIENTE** |
| Eficiencia conversión GNV | 95% vs diésel | Media | Validar con pruebas |
| Volumen unitario tanque | 0.080 m³ | Media | Confirmar con proveedor |
| Peso unitario tanque | 65 kg | Media | Confirmar con proveedor |
| Tasa de cambio USD/COP | 3,800 | Baja | Actualizar al momento de cotización |

### 9.4 Items de Alto Riesgo que Requieren Atención Inmediata

1. **Peso adicional (1,760-1,840 kg)**: Puede afectar significativamente capacidad de carga. Evaluar impacto económico.
2. **Número de tanques (22-23 unidades)**: Requiere espacio significativo. Validar disponibilidad de espacio en chasis.
3. **Autonomía objetivo**: Si se puede reducir, se ahorra significativamente en costo y peso.
4. **Disponibilidad de estaciones GNV**: Crítico para viabilidad operativa.

---

## 10. Conclusiones y Recomendaciones

### 10.1 Conclusiones Técnicas

1. **Viabilidad técnica**: La conversión a GNV es técnicamente viable para los tres tipos de vehículos considerados.

2. **Dimensionamiento**: Para autonomías de 600-800 km, se requieren 22-23 tanques tipo 3, con peso adicional de 1,760-1,840 kg.

3. **Impacto de peso**: El peso adicional es significativo y debe evaluarse su impacto en capacidad de carga y economía operativa.

4. **Rangos de presión**: Los rangos propuestos (200-250 bar → 20-40 bar → 7-10 bar) son consistentes con normativas internacionales y prácticas del mercado.

### 10.2 Recomendaciones

1. **Validar requerimientos reales**: Antes de proceder, validar consumo real, autonomía mínima aceptable y disponibilidad de estaciones GNV.

2. **Evaluar impacto de peso**: Realizar análisis económico considerando reducción de capacidad de carga vs ahorro en combustible.

3. **Considerar tanques tipo 4**: Si el peso es crítico, evaluar tanques tipo 4 (más livianos pero más costosos).

4. **Reducir autonomía si es posible**: Reducir autonomía objetivo puede reducir significativamente costo y peso del sistema.

5. **Planificar migración a GNL**: Si se planea migración futura, considerar diseño modular desde el inicio.

6. **Cumplimiento normativo**: Asegurar que todos los componentes cumplan UNECE R110 y que el taller de instalación esté certificado.

### 10.3 Próximos Pasos

1. **Reunión con cliente**: Presentar este informe y validar supuestos críticos.
2. **Ajuste de diseño**: Ajustar dimensionamiento basado en validaciones del cliente.
3. **Cotización detallada**: Obtener cotizaciones de proveedores con especificaciones finales.
4. **Selección de taller**: Identificar y seleccionar taller certificado para instalación.
5. **Plan de pruebas**: Detallar plan de pruebas específico para vehículos del cliente.

---

## 11. Referencias y Fuentes

### 11.1 Normativas

1. UNECE R110 - Uniform provisions concerning the approval of specific components of motor vehicles using compressed natural gas (CNG)
2. ISO 11439 - Gas cylinders — High pressure cylinders for the on-board storage of natural gas as a fuel for automotive vehicles
3. ISO 15500 - Road vehicles — Compressed natural gas (CNG) fuel systems
4. SAE J1616 - Recommended Practice for Compressed Natural Gas Vehicle Fuel
5. Resolución 957 de 2012 (Colombia) - Reglamento Técnico para talleres, equipos y procesos de conversión a gas natural comprimido
6. Resolución 180540 de 2010 (Colombia) - Reglamento para la conversión de vehículos a gas natural
7. NTC 3949 - Estaciones de regulación de presión de gas combustible
8. RETIE - Reglamento Técnico de Instalaciones Eléctricas

### 11.2 Fuentes Técnicas

1. NIST Chemistry WebBook - Propiedades termodinámicas del metano
2. ASTM D975 - Standard Specification for Diesel Fuel
3. ISO 6976:2016 - Natural gas — Calculation of calorific values, density, relative density and Wobbe index from composition

### 11.3 Datos Asumidos o Estimados

- Consumos de combustible: Estimados basados en vehículos similares (confianza media)
- Autonomías deseadas: Asumidas (confianza baja - requiere validación)
- Precios de componentes: Estimados de mercado (confianza media-baja)
- Eficiencia de conversión: Asumida 95% (confianza media)

---

**Fin del Informe**

---

## Anexo A: Glosario de Términos

- **GNV**: Gas Natural Vehicular (CNG - Compressed Natural Gas)
- **GNL**: Gas Natural Licuado (LNG - Liquefied Natural Gas)
- **LHV**: Lower Heating Value (Poder Calorífico Inferior)
- **ECU**: Engine Control Unit (Unidad de Control del Motor)
- **UNECE**: United Nations Economic Commission for Europe
- **NTC**: Norma Técnica Colombiana
- **RETIE**: Reglamento Técnico de Instalaciones Eléctricas
- **RUNT**: Registro Único Nacional de Tránsito
- **P&ID**: Piping and Instrumentation Diagram (Diagrama de Tuberías e Instrumentación)

---

## Anexo B: Conversiones de Unidades

| Magnitud | SI | Imperial | Conversión |
|----------|----|----------|------------|
| Presión | 1 bar | 14.5 psi | 1 bar = 14.5038 psi |
| Volumen | 1 m³ | 1,000 L | 1 m³ = 1,000 L |
| Masa | 1 kg | 2.20462 lb | 1 kg = 2.20462 lb |
| Energía | 1 MJ | 0.2778 kWh | 1 MJ = 0.2778 kWh |
| Temperatura | K = °C + 273.15 | °F = (°C × 9/5) + 32 | - |

---

**Documento generado el**: 2024-12-19  
**Versión**: 1.0  
**Autor**: Ingeniería de Sistemas GNV  
**Cliente**: PETROLIQUIDOS

