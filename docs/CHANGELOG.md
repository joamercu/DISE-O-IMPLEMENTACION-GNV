# 📝 Changelog - Aplicación GNV

Todos los cambios notables de este proyecto serán documentados en este archivo.

## [1.2] - 2024-12-19

### ✨ Agregado
- **API REST para datos de salida del proyecto**
  - Servidor FastAPI (`src/api_endpoint.py`)
  - Endpoint `GET /datos-salida` - Obtiene todos los datos de salida con timestamp
  - Endpoint `GET /datos-salida/resumen` - Resumen ligero sin contenido de archivos
  - Endpoint `POST /datos-salida/crear-carpeta` - Crea carpeta organizada "cliente 1 - petroliquidos"
  - Organización automática de archivos por categorías (outputs, data, docs, assets)
  - Codificación de archivos en base64 para transferencia
  - Generación de metadatos con timestamp
  - Documentación interactiva (Swagger UI y ReDoc)
  - Script de inicio `scripts/iniciar_api.bat`
  - Ejemplo de uso `ejemplo_uso_api.py`

### 📚 Documentación
- Nuevo documento [API_ENDPOINT_DATOS_SALIDA.md](API_ENDPOINT_DATOS_SALIDA.md)
- Actualización de README.md con sección de API REST
- Actualización de API_REFERENCE.md con endpoints REST
- Actualización de todos los documentos de referencia

---

## [1.1] - 2024-12-19

### ✨ Agregado
- **Generador automático de diagramas P&ID (draw.io)**
  - Módulo `drawio_agent.py` con clase `DrawIOAgent`
  - Integración con Streamlit (`drawio_integration.py`)
  - Generación automática de diagramas con variables dinámicas
  - Componentes del sistema: tanques, reguladores, válvulas, sensores, ECU, inyectores, motor
  - Conexiones entre componentes con etiquetas de presión
  - Leyenda y notas técnicas
  - Panel de variables del proyecto
  - Descarga del diagrama en formato .drawio.xml
  - Compatible con [draw.io](https://app.diagrams.net)

### 📚 Documentación
- Actualización de README.md con nueva funcionalidad
- Actualización de ARQUITECTURA.md con módulos draw.io
- Actualización de GUIA_USUARIO.md con instrucciones de uso
- Actualización de API_REFERENCE.md con documentación de funciones
- Actualización de CHANGELOG.md

---

## [1.0] - 2024-12-19

### ✨ Agregado
- Sistema de autenticación con roles (Administrador/Cliente)
- Cálculo completo de sistemas GNV/CNG
- Análisis de sensibilidad con gráficos
- Gestión de datos del cliente
- Manifest del proyecto con formularios interactivos
- Exportación de informes (HTML, JSON)
- Sistema de recordar usuario
- Registro de auditoría con timestamps
- Descarga de entregables para administradores
- Formularios interactivos para decisiones pendientes
- **Generador automático de diagramas P&ID (draw.io)** - Nuevo
  - Agente `DrawIOAgent` para generación de diagramas
  - Integración con Streamlit (`drawio_integration.py`)
  - Componentes dinámicos con variables calculadas
  - Exportación a formato draw.io compatible
  - Visualización de variables del diagrama

### 🔧 Mejorado
- Arquitectura modular optimizada
- Eliminación de código duplicado (~250 líneas)
- Rutas centralizadas en config.py
- Motor de cálculos reutilizable
- Validación de datos mejorada
- Manejo de errores robusto

### 📚 Documentación
- README.md principal actualizado
- Guía de usuario completa
- Documentación de parámetros
- Documentación de arquitectura
- Verificación de vínculos internos

### 🏗️ Estructura
- Módulos organizados en `utils/`
- Configuración centralizada en `config.py`
- Archivos de datos en `data/`
- Documentación en `docs/`

### 🔒 Seguridad
- Hash SHA-256 para contraseñas
- Sistema de roles con permisos diferenciados
- Validación de entrada de datos
- Registro de auditoría

### 📊 Funcionalidades
- 6 pestañas principales:
  1. Cálculos Principales
  2. Datos del Cliente
  3. Fórmulas y Procedimientos (solo Admin)
  4. Análisis de Sensibilidad
  5. Manifest del Proyecto
  6. Información Técnica

### ⚙️ Parámetros
- Todos los parámetros configurables desde la UI
- Valores por defecto basados en estándares técnicos
- Constantes físicas editables
- Parámetros del proyecto editables (solo Admin)

### 🚀 Scripts
- `iniciar_app.bat` - Inicio rápido
- `iniciar_app_verbose.bat` - Inicio con verificaciones
- `instalar_dependencias.bat` - Instalación de dependencias

---

## Próximas Versiones

### [1.1] - Planificado
- [ ] Base de datos SQLite
- [ ] Sistema de logging
- [ ] Tests unitarios
- [ ] Mejoras en UI/UX
- [ ] Exportación a PDF

### [1.3] - Planificado
- [ ] Caché de cálculos
- [ ] Historial de cálculos
- [ ] Comparación de escenarios
- [ ] Autenticación en API REST

---

*Última actualización: 2024-12-19*

