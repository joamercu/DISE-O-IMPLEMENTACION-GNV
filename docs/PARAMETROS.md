# ⚙️ Documentación de Parámetros - Aplicación GNV

## Parámetros por Defecto

Todos los parámetros están definidos en `src/config.py` y pueden ser modificados desde la interfaz de usuario.

## Parámetros de Operación

### Consumo de Diésel
- **Valor por defecto:** 35.0 L/100 km
- **Rango:** 1.0 - 200.0 L/100 km
- **Descripción:** Consumo de combustible diésel del vehículo
- **Fuente:** Datos del vehículo o estimaciones

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

### Eficiencia de Conversión GNV vs Diésel
- **Valor por defecto:** 0.95
- **Rango:** 0.80 - 1.0
- **Descripción:** Factor de eficiencia del sistema GNV comparado con diésel
- **Consideraciones:** 
  - 0.90-0.95: Típico para sistemas bi-fuel
  - 0.95-1.0: Sistemas dedicados optimizados

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

### 1. Volumen Diésel Equivalente
```
V_diesel = (Consumo × Autonomía) / 100
```

### 2. Energía Requerida
```
E = V_diesel × E_diesel
```

### 3. Masa de CH₄ Requerida
```
m_CH4 = (E / LHV_CH4) / η
```
Donde η = eficiencia de conversión

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

## Consideraciones Importantes

1. **Validación:** Todos los valores deben validarse con datos reales del vehículo
2. **Composición del Gas:** El GNV contiene ~90-95% CH₄, no 100%
3. **Factor Z:** Puede variar según la composición del gas natural
4. **Peso:** El peso adicional afecta la capacidad de carga
5. **Espacio:** Verificar disponibilidad de espacio en el chasis
6. **Estaciones:** Validar disponibilidad de estaciones GNV en rutas

## Modificar Parámetros por Defecto

Para cambiar los valores por defecto globalmente, edite `src/config.py`:

```python
# Parámetros por defecto de cálculo
DEFAULT_CONSUMO_DIESEL = 35.0
DEFAULT_AUTONOMIA = 800.0
# ... etc
```

Los cambios se reflejarán en toda la aplicación.

---

*Documentación actualizada: 2024-12-19*

