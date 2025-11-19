# 📚 Documentación Completa - Aplicación GNV

## 🎯 Resumen Ejecutivo

**Proyecto:** CALCULOS COMBUSTIBLE VEHICULAR GNC/GNL  
**Cliente:** PETROLIQUIDOS  
**Versión:** 1.0  
**Fecha:** 2024-12-19  
**Estado:** ✅ Completamente Documentado

## 📑 Estructura de Documentación

### Documentación Principal (Raíz)

- **[README.md](../README.md)** - Documentación principal del proyecto
- **[README_INICIO_RAPIDO.md](../README_INICIO_RAPIDO.md)** - Guía de inicio rápido

### Documentación Técnica (docs/)

#### Para Usuarios
1. **[GUIA_USUARIO.md](GUIA_USUARIO.md)** ⭐
   - Guía completa paso a paso
   - Instrucciones de uso de cada pestaña
   - Funciones por rol
   - Consejos y mejores prácticas

2. **[INSTALACION.md](INSTALACION.md)** ⭐
   - Requisitos del sistema
   - Instalación paso a paso
   - Solución de problemas
   - Configuración avanzada

#### Para Desarrolladores
3. **[ARQUITECTURA.md](ARQUITECTURA.md)** ⭐
   - Estructura del sistema
   - Flujo de datos
   - Módulos y responsabilidades
   - Patrones de diseño

4. **[API_REFERENCE.md](API_REFERENCE.md)** ⭐
5. **[API_ENDPOINT_DATOS_SALIDA.md](API_ENDPOINT_DATOS_SALIDA.md)** - Documentación API REST ⭐
   - Referencia completa de funciones
   - Parámetros y retornos
   - Ejemplos de uso
   - Módulos disponibles

#### Para Todos
5. **[PARAMETROS.md](PARAMETROS.md)** ⭐
   - Todos los parámetros documentados
   - Valores por defecto
   - Rangos permitidos
   - Fórmulas de cálculo
   - Valores recomendados

6. **[RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)**
   - Resumen ejecutivo
   - Alcance del proyecto
   - Estado actual
   - Próximos pasos

7. **[CHANGELOG.md](CHANGELOG.md)**
   - Historial de versiones
   - Cambios realizados
   - Mejoras futuras

#### Documentación Técnica Adicional
8. **[VERIFICACION_VINCULOS.md](VERIFICACION_VINCULOS.md)**
   - Verificación técnica
   - Optimizaciones realizadas
   - Estado del código

9. **[INDICE.md](INDICE.md)**
   - Índice completo de documentación
   - Guía de navegación

## 📊 Parámetros Actuales (Resumen)

### Parámetros de Operación
| Parámetro | Valor por Defecto | Rango |
|-----------|-------------------|-------|
| Consumo de Diésel | 35.0 L/100 km | 1.0 - 200.0 |
| Autonomía Deseada | 800.0 km | 100.0 - 2000.0 |

### Parámetros Técnicos
| Parámetro | Valor por Defecto | Rango | Estándar |
|-----------|-------------------|-------|----------|
| Poder Calorífico Diésel | 35.8 MJ/L | 30.0 - 40.0 | ASTM D975 |
| LHV CH₄ | 50.0 MJ/kg | 45.0 - 55.0 | ISO 6976:2016 |
| Eficiencia de Conversión | 0.95 | 0.80 - 1.0 | - |

### Parámetros de Almacenamiento
| Parámetro | Valor por Defecto | Rango |
|-----------|-------------------|-------|
| Presión de Llenado | 200.0 bar | 150.0 - 300.0 |
| Temperatura de Operación | 25.0 °C | 0.0 - 50.0 |
| Factor de Compresibilidad Z | 0.85 | 0.70 - 1.0 |
| Volumen Unitario Tanque | 0.080 m³ | 0.01 - 0.20 |
| Peso Tanque Vacío | 65.0 kg | 20.0 - 150.0 |
| Peso Soportes | 10.0 kg | 5.0 - 30.0 |
| Peso Accesorios | 5.0 kg | 1.0 - 20.0 |

### Constantes Físicas
| Constante | Valor | Unidad |
|-----------|-------|--------|
| Constante Universal de Gases R | 8.314 | J/(mol·K) |
| Masa Molar CH₄ | 0.01604 | kg/mol |

*Ver [PARAMETROS.md](PARAMETROS.md) para documentación completa*

## 🏗️ Estructura del Sistema

### Módulos Principales
```
src/
├── calculos_combustible_vehicular.py  # App principal (2012 líneas)
├── auth_system.py                      # Autenticación
├── config.py                           # Configuración
└── utils/
    ├── auth_utils.py                   # Utilidades auth
    ├── manifest_utils.py               # Manejo manifest
    ├── calculation_engine.py          # Motor cálculos
    └── file_handler.py                 # Manejo archivos
```

### Pestañas de la Aplicación
1. 🔢 **Cálculos Principales** - Cálculo del sistema GNV
2. 👤 **Datos del Cliente** - Información y supuestos
3. 📐 **Fórmulas y Procedimientos** - Fórmulas técnicas (solo Admin)
4. 📊 **Análisis de Sensibilidad** - Análisis de variaciones
5. 📋 **Manifest del Proyecto** - Información del proyecto
6. ℹ️ **Información Técnica** - Referencia técnica

## 🔐 Credenciales por Defecto

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

**Cliente:**
- Usuario: `cliente`
- Contraseña: `cliente123`

⚠️ **Cambiar en producción**

## 📁 Archivos Importantes

### Código Fuente
- `src/calculos_combustible_vehicular.py` - Aplicación principal
- `src/config.py` - Configuración centralizada
- `src/auth_system.py` - Sistema de autenticación

### Datos
- `data/PETROLIQUIDOS_GNV_manifest_v1.json` - Manifest
- `data/users_db.json` - Base de datos de usuarios
- `data/remembered_user.json` - Usuario recordado

### Scripts
- `iniciar_app.bat` - Inicio rápido
- `instalar_dependencias.bat` - Instalación

## 🚀 Inicio Rápido

1. **Instalar dependencias:**
   ```bash
   instalar_dependencias.bat
   ```

2. **Iniciar aplicación:**
   ```bash
   iniciar_app.bat
   ```

3. **Acceder:**
   - URL: http://localhost:8501
   - Usuario: `admin` / Contraseña: `admin123`

## 📖 Guía de Navegación

### Para Usuarios Nuevos
1. Leer [GUIA_USUARIO.md](GUIA_USUARIO.md)
2. Consultar [PARAMETROS.md](PARAMETROS.md)
3. Revisar [INSTALACION.md](INSTALACION.md) si hay problemas

### Para Desarrolladores
1. Revisar [ARQUITECTURA.md](ARQUITECTURA.md)
2. Consultar [API_REFERENCE.md](API_REFERENCE.md)
3. Ver [VERIFICACION_VINCULOS.md](VERIFICACION_VINCULOS.md)

### Para Administradores
1. Leer [RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)
2. Revisar [CHANGELOG.md](CHANGELOG.md)
3. Consultar [ARQUITECTURA.md](ARQUITECTURA.md)

## ✅ Estado de la Documentación

- ✅ README principal actualizado
- ✅ Guía de usuario completa
- ✅ Documentación de parámetros actualizada
- ✅ Arquitectura documentada
- ✅ Referencia de API completa
- ✅ Guía de instalación
- ✅ Changelog actualizado
- ✅ Índices creados

## 📝 Notas Importantes

1. **Parámetros:** Todos los parámetros están en `src/config.py`
2. **Rutas:** Todas las rutas están centralizadas
3. **Seguridad:** Cambiar credenciales en producción
4. **Datos:** Los archivos JSON están en `data/`
5. **Documentación:** Toda la documentación está en `docs/`

## 🔄 Actualización de Documentación

Esta documentación se actualiza automáticamente cuando:
- Se modifican parámetros en `config.py`
- Se agregan nuevas funcionalidades
- Se cambian valores por defecto

**Última actualización:** 2024-12-19

---

*Documentación completa y actualizada: 2024-12-19*

