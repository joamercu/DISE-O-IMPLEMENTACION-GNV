# Pipeline Híbrido Automatizado - Layout Ortogonal P&ID

## 📋 Descripción

Pipeline robusto (Opción A) para optimización automática de diagramas P&ID en formato draw.io XML.

### Características

✅ **Extracción de grafo**: Nodos, puertos y edges del XML draw.io  
✅ **Constraints**: Puertos obligatorios, prioridades de edges, bounding boxes fijas  
✅ **Layout ortogonal**: Algoritmo inspirado en ELK para cálculo de posiciones y waypoints  
✅ **Aplicación automática**: Actualización de geometrías y waypoints en XML  
✅ **Validación**: Verificación automática con XPaths  

## 🚀 Uso

### Uso básico

```bash
python pipeline_completo.py [archivo.drawio.xml]
```

### Opciones

```bash
# Especificar archivo de salida
python pipeline_completo.py --output diagrama_optimizado.drawio.xml

# Solo validar sin aplicar layout
python pipeline_completo.py --validate-only

# Saltar cálculo de layout (solo aplicar waypoints existentes)
python pipeline_completo.py --skip-layout
```

## 📁 Archivos del Pipeline

### Módulos principales

1. **`elk_layout_pipeline.py`**
   - `DrawIOGraphExtractor`: Extrae grafo del XML
   - Clases: `Graph`, `Node`, `Edge`, `Port`, `EdgePriority`

2. **`elk_layout_engine.py`**
   - `OrthogonalLayoutEngine`: Calcula layout ortogonal
   - Algoritmo de posicionamiento evitando solapamientos
   - Cálculo de waypoints ortogonales

3. **`xml_applicator.py`**
   - `XMLApplicator`: Aplica resultados al XML
   - Actualiza geometrías de nodos
   - Actualiza waypoints de edges

4. **`validator.py`**
   - `DiagramValidator`: Validación automática
   - Verifica estructura XML
   - Verifica conexiones y geometrías
   - Detecta solapamientos

5. **`pipeline_completo.py`**
   - Orquesta todos los módulos
   - Interfaz de línea de comandos

## 🔧 Funcionamiento

### Paso 1: Extracción de Grafo
- Lee el XML draw.io
- Identifica nodos (vértices) y edges (conexiones)
- Infiere puertos basados en conexiones
- Clasifica tipos de nodos y edges

### Paso 2: Validación Inicial
- Verifica estructura XML
- Valida geometrías de nodos
- Verifica conexiones (source/target válidos)
- Detecta solapamientos iniciales

### Paso 3: Cálculo de Layout
- Posiciona nodos respetando constraints:
  - Nodos fijos mantienen posición
  - Nodos con prioridad alta se posicionan primero
  - Evita solapamientos
- Calcula waypoints ortogonales:
  - Ruteo L-shaped o U-shaped
  - Alineación a grid
  - Respeta puertos cuando están definidos

### Paso 4: Aplicación al XML
- Actualiza `mxGeometry` de nodos
- Actualiza `Array` de waypoints en edges
- Mantiene estructura XML válida

### Paso 5: Validación Final
- Verifica integridad del resultado
- Reporta errores y advertencias

## 📊 Tipos de Nodos Soportados

- **Tanques**: `cylinder3`
- **Válvulas**: `valve`
- **Reguladores**: `hexagon`
- **Manifolds**: `parallelogram`
- **Sensores**: `ellipse`
- **ECU**: `rect` (con borde punteado)
- **Filtros**: `cylinder`

## 🔗 Tipos de Edges

- **Gas (MAIN_PIPE)**: Tuberías principales (prioridad 1)
- **Control (CONTROL_SIGNAL)**: Señales de control (prioridad 2)
- **Data (DATA_SIGNAL)**: Señales de datos (prioridad 3)
- **Vent (VENT)**: Venteos (prioridad 4)

## ⚙️ Parámetros Configurables

En `elk_layout_engine.py`:

```python
self.grid_size = 50        # Tamaño de grid para alineación
self.min_distance = 100    # Distancia mínima entre nodos
self.port_offset = 10      # Offset de puertos desde el borde
```

## ✅ Validaciones Realizadas

1. **Estructura XML**: Elementos principales presentes
2. **Geometrías**: Dimensiones válidas, posiciones no negativas
3. **Conexiones**: Source y target válidos
4. **Waypoints**: Coordenadas válidas
5. **Solapamientos**: Detección de nodos superpuestos

## 📝 Ejemplo de Salida

```
======================================================================
PIPELINE AUTOMATIZADO - LAYOUT ORTOGONAL P&ID
======================================================================
📁 Archivo de entrada: diagrama.drawio.xml
📁 Archivo de salida: diagrama_LAYOUT.drawio.xml

PASO 1: EXTRACCIÓN DE GRAFO
----------------------------------------------------------------------
📊 Extrayendo grafo del diagrama...
   ✅ Nodos extraídos: 42
   ✅ Edges extraídos: 28
   ✅ Puertos inferidos: 56

PASO 2: VALIDACIÓN INICIAL
----------------------------------------------------------------------
🔍 Validando diagrama...
   ✅ Validación completada

PASO 3: CÁLCULO DE LAYOUT ORTOGONAL
----------------------------------------------------------------------
🔧 Calculando layout ortogonal...
   ✅ Layout calculado para 42 nodos
   ✅ Waypoints calculados para 28 edges

PASO 4: APLICACIÓN AL XML
----------------------------------------------------------------------
📝 Aplicando layout al XML...
   ✅ 42 nodos actualizados
   ✅ 28 edges actualizados

PASO 5: VALIDACIÓN FINAL
----------------------------------------------------------------------
🔍 Validando diagrama...
   ✅ Validación completada

🎉 Pipeline completado exitosamente!
```

## 🔍 Revisión Manual Fina

Después de ejecutar el pipeline:

1. Abra el archivo generado en [draw.io](https://app.diagrams.net)
2. Revise posicionamiento de nodos críticos
3. Ajuste waypoints si es necesario
4. Verifique que todas las conexiones sean claras
5. Asegúrese de que no haya solapamientos visuales

## 🐛 Solución de Problemas

### Errores de conexión
- Verifique que todos los edges tengan source y target válidos
- Use `--validate-only` para diagnosticar

### Solapamientos
- El algoritmo intenta evitarlos automáticamente
- Si persisten, ajuste `min_distance` en el engine
- Revise manualmente en draw.io

### Waypoints incorrectos
- Verifique que los puertos estén correctamente inferidos
- Ajuste `grid_size` para mejor alineación

## 📚 Referencias

- [Draw.io XML Format](https://github.com/jgraph/drawio)
- [ELK - Eclipse Layout Kernel](https://www.eclipse.org/elk/)
- [P&ID Standards (ISA S5.1)](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa51)

