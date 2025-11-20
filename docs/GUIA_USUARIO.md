# 👤 Guía de Usuario - Aplicación GNV

## Tabla de Contenidos

1. [Inicio de Sesión](#inicio-de-sesión)
2. [Interfaz Principal](#interfaz-principal)
3. [Pestañas de la Aplicación](#pestañas-de-la-aplicación)
4. [Guía Paso a Paso](#guía-paso-a-paso)
5. [Funciones por Rol](#funciones-por-rol)

## Inicio de Sesión

### Primera Vez

1. Ejecute `scripts/iniciar_app.bat` o `streamlit run src/calculos_combustible_vehicular.py`
2. La aplicación se abrirá en su navegador
3. Ingrese las credenciales:

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`
- Rol: Administrador

**Cliente:**
- Usuario: `cliente`
- Contraseña: `cliente123`
- Rol: Cliente

### Recordar Usuario

- Marque la casilla "💾 Recordar usuario" para guardar su nombre de usuario
- La contraseña **NO** se guarda por seguridad
- Puede eliminar el usuario guardado con "🗑️ Olvidar usuario guardado"

## Interfaz Principal

### Barra Lateral (Sidebar)

**Información del Proyecto:**
- CLIENTE: PETROLIQUIDOS
DESARROLLO: WELDTECH SOLUTION
VERSION: PROPUESTA TECNICA
REVISION: 0 (PROPUESTA PREELIMINAR)
DESARROLLO: WELDTECH SOLUTION
VERSION: PROPUESTA TECNICA
REVISION: 0 (PROPUESTA PREELIMINAR)
- Versión: 1.0
- Fecha: 2024-12-19

**Editar Información del Proyecto** (Solo Administradores):
- Permite modificar Cliente, Versión y Fecha
- Los cambios se reflejan en todos los informes

**Cerrar Sesión:**
- Botón para cerrar sesión y volver al login

## Pestañas de la Aplicación

### 1. 🔢 Cálculos Principales

**Propósito:** Calcular los parámetros del sistema GNV/CNG

**Pasos:**

1. **Ingrese Parámetros de Operación:**
   - Consumo de Diésel (L/100 km): Valor por defecto 35.0
   - Autonomía Deseada (km): Valor por defecto 800.0

2. **Configure Parámetros Técnicos:**
   - Poder Calorífico Diésel (MJ/L): 35.8 (ASTM D975)
   - LHV CH₄ (MJ/kg): 50.0 (ISO 6976:2016)
   - Eficiencia de Conversión: 0.95

3. **Ajuste Parámetros de Almacenamiento:**
   - Presión de Llenado (bar): 200.0
   - Temperatura de Operación (°C): 25.0
   - Factor de Compresibilidad Z: 0.85
   - Volumen Unitario Tanque (m³): 0.080
   - Pesos: Tanque (65 kg), Soportes (10 kg), Accesorios (5 kg)

4. **Constantes Físicas** (Expandible):
   - Constante Universal de Gases R: 8.314 J/(mol·K)
   - Masa Molar CH₄: 0.01604 kg/mol

5. **Calcular:**
   - Haga clic en "🚀 Calcular Sistema GNV"
   - Los resultados se mostrarán inmediatamente

**Resultados Mostrados:**
- Proceso de cálculo paso a paso
- Tabla resumen de resultados
- Alertas y recomendaciones
- **Diagrama P&ID del Sistema GNV** (Expandible) - Nuevo

**Generador de Diagrama P&ID:**
1. Después de realizar un cálculo, expanda la sección "📊 Diagrama P&ID del Sistema GNV"
2. Haga clic en "🔄 Generar Diagrama Actualizado"
3. El diagrama se generará automáticamente con las variables calculadas
4. Use "📋 Ver Variables" para ver los parámetros del diagrama
5. Use "📥 Descargar Diagrama" para obtener el archivo .drawio.xml
6. Abra el archivo en [draw.io](https://app.diagrams.net) para visualizar o editar

**Componentes del Diagrama:**
- Tanques CNG con número y capacidad calculados
- Sistema de regulación (2 etapas) con rangos de presión
- Válvulas de seguridad y control
- Sensores (presión, temperatura, lambda)
- ECU y sistema de inyección
- Motor convertido
- Leyenda y notas técnicas
- Variables del proyecto calculadas

### 2. 👤 Datos del Cliente

**Propósito:** Capturar información del cliente y supuestos

**Campos:**

1. **Información del Cliente:**
   - Nombre del Cliente
   - Capacidad de la Flota
   - Rol (solo lectura)

2. **Supuestos Operativos:**
   - Consumo de combustible actual
   - Perfil de operación (km/día, % carretera vs urbano)
   - Autonomía requerida
   - Rutas principales
   - *Use el expandible ℹ️ para ver ejemplos*

3. **Supuestos de Componentes:**
   - Tipo de tanques preferido
   - Presión de trabajo
   - Restricciones de espacio y peso
   - Preferencias técnicas
   - *Use el expandible ℹ️ para ver ejemplos*

4. **Guardar:**
   - Haga clic en "💾 Guardar Datos del Cliente"
   - Se registrará fecha y usuario

**Funciones Adicionales (Solo Administradores):**
- Exportar datos a JSON
- Ver información de auditoría completa

### 3. 📐 Fórmulas y Procedimientos

**Acceso:** Solo Administradores

**Contenido:**
- Fórmulas matemáticas completas
- Procedimientos numéricos paso a paso
- Ejemplo de cálculo completo
- Referencias técnicas

**Clientes:** Verán mensaje de acceso restringido

### 4. 📊 Análisis de Sensibilidad

**Propósito:** Evaluar variaciones en los parámetros

**Pasos:**

1. **Configure Parámetros Base:**
   - Consumo Base (L/100 km)
   - Autonomía Base (km)
   - Variación a Analizar (%)

2. **Calcular:**
   - Haga clic en "🔄 Calcular Análisis de Sensibilidad"

3. **Resultados:**
   - Tabla de variación de consumo
   - Tabla de variación de autonomía
   - Gráficos interactivos

**Interpretación:**
- Vea cómo cambian los resultados con diferentes valores
- Identifique parámetros críticos
- Optimice el diseño del sistema

### 5. 📋 Manifest del Proyecto

**Contenido:**
- Información del proyecto
- Entregables (descargables para administradores)
- Parámetros técnicos
- Regulaciones y cumplimiento
- Riesgos identificados
- Decisiones pendientes (con formularios interactivos)
- Estimaciones de costo
- Próximos pasos

**Funciones Especiales:**

**Formularios de Decisiones Pendientes:**
- Cada decisión de alta prioridad tiene su propio formulario
- Complete los campos según el tipo de pregunta
- Guarde las respuestas

**Exportación (Solo Administradores):**
- Descargar Manifest JSON
- Descargar Manifest HTML
- Descargar entregables individuales

### 6. ℹ️ Información Técnica

**Contenido:**
- Informe de resultados de cálculo (si se ha calculado)
- Descarga de informe HTML
- Referencia técnica de la plataforma
- Normativas y certificaciones
- Limitaciones y exclusiones
- Recomendaciones
- Contacto y soporte

## Guía Paso a Paso

### Ejemplo: Calcular Sistema GNV

1. **Inicie sesión** como Administrador o Cliente
2. Vaya a la pestaña **🔢 Cálculos Principales**
3. Ajuste los parámetros según su caso:
   - Consumo: 35 L/100 km
   - Autonomía: 600 km
   - Presión: 200 bar
4. Haga clic en **"🚀 Calcular Sistema GNV"**
5. Revise los resultados y alertas
6. Vaya a **ℹ️ Información Técnica** para descargar el informe HTML

### Ejemplo: Completar Datos del Cliente

1. Vaya a la pestaña **👤 Datos del Cliente**
2. Complete el formulario:
   - Nombre del cliente
   - Capacidad de la flota
   - Supuestos operativos (use los ejemplos como guía)
   - Supuestos de componentes
3. Haga clic en **"💾 Guardar Datos del Cliente"**
4. Si es administrador, puede exportar a JSON

### Ejemplo: Responder Decisiones Pendientes

1. Vaya a la pestaña **📋 Manifest del Proyecto**
2. Desplácese a **"❓ Decisiones Pendientes"**
3. Abra cada formulario de decisión de alta prioridad
4. Complete los campos según el tipo de pregunta
5. Guarde cada respuesta

## Funciones por Rol

### 👨‍💼 Administrador

**Acceso Completo:**
- ✅ Editar información del proyecto
- ✅ Ver fórmulas y procedimientos
- ✅ Exportar datos del cliente a JSON
- ✅ Descargar entregables
- ✅ Exportar manifest completo (JSON y HTML)
- ✅ Ver todas las respuestas de decisiones pendientes

### 👤 Cliente

**Acceso Limitado:**
- ✅ Realizar cálculos
- ✅ Ver resultados
- ✅ Completar datos del cliente
- ✅ Ver análisis de sensibilidad
- ✅ Ver manifest del proyecto
- ✅ Responder decisiones pendientes
- ❌ NO puede ver fórmulas y procedimientos
- ❌ NO puede exportar datos
- ❌ NO puede descargar entregables

## Consejos y Mejores Prácticas

1. **Guarde frecuentemente:** Los datos del cliente se guardan en sesión
2. **Use los ejemplos:** Los expandibles ℹ️ contienen ejemplos útiles
3. **Revise las alertas:** Las alertas indican valores problemáticos
4. **Exporte informes:** Use la descarga HTML para documentar resultados
5. **Complete decisiones:** Las respuestas ayudan a definir el alcance del proyecto

## Solución de Problemas

### La aplicación no inicia
- Verifique que Python esté instalado
- Ejecute `instalar_dependencias.bat`
- Verifique que esté en el directorio correcto

### No puedo ver ciertas funciones
- Verifique su rol de usuario
- Algunas funciones son solo para administradores

### Los cálculos no se muestran
- Asegúrese de hacer clic en "Calcular Sistema GNV"
- Verifique que los parámetros sean válidos (> 0)

### No puedo descargar archivos
- Verifique que los archivos existan en las rutas esperadas
- Solo administradores pueden descargar entregables

---

*Guía actualizada: 2024-12-19*

