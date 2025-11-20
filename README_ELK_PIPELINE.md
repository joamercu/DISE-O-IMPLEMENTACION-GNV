# Pipeline Completo con Integración ELK

## 📋 Descripción

Pipeline Python completo que:
1. ✅ **Parsea** el XML draw.io
2. ✅ **Identifica** nodos, puertos y edges
3. ✅ **Invoca ELK** (Eclipse Layout Kernel) a través de elkjs/Node.js
4. ✅ **Escribe** de vuelta posiciones y waypoints en el XML
5. ✅ **Emite reporte** de cambios y aristas que requieren revisión manual

## 🚀 Instalación

### Requisitos

1. **Python 3.7+**
2. **Node.js** (opcional, para usar ELK real)
3. **elkjs** (opcional, para usar ELK real)

### Instalar elkjs (opcional)

Si quieres usar ELK real en lugar del algoritmo interno:

```bash
# Instalar Node.js si no lo tienes
# Descargar de: https://nodejs.org/

# Instalar elkjs
npm install elkjs
```

Si no instalas elkjs, el pipeline usará automáticamente el algoritmo interno.

## 📖 Uso

### Uso básico

```bash
python pipeline_elk_completo.py [archivo.drawio.xml]
```

### Opciones

```bash
# Especificar archivo de salida
python pipeline_elk_completo.py --output diagrama_optimizado.drawio.xml

# Especificar archivo de reporte
python pipeline_elk_completo.py --report cambios.txt

# Usar algoritmo interno (no requiere Node.js/elkjs)
python pipeline_elk_completo.py --use-internal

# Solo validar sin aplicar layout
python pipeline_elk_completo.py --validate-only
```

## 📁 Archivos del Pipeline

### Módulos principales

1. **`elk_layout_pipeline.py`**
   - `DrawIOGraphExtractor`: Parsea XML y extrae grafo
   - Clases: `Graph`, `Node`, `Edge`, `Port`, `EdgePriority`

2. **`elk_integration.py`**
   - `ELKIntegration`: Integración con ELK real
   - Convierte grafo a formato ELK JSON
   - Invoca elkjs a través de Node.js
   - Extrae resultados del layout

3. **`elk_layout_engine.py`**
   - `OrthogonalLayoutEngine`: Algoritmo interno (fallback)
   - Se usa si ELK no está disponible

4. **`xml_applicator.py`**
   - `XMLApplicator`: Escribe resultados al XML
   - Actualiza geometrías de nodos
   - Actualiza waypoints de edges

5. **`change_reporter.py`**
   - `ChangeReporter`: Genera reportes de cambios
   - Identifica aristas problemáticas
   - Analiza desplazamientos de nodos

6. **`validator.py`**
   - `DiagramValidator`: Validación automática
   - Verifica estructura, conexiones, geometrías

7. **`pipeline_elk_completo.py`**
   - Orquestador principal
   - Interfaz de línea de comandos

### Archivos de soporte

- **`elk_layout.js`**: Script Node.js para invocar elkjs
- **`package.json`**: Configuración npm para elkjs

## 🔧 Funcionamiento Detallado

### Paso 1: Parsear XML y Extraer Grafo

```python
extractor = DrawIOGraphExtractor(input_file)
graph = extractor.extract()
```

- Lee el XML draw.io
- Identifica todos los nodos (vértices)
- Identifica todos los edges (conexiones)
- Infiere puertos basados en geometrías
- Clasifica tipos de componentes

### Paso 2: Validación Inicial

```python
validator = DiagramValidator(input_file)
is_valid, errors, warnings = validator.validate_all()
```

- Verifica estructura XML
- Valida geometrías
- Verifica conexiones
- Detecta solapamientos

### Paso 3: Calcular Layout

#### Con ELK (si está disponible):

```python
elk_integration = ELKIntegration(graph)
elk_graph = elk_integration.convert_to_elk_graph()  # Convierte a formato ELK
elk_result = elk_integration.call_elk(elk_graph)     # Invoca elkjs
layout_results = elk_integration.extract_layout_from_elk(elk_result)
```

#### Con algoritmo interno (fallback):

```python
layout_engine = OrthogonalLayoutEngine(graph)
layout_results = layout_engine.calculate_layout()
```

### Paso 4: Aplicar al XML

```python
applicator = XMLApplicator(input_file)
applicator.apply_layout(layout_results)
applicator.save(output_file)
```

- Actualiza `mxGeometry` de nodos
- Actualiza `Array` de waypoints en edges

### Paso 5: Generar Reporte

```python
reporter = ChangeReporter(original_graph, layout_results)
report_text = reporter.generate_report(report_file)
```

- Analiza cambios de posición
- Analiza cambios en waypoints
- Identifica aristas problemáticas
- Genera reporte en texto

### Paso 6: Validación Final

- Verifica integridad del resultado
- Reporta errores y advertencias

## 📊 Formato del Reporte

El reporte incluye:

### Resumen
- Nodos movidos significativamente
- Cambios en waypoints
- Aristas que requieren revisión
- Problemas críticos

### Cambios en Posiciones de Nodos
- Top 10 nodos con mayor desplazamiento
- Distancia de movimiento
- Si el nodo estaba marcado como fijo

### Cambios en Waypoints
- Cambios en cantidad de waypoints
- Desplazamientos de waypoints

### Aristas que Requieren Revisión Manual
- Aristas sin waypoints
- Aristas con demasiados waypoints
- Aristas que cruzan muchos otros edges
- Pipes principales sin waypoints claros
- Nodos muy distantes

## 🔍 Ejemplo de Salida

```
================================================================================
PIPELINE COMPLETO CON INTEGRACIÓN ELK
================================================================================
📁 Archivo de entrada: diagrama.drawio.xml
📁 Archivo de salida: diagrama_ELK.drawio.xml
📄 Archivo de reporte: diagrama_REPORT.txt

✅ ELK disponible

PASO 1: PARSEAR XML Y EXTRAER GRAFO
--------------------------------------------------------------------------------
📊 Extrayendo grafo del diagrama...
   ✅ Nodos extraídos: 42
   ✅ Edges extraídos: 28
   ✅ Puertos inferidos: 56

PASO 2: VALIDACIÓN INICIAL
--------------------------------------------------------------------------------
🔍 Validando diagrama...
   ✅ Validación completada

PASO 3: CÁLCULO DE LAYOUT
--------------------------------------------------------------------------------
   🔧 Invocando ELK...
   ✅ Layout calculado por ELK
   ✅ Nodos procesados: 42
   ✅ Edges procesados: 28

PASO 4: APLICAR RESULTADOS AL XML
--------------------------------------------------------------------------------
📝 Aplicando layout al XML...
   ✅ 42 nodos actualizados
   ✅ 28 edges actualizados

PASO 5: GENERAR REPORTE DE CAMBIOS
--------------------------------------------------------------------------------
📊 Analizando cambios...
📄 Reporte guardado en: diagrama_REPORT.txt

PASO 6: VALIDACIÓN FINAL
--------------------------------------------------------------------------------
🔍 Validando diagrama...
   ✅ Validación completada

================================================================================
RESUMEN FINAL
================================================================================
✅ Grafo extraído: 42 nodos, 28 edges
✅ Layout calculado: 42 nodos
✅ Waypoints calculados: 28 edges
✅ Archivo generado: diagrama_ELK.drawio.xml
✅ Reporte generado: diagrama_REPORT.txt
✅ Validación: Válido

📊 RESUMEN DE CAMBIOS:
   • Nodos movidos significativamente: 22
   • Cambios en waypoints: 28
   • Aristas que requieren revisión: 21
   • Problemas críticos: 0
```

## 🐛 Solución de Problemas

### ELK no disponible

Si Node.js o elkjs no están instalados:
- El pipeline usará automáticamente el algoritmo interno
- O usa `--use-internal` explícitamente

### Errores de conexión

Si hay errores de conexión:
- Use `--validate-only` para diagnosticar
- Revise el reporte de validación

### Waypoints incorrectos

Si los waypoints no son correctos:
- Revise el reporte para ver aristas problemáticas
- Ajuste manualmente en draw.io si es necesario

## 📚 Referencias

- [ELK - Eclipse Layout Kernel](https://www.eclipse.org/elk/)
- [elkjs - ELK for JavaScript](https://github.com/kieler/elkjs)
- [Draw.io XML Format](https://github.com/jgraph/drawio)

## ✅ Ventajas del Pipeline

1. **Automático**: Todo el proceso en un solo comando
2. **Robusto**: Fallback a algoritmo interno si ELK no está disponible
3. **Informativo**: Reporte detallado de cambios y problemas
4. **Validado**: Verificación automática antes y después
5. **Reproducible**: Mismo resultado con mismos inputs

