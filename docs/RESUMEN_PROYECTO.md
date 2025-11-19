# 📋 Resumen del Proyecto - Aplicación GNV

## Información General

**Nombre del Proyecto:** CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL  
**Cliente:** PETROLIQUIDOS  
**Versión:** 1.0  
**Fecha:** 2024-12-19  
**Estado:** ✅ Activo y Funcional

## Objetivo

Desarrollar una herramienta de cálculo para dimensionar sistemas de Gas Natural Vehicular (GNV/CNG) para vehículos pesados, permitiendo:

- Cálculo de parámetros técnicos necesarios
- Análisis de diferentes escenarios
- Gestión de información del cliente
- Documentación y exportación de resultados

## Alcance

### Funcionalidades Implementadas

1. **Sistema de Autenticación**
   - Roles: Administrador y Cliente
   - Hash SHA-256 para contraseñas
   - Recordar usuario (solo username)

2. **Cálculos Principales**
   - Dimensionamiento de tanques
   - Cálculo de energía requerida
   - Estimación de peso adicional
   - Proceso paso a paso

3. **Gestión de Datos**
   - Formulario de datos del cliente
   - Supuestos operativos y de componentes
   - Exportación a JSON (solo Admin)
   - Registro de auditoría

4. **Análisis de Sensibilidad**
   - Variación de consumo
   - Variación de autonomía
   - Gráficos interactivos

5. **Manifest del Proyecto**
   - Visualización completa
   - Formularios interactivos
   - Descarga de entregables
   - Exportación HTML/JSON

6. **Información Técnica**
   - Fórmulas y procedimientos (solo Admin)
   - Normativas y certificaciones
   - Generación de informes HTML

## Tecnología

- **Framework:** Streamlit 1.28.0+
- **Lenguaje:** Python 3.8+
- **Datos:** Pandas 2.0.0+
- **Almacenamiento:** JSON files

## Estructura

### Pestañas de la Aplicación

1. 🔢 **Cálculos Principales** - Cálculo del sistema GNV
2. 👤 **Datos del Cliente** - Información y supuestos
3. 📐 **Fórmulas y Procedimientos** - Fórmulas técnicas (solo Admin)
4. 📊 **Análisis de Sensibilidad** - Análisis de variaciones
5. 📋 **Manifest del Proyecto** - Información del proyecto
6. ℹ️ **Información Técnica** - Referencia técnica

## Parámetros Principales

### Valores por Defecto

- Consumo diésel: 35.0 L/100 km
- Autonomía: 800.0 km
- Presión: 200.0 bar
- Temperatura: 25.0 °C
- Volumen tanque: 0.080 m³ (80 L)
- Peso tanque: 65.0 kg

### Constantes Físicas

- Constante de gases R: 8.314 J/(mol·K)
- Masa molar CH₄: 0.01604 kg/mol

## Usuarios por Defecto

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

**Cliente:**
- Usuario: `cliente`
- Contraseña: `cliente123`

⚠️ **Cambiar en producción**

## Archivos Importantes

### Código Fuente
- `src/calculos_combustible_vehicular.py` - Aplicación principal
- `src/config.py` - Configuración
- `src/auth_system.py` - Autenticación
- `src/utils/` - Módulos utilitarios

### Datos
- `data/PETROLIQUIDOS_GNV_manifest_v1.json` - Manifest
- `data/users_db.json` - Usuarios
- `data/remembered_user.json` - Usuario recordado

### Scripts
- `iniciar_app.bat` - Inicio rápido
- `instalar_dependencias.bat` - Instalación

## Documentación

Toda la documentación está en `docs/`:
- Guía de usuario
- Documentación de parámetros
- Arquitectura del sistema
- Referencia de API
- Guía de instalación

## Estado Actual

✅ **Completado:**
- Sistema de autenticación
- Cálculos principales
- Análisis de sensibilidad
- Gestión de datos del cliente
- Manifest del proyecto
- Exportación de informes
- Generador automático de diagramas P&ID
- **API REST para datos de salida** ✅
- Documentación completa

## Próximos Pasos

- [ ] Base de datos SQLite
- [ ] Sistema de logging
- [ ] Tests unitarios
- [ ] Exportación a PDF
- [x] API REST ✅ **Completado**

## Contacto

Para consultas técnicas o actualizaciones, contactar al equipo de ingeniería.

---

*Resumen actualizado: 2024-12-19*

