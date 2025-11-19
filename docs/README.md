# 📚 Documentación Técnica - Aplicación GNV

## Índice de Documentación

### 📖 Documentación Principal

1. **[GUIA_USUARIO.md](GUIA_USUARIO.md)** - Guía completa para usuarios finales
2. **[PARAMETROS.md](PARAMETROS.md)** - Documentación detallada de parámetros
3. **[ARQUITECTURA.md](ARQUITECTURA.md)** - Arquitectura técnica del sistema
4. **[API_REFERENCE.md](API_REFERENCE.md)** - Referencia de funciones y módulos
5. **[INSTALACION.md](INSTALACION.md)** - Guía de instalación y configuración
6. **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios y versiones

### 🔍 Documentación Técnica

7. **[VERIFICACION_VINCULOS.md](VERIFICACION_VINCULOS.md)** - Verificación técnica
8. **[ANALISIS_ARQUITECTURA.md](ANALISIS_ARQUITECTURA.md)** - Análisis inicial
9. **[PROPUESTA_MODULARIZACION.md](PROPUESTA_MODULARIZACION.md)** - Propuesta de modularización

### 📄 Documentos de Referencia

10. **[PETROLIQUIDOS_GNV_Informe_v1.md](PETROLIQUIDOS_GNV_Informe_v1.md)** - Informe técnico original
11. **[Resolucion_957_2012_Resumen.md](Resolucion_957_2012_Resumen.md)** - Resumen normativo

## Descripción General

Esta aplicación Streamlit permite calcular los parámetros técnicos necesarios para la conversión de vehículos pesados a Gas Natural Vehicular (GNV/CNG).

## Características Principales

- ✅ Sistema de autenticación con roles (Administrador/Cliente)
- ✅ Cálculos completos de sistemas GNV/CNG
- ✅ Análisis de sensibilidad
- ✅ Gestión de datos del cliente
- ✅ Manifest del proyecto
- ✅ Exportación de informes (HTML, JSON)
- ✅ Formularios interactivos para decisiones pendientes
- ✅ **Generador automático de diagramas P&ID (draw.io)** - Nuevo

## Estructura Técnica

### Módulos Principales

```
src/
├── calculos_combustible_vehicular.py  # Aplicación principal (2021 líneas)
├── auth_system.py                      # Sistema de autenticación
├── config.py                           # Configuración centralizada
└── utils/
    ├── auth_utils.py                   # Utilidades de autenticación
    ├── manifest_utils.py               # Manejo de manifest
    ├── calculation_engine.py           # Motor de cálculos
    ├── file_handler.py                 # Manejo de archivos
    ├── drawio_agent.py                 # Agente generador de diagramas P&ID
    └── drawio_integration.py           # Integración draw.io con Streamlit
```

### Flujo de Datos

```
Usuario → Autenticación → Interfaz Streamlit → Módulos Utils → Cálculos → Resultados
```

## Tecnologías Utilizadas

- **Streamlit:** Framework web para aplicaciones Python (>=1.28.0)
- **Pandas:** Manipulación y análisis de datos (>=2.0.0)
- **Python:** Lenguaje de programación (3.8+)

## Configuración

Todos los parámetros están centralizados en `src/config.py`:

- Parámetros por defecto de cálculo
- Rutas de archivos
- Constantes físicas
- Configuración de la aplicación

## Parámetros Principales

### Parámetros de Operación
- Consumo de diésel: **35.0 L/100 km**
- Autonomía deseada: **800.0 km**

### Parámetros Técnicos
- Poder calorífico diésel: **35.8 MJ/L**
- LHV CH₄: **50.0 MJ/kg**
- Eficiencia de conversión: **0.95**

### Parámetros de Almacenamiento
- Presión de llenado: **200.0 bar**
- Temperatura de operación: **25.0 °C**
- Factor de compresibilidad Z: **0.85**
- Volumen unitario tanque: **0.080 m³**
- Peso tanque vacío: **65.0 kg**

*Ver [PARAMETROS.md](PARAMETROS.md) para documentación completa*

## Seguridad

- Hash SHA-256 para contraseñas
- Sistema de roles con permisos diferenciados
- Validación de entrada de datos
- Registro de auditoría

## Mantenimiento

Para actualizar parámetros, modificar `src/config.py`.  
Para agregar funcionalidades, crear nuevos módulos en `src/utils/`.

## Versión Actual

- **Versión:** 1.0
- **Fecha:** 2024-12-19
- **Cliente:** PETROLIQUIDOS
- **Última actualización:** 2024-12-19

---

*Documentación actualizada: 2024-12-19*
