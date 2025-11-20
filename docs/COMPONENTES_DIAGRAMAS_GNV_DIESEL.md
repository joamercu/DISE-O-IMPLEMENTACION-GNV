# 🔧 Componentes Principales y Diagramas de Flujo - Sistema GNV para Vehículos Diésel

## Resumen Ejecutivo

Este documento recopila los componentes principales, diagramas de flujo típicos y elementos adicionales para complementar diagramas de sistemas GNV (Gas Natural Vehicular) en vehículos diésel con sistema dual fuel.

**Fecha de elaboración:** 2025-01-19  
**Proyecto:** Diseño e Implementación GNV  
**Versión:** 1.0

---

## 1. Componentes Principales del Sistema GNV para Vehículos Diésel

### 1.1 Componentes de Almacenamiento

#### 1.1.1 Tanques/Cilindros de Almacenamiento de GNV
- **Función:** Almacenan el gas natural comprimido a alta presión
- **Presión de operación:** 200-250 bar (estándar Colombia: 200 bar)
- **Presión de prueba:** 300 bar
- **Tipos:**
  - Tipo 3: Acero con envoltura composite (peso: 50-80 kg para 80L)
  - Tipo 4: Fully composite (peso: 30-50 kg para 80L, más costoso)
- **Vida útil:** 15-20 años con inspecciones periódicas
- **Certificaciones:** ECE R110, DOT, ISO 11439
- **Ubicación típica:** Chasis del vehículo, optimizando espacio y centro de gravedad

#### 1.1.2 Válvula de Llenado (Receptáculo)
- **Función:** Permite el llenado seguro del tanque desde estación de servicio GNV
- **Características:**
  - Sistemas de seguridad para prevenir llenado excesivo
  - Prevención de fugas durante el proceso
  - Conexión tipo NGV1 o NGV2 (estándar internacional)
- **Ubicación:** Accesible desde el exterior del vehículo

#### 1.1.3 Válvula del Cilindro con Sistema de Venteo
- **Función:** Controla el flujo de gas desde el cilindro
- **Características:**
  - Sistema de alivio de presión (PRV - Pressure Relief Valve)
  - Control de exceso de flujo (EFC - Excess Flow Check)
  - Venteo de emergencia en caso de sobrepresión
- **Presión de alivio:** Típicamente 250 bar para tanques de 200 bar

#### 1.1.4 Manifold de Distribución
- **Función:** Conecta múltiples tanques en paralelo
- **Características:**
  - Permite carga y descarga uniforme de todos los tanques
  - Balanceo de presión entre tanques
  - Punto central de conexión para válvulas de seguridad

### 1.2 Componentes de Regulación y Control de Presión

#### 1.2.1 Electroválvula de Alta Presión (Shut-off Valve)
- **Función:** Controla el paso del gas desde los tanques hacia el regulador
- **Características:**
  - Actuación eléctrica controlada por ECU
  - Cierre automático en emergencias
  - Cierre cuando el motor está apagado
  - Actúa como mecanismo de seguridad principal
- **Presión de trabajo:** 200-250 bar

#### 1.2.2 Regulador de Presión - Primera Etapa
- **Función:** Reduce la alta presión del gas almacenado (200-250 bar) a presión intermedia
- **Presión de entrada:** 200-250 bar
- **Presión de salida:** 20-40 bar (típico)
- **Características:**
  - Incluye calentador para prevenir congelamiento (efecto Joule-Thomson)
  - Regulación automática
  - Compensación de temperatura

#### 1.2.3 Regulador de Presión - Segunda Etapa
- **Función:** Reduce la presión intermedia a presión de inyección
- **Presión de entrada:** 20-40 bar
- **Presión de salida:** 1-3 bar (típico para inyección en colector) o 7-10 bar (según sistema)
- **Características:**
  - Regulación precisa para inyección
  - Respuesta rápida a cambios de carga del motor

### 1.3 Componentes de Filtración

#### 1.3.1 Filtro de Gas - Alta Presión
- **Función:** Elimina impurezas del gas antes del primer regulador
- **Ubicación:** Entre válvula shut-off y regulador primera etapa
- **Características:**
  - Filtrado de partículas sólidas
  - Protección de componentes aguas abajo
  - Elemento filtrante reemplazable

#### 1.3.2 Filtro de Gas - Baja Presión
- **Función:** Filtrado final antes de inyección
- **Ubicación:** Después del regulador segunda etapa
- **Características:**
  - Filtrado fino
  - Protección de inyectores

### 1.4 Componentes de Inyección

#### 1.4.1 Inyectores de Gas
- **Función:** Dosifican la cantidad precisa de gas natural en el colector de admisión
- **Tipos:**
  - Inyección secuencial: Inyección por fases, sincronizada con cada cilindro
  - Inyección continua: Flujo constante regulado
- **Control:** Operan bajo gestión de la ECU
- **Presión de trabajo:** 1-3 bar o 7-10 bar según sistema
- **Cantidad:** Típicamente uno por cilindro del motor

#### 1.4.2 Mezclador (Opcional)
- **Función:** Combina el GNV con el aire de admisión antes de entrar a la cámara de combustión
- **Aplicación:** Sistemas más antiguos o específicos
- **Ubicación:** Entre inyectores y múltiple de admisión

### 1.5 Componentes de Control Electrónico

#### 1.5.1 Unidad de Control Electrónica (ECU)
- **Función:** Gestiona el funcionamiento completo del sistema GNV
- **Responsabilidades:**
  - Regulación de presión mediante control de válvulas
  - Dosificación del gas según carga del motor
  - Sincronización con inyección de diésel
  - Conmutación entre diésel y GNV
  - Gestión de seguridad y emergencias
  - Optimización de rendimiento y emisiones
- **Comunicación:**
  - CAN Bus con ECU del motor
  - Integración con sistemas del vehículo
- **Entradas:**
  - Sensores de presión (alta y baja)
  - Sensores de temperatura
  - Sensor lambda (O₂)
  - Señales del motor (RPM, carga, posición cigüeñal)
- **Salidas:**
  - Control de electroválvulas
  - Control de inyectores de gas
  - Señales de ajuste a ECU motor (si aplica)

#### 1.5.2 Emuladores y Variadores de Avance
- **Función:** Ajustan señales electrónicas y tiempos de encendido
- **Aplicación:** Optimización del rendimiento del motor con GNV
- **Tipos:**
  - Emulador de sensores
  - Variador de avance de inyección
  - Ajuste de mapa de combustible

### 1.6 Sensores del Sistema

#### 1.6.1 Sensor de Presión - Alta Presión
- **Función:** Monitorea presión en tanques y línea de alta presión
- **Rango:** 0-300 bar
- **Ubicación:** Después de manifold, antes de regulador primera etapa
- **Señal:** Enviada a ECU

#### 1.6.2 Sensor de Presión - Baja Presión
- **Función:** Monitorea presión después de reguladores
- **Rango:** 0-10 bar
- **Ubicación:** Después de regulador segunda etapa
- **Señal:** Enviada a ECU para control de inyección

#### 1.6.3 Sensor de Temperatura - Alta Presión
- **Función:** Monitorea temperatura del gas en línea de alta presión
- **Rango:** -40°C a +125°C
- **Ubicación:** Cerca de regulador primera etapa
- **Uso:** Compensación de densidad y prevención de congelamiento

#### 1.6.4 Sensor de Temperatura - Baja Presión
- **Función:** Monitorea temperatura del gas antes de inyección
- **Rango:** -40°C a +125°C
- **Ubicación:** Después de regulador segunda etapa
- **Uso:** Ajuste de dosificación

#### 1.6.5 Sensor Lambda (O₂)
- **Función:** Mide concentración de oxígeno en gases de escape
- **Ubicación:** Tubo de escape, antes del catalizador
- **Uso:** Control de mezcla aire-combustible (relación lambda)
- **Objetivo:** Lambda ≈ 1.0 para combustión óptima

#### 1.6.6 Sensor de Flujo de Gas
- **Función:** Mide flujo másico o volumétrico de gas
- **Ubicación:** Línea de baja presión
- **Uso:** Medición de consumo y control de dosificación

#### 1.6.7 Sensor de Posición del Cigüeñal
- **Función:** Monitorea posición y velocidad del cigüeñal
- **Uso:** Sincronización de inyección de gas con ciclo del motor
- **Integración:** Con ECU del motor

### 1.7 Componentes de Seguridad

#### 1.7.1 Válvulas de Alivio de Presión (PRV)
- **Función:** Liberan gas en caso de sobrepresión
- **Presión de activación:** Típicamente 250 bar para tanques de 200 bar
- **Ubicación:** Cada tanque individual
- **Tipo:** Mecánica, activación por presión

#### 1.7.2 Válvula de Exceso de Flujo (EFC)
- **Función:** Cierra automáticamente en caso de flujo excesivo (fuga)
- **Ubicación:** En válvula del cilindro o línea principal
- **Tipo:** Mecánica, activación por velocidad de flujo

#### 1.7.3 Sistema de Detección de Fugas
- **Función:** Detecta fugas de gas en el sistema
- **Componentes:**
  - Sensores de gas en compartimentos cerrados
  - Alarmas visuales y sonoras
  - Cierre automático de válvulas

#### 1.7.4 Válvula de Cierre Rápido
- **Función:** Cierre manual de emergencia
- **Ubicación:** Accesible desde el exterior del vehículo
- **Tipo:** Manual o eléctrica con activación remota

### 1.8 Componentes de Interfaz y Control

#### 1.8.1 Conmutador/Selector de Combustible
- **Función:** Permite al conductor seleccionar entre diésel, GNV o modo dual
- **Tipos:**
  - Manual: Interruptor en cabina
  - Automático: Controlado por ECU según condiciones
- **Indicadores:** Luces LED o pantalla mostrando modo activo

#### 1.8.2 Indicador de Presión
- **Función:** Muestra presión del gas en el sistema
- **Ubicación:** Tablero del vehículo
- **Tipo:** Analógico o digital
- **Información:** Presión actual y nivel de llenado

#### 1.8.3 Indicador de Nivel de Combustible
- **Función:** Muestra cantidad de GNV disponible
- **Cálculo:** Basado en presión y temperatura (densidad)
- **Unidades:** m³, kg, o porcentaje

### 1.9 Componentes del Motor Diésel (Adaptaciones)

#### 1.9.1 Sistema de Inyección de Diésel
- **Función:** Suministra diésel para ignición del GNV
- **Modo Dual Fuel:**
  - Diésel: 10-30% (pilot injection para ignición)
  - GNV: 70-90% (combustible principal)
- **Control:** ECU gestiona proporción según carga del motor

#### 1.9.2 Múltiple de Admisión
- **Función:** Distribuye mezcla aire-GNV a cada cilindro
- **Adaptación:** Puntos de inyección de gas integrados

#### 1.9.3 Sistema de Refrigeración
- **Importancia:** Mantiene temperatura del motor adecuada
- **Consideración:** GNV tiene temperatura de ignición mayor que diésel
- **Requisito:** Sistema en óptimas condiciones

---

## 2. Diagrama de Flujo Típico del Sistema GNV en Vehículos Diésel

### 2.1 Flujo Principal de Gas

```
[Estación de Servicio GNV]
         ↓
[Válvula de Llenado]
         ↓
[Tanques/Cilindros de Almacenamiento] (200-250 bar)
         ↓
[Válvulas de Alivio PRV] (250 bar)
         ↓
[Manifold de Distribución]
         ↓
[Electroválvula Shut-off] (Controlada por ECU)
         ↓
[Regulador Primera Etapa] (200-250 bar → 20-40 bar)
         ↓
[Calentador] (Prevención congelamiento)
         ↓
[Filtro de Gas - Alta Presión]
         ↓
[Regulador Segunda Etapa] (20-40 bar → 1-3 bar o 7-10 bar)
         ↓
[Filtro de Gas - Baja Presión]
         ↓
[Inyectores de Gas] (Controlados por ECU)
         ↓
[Múltiple de Admisión]
         ↓
[Cámara de Combustión] (Mezcla con aire + diésel piloto)
         ↓
[Motor Diésel]
```

### 2.2 Flujo de Señales de Control

```
[Sensores] → [ECU] → [Actuadores]
     ↓           ↓          ↓
  - Presión   - Control  - Electroválvulas
  - Temperatura - Dosificación - Inyectores
  - Lambda    - Sincronización - Reguladores
  - Flujo     - Seguridad
  - RPM       - Optimización
  - Carga
```

### 2.3 Flujo de Seguridad

```
[Detección de Anomalía]
         ↓
[Alarma/Indicador]
         ↓
[Cierre Automático de Válvulas]
         ↓
[Venteo Seguro (si aplica)]
         ↓
[Modo Seguro del Motor]
```

---

## 3. Elementos Adicionales para Complementar el Diagrama

### 3.1 Componentes de Tuberías y Conexiones

#### 3.1.1 Tuberías de Alta Presión
- **Material:** Acero inoxidable o cobre
- **Presión de trabajo:** 200-250 bar
- **Diámetro:** Según flujo requerido
- **Ubicación:** Entre tanques y regulador primera etapa
- **Características:** Rígidas, con conexiones tipo flare o soldadas

#### 3.1.2 Tuberías de Baja Presión
- **Material:** Acero, cobre o materiales flexibles certificados
- **Presión de trabajo:** 1-10 bar
- **Diámetro:** Según flujo requerido
- **Ubicación:** Después de regulador segunda etapa hasta inyectores
- **Características:** Pueden ser flexibles para facilitar instalación

#### 3.1.3 Conexiones y Acoplamientos
- **Tipo:** Roscas NGT, DIN, o según especificación
- **Material:** Acero inoxidable o latón
- **Características:** Herméticas, resistentes a vibraciones

### 3.2 Componentes de Soportes y Estructura

#### 3.2.1 Soportes para Tanques
- **Función:** Fijación segura de tanques al chasis
- **Material:** Acero estructural
- **Características:** Resistencia a vibraciones y cargas dinámicas
- **Diseño:** Según normativa y especificaciones del fabricante

#### 3.2.2 Protección de Tanques
- **Función:** Protección física contra impactos
- **Material:** Acero o composite
- **Ubicación:** Alrededor de tanques

### 3.3 Componentes de Ventilación

#### 3.3.1 Sistema de Ventilación
- **Función:** Evacuar gas en caso de fuga
- **Ubicación:** Compartimentos donde están los tanques
- **Características:** Ventilación natural o forzada según diseño

### 3.4 Componentes de Diagnóstico

#### 3.4.1 Puerto de Diagnóstico
- **Función:** Conexión para diagnóstico y calibración
- **Tipo:** OBD-II o específico del sistema
- **Uso:** Lectura de códigos, parámetros, calibración

#### 3.4.2 Registro de Datos
- **Función:** Almacenamiento de datos de operación
- **Uso:** Análisis de rendimiento, mantenimiento predictivo

---

## 4. Comparación con Diagrama Actual

### 4.1 Componentes ya Incluidos en tu Diagrama

✅ **Componentes Presentes:**
- Tanques CNG (Tipo 3, 80L, 200 bar)
- Válvulas de alivio PRV (250 bar)
- Manifold de distribución
- Válvula shut-off automática
- Regulador primera etapa (200-250 bar → 20-40 bar) con calentador
- Filtro de gas alta presión
- Regulador segunda etapa (20-40 bar → 7-10 bar)
- ECU (Engine Control Unit)
- Sensores (P, T, Lambda)
- Inyectores de gas secuenciales
- Motor diésel convertido
- Válvula de llenado (receptáculo)

### 4.2 Componentes Adicionales Recomendados

#### 4.2.1 Componentes de Seguridad Adicionales
- ⚠️ **Válvula de Exceso de Flujo (EFC):** En válvula del cilindro o línea principal
- ⚠️ **Sistema de Detección de Fugas:** Sensores de gas en compartimentos
- ⚠️ **Válvula de Cierre Rápido Manual:** Accesible desde exterior

#### 4.2.2 Componentes de Control
- ⚠️ **Conmutador/Selector de Combustible:** Interfaz para conductor
- ⚠️ **Indicadores en Tablero:** Presión, nivel, modo de operación
- ⚠️ **Sensor de Flujo de Gas:** Para medición de consumo

#### 4.2.3 Componentes de Tuberías
- ⚠️ **Especificación de Tuberías:** Material, diámetro, tipo de conexión
- ⚠️ **Puntos de Venteo:** Para seguridad en caso de emergencia

#### 4.2.4 Componentes de Diagnóstico
- ⚠️ **Puerto de Diagnóstico:** OBD-II o específico
- ⚠️ **Sistema de Registro de Datos:** Para análisis

### 4.3 Mejoras Sugeridas al Diagrama

1. **Agregar Válvula EFC:** En cada tanque o en línea principal
2. **Especificar Tipo de Tuberías:** Con leyenda de materiales y presiones
3. **Agregar Sistema de Ventilación:** En compartimento de tanques
4. **Incluir Interfaz de Usuario:** Conmutador e indicadores
5. **Detallar Sistema de Llenado:** Conexión desde estación de servicio
6. **Agregar Componentes de Diagnóstico:** Puerto OBD y registro de datos
7. **Especificar Sensores Adicionales:** Sensor de flujo, sensores de fuga
8. **Incluir Soportes y Estructura:** Para tanques y componentes

---

## 5. Diagrama de Flujo Simplificado para Referencia

### 5.1 Flujo de Gas (Simplificado)

```
ESTACIÓN DE SERVICIO
        ↓
VÁLVULA DE LLENADO
        ↓
TANQUES CNG (200 bar)
        ↓
MANIFOLD
        ↓
VÁLVULA SHUT-OFF
        ↓
REGULADOR 1RA ETAPA (→ 20-40 bar)
        ↓
FILTRO
        ↓
REGULADOR 2DA ETAPA (→ 7-10 bar)
        ↓
INYECTORES
        ↓
MÚLTIPLE DE ADMISIÓN
        ↓
MOTOR DIESEL
```

### 5.2 Flujo de Control (Simplificado)

```
SENSORES → ECU → ACTUADORES
   ↓         ↓        ↓
P, T, λ   Control  Válvulas,
RPM,      Dosif.   Inyectores
Carga     Segur.   Reguladores
```

---

## 6. Referencias y Fuentes

1. **Manual de Instalación de Equipos a GNV (Bolivia):**
   - EEC-GNV: Manual técnico de instalación
   - URL: https://www.eecgnv.gob.bo

2. **Sistema de Gas Natural Vehicular (Anair):**
   - Componentes y funcionamiento
   - URL: https://anair.es/articulos/sistema-de-gas-natural-vehicular.html

3. **American Power Group (APG):**
   - Sistemas dual fuel diesel-GNV
   - Diagramas técnicos
   - URL: https://gascomb.com/apg_diagrama_v5000.html

4. **Normativas:**
   - UNECE R110: Componentes de GNV
   - ISO 11439: Tanques CNG
   - DOT: Regulaciones Estados Unidos

---

## 7. Notas Técnicas

### 7.1 Presiones Típicas del Sistema

| Punto del Sistema | Presión (bar) | Observaciones |
|-------------------|---------------|---------------|
| Tanques (llenado) | 200-250 | Estándar Colombia: 200 bar |
| Línea alta presión | 200-250 | Después de manifold |
| Regulador 1ra etapa salida | 20-40 | Presión intermedia |
| Regulador 2da etapa salida | 1-3 o 7-10 | Según sistema de inyección |
| Inyección al motor | 1-3 o 7-10 | Presión de trabajo inyectores |

### 7.2 Temperaturas Típicas

| Componente | Temperatura | Observaciones |
|------------|-------------|---------------|
| Gas en tanques | Ambiente | -40°C a +60°C operación |
| Después de regulador 1ra | Puede bajar | Efecto Joule-Thomson |
| Calentador | +20°C a +40°C | Prevención congelamiento |
| Motor | 80-100°C | Temperatura de operación |

### 7.3 Flujos Típicos

| Aplicación | Flujo (Nm³/h) | Observaciones |
|------------|---------------|---------------|
| Vehículo ligero | 10-30 | Consumo típico |
| Vehículo pesado | 30-100 | Consumo típico |
| Llenado tanque | 50-200 | Depende de estación |

---

## 8. Conclusiones

Este documento proporciona una guía completa de componentes principales, diagramas de flujo y elementos adicionales para sistemas GNV en vehículos diésel.

**Puntos clave:**
1. El diagrama actual incluye los componentes principales del sistema
2. Se recomiendan componentes adicionales de seguridad y control
3. Los diagramas de flujo ayudan a visualizar el funcionamiento completo
4. Es esencial especificar materiales, presiones y conexiones en el diagrama
5. Los componentes de diagnóstico facilitan el mantenimiento

**Recomendaciones:**
- Agregar componentes de seguridad adicionales (EFC, detección de fugas)
- Incluir interfaz de usuario (conmutador, indicadores)
- Especificar detalles de tuberías y conexiones
- Agregar sistema de diagnóstico
- Documentar sistema de ventilación

---

*Documento creado: 2025-01-19*  
*Última actualización: 2025-01-19*  
*Fuente: Búsqueda web de componentes y diagramas de sistemas GNV*

