# Sistema de Notificaciones y Seguimiento

## Descripción General

El sistema de notificaciones y seguimiento permite registrar automáticamente cuando un cliente envía sus datos, notificar al administrador (por email y en la aplicación), y llevar un seguimiento completo de los envíos con estados y notas.

## Componentes

### 1. Base de Datos PostgreSQL

El sistema utiliza PostgreSQL para almacenar:

- **Submissions**: Registro principal de envíos
- **Submission Data**: Datos del cliente enviados
- **Submission Calculos**: Resultados de cálculos asociados
- **Submission Diagramas**: Diagramas generados (XML y PDF)
- **Notificaciones**: Registro de todas las notificaciones enviadas

### 2. Módulo de Base de Datos (`src/database.py`)

Funciones principales:
- `init_database()` - Inicializar tablas
- `create_submission()` - Crear nuevo envío
- `get_submissions()` - Obtener envíos con filtros
- `update_submission_status()` - Actualizar estado
- `get_submission_by_id()` - Obtener envío completo
- `add_calculos_to_submission()` - Agregar cálculos
- `add_diagrama_to_submission()` - Agregar diagrama
- `get_submission_stats()` - Estadísticas

### 3. Sistema de Notificaciones (`src/notifications.py`)

Funciones:
- `send_email_notification()` - Enviar email al administrador
- `create_app_notification()` - Crear notificación en app
- `send_notifications()` - Enviar todas las notificaciones

### 4. Panel de Administración (`src/admin_panel.py`)

Interfaz completa para administradores con:
- Dashboard con estadísticas
- Lista de envíos con filtros
- Vista detallada de envíos
- Gestión de estados y notas
- Notificaciones no leídas

## Configuración

### 1. Variables de Entorno

Crear archivo `.env` desde `.env.example`:

```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gnv_app
DB_USER=gnv_user
DB_PASSWORD=tu_password

# Email SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
ADMIN_EMAIL=admin@weldtech.com
```

### 2. Inicialización de Base de Datos

```bash
python scripts/init_database.py
```

Este script:
- Crea la base de datos si no existe
- Crea todas las tablas necesarias
- Configura los índices y relaciones

## Flujo de Trabajo

### Cliente Envía Datos

1. Cliente completa formulario de datos del cliente
2. Al hacer clic en "Guardar":
   - Se crea un submission en BD con estado "pendiente"
   - Se guardan los datos del cliente
   - Se envía email al administrador
   - Se crea notificación en la app
   - Se guarda `submission_id` en session_state

### Cliente Realiza Cálculos

1. Cliente realiza cálculos del sistema
2. Los resultados se asocian automáticamente al submission activo
3. Se guardan en `submission_calculos`

### Cliente Genera Diagrama

1. Cliente genera diagrama P&ID
2. El diagrama se guarda en `submission_diagramas`
3. Se almacena XML y PDF (en base64)

### Administrador Revisa

1. Administrador ve notificaciones en el panel
2. Puede filtrar y buscar envíos
3. Revisa datos, cálculos y diagramas
4. Cambia estado (pendiente → en revisión → aprobado/rechazado)
5. Agrega notas si es necesario

## Estados de Envío

- **Pendiente**: Envío recién recibido, esperando revisión
- **En Revisión**: Administrador está revisando el envío
- **Aprobado**: Envío aprobado por el administrador
- **Rechazado**: Envío rechazado (con notas explicativas)

## Notificaciones

### Email

- Se envía automáticamente cuando un cliente envía datos
- Incluye información del cliente, fecha y enlaces
- Formato HTML con diseño profesional
- Requiere configuración SMTP válida

### Aplicación

- Aparece en el panel de administración
- Contador de notificaciones no leídas
- Lista de notificaciones recientes
- Se puede marcar como leída

## Uso del Panel de Administración

### Acceso

Solo disponible para usuarios con rol "Administrador". Aparece como una nueva pestaña en la aplicación.

### Dashboard

Muestra estadísticas generales:
- Total de envíos
- Envíos por estado
- Gráficos de distribución

### Gestión de Envíos

- **Filtros**: Por estado, cliente, fecha
- **Búsqueda**: Por nombre de cliente
- **Vista Detallada**: 
  - Datos del cliente
  - Resultados de cálculos
  - Diagramas generados
  - Historial de notificaciones
  - Gestión de estado y notas

### Notificaciones

- Lista de notificaciones no leídas
- Botón para ver envío asociado
- Marcar como leída

## Solución de Problemas

### Base de Datos No Conecta

1. Verificar que PostgreSQL esté ejecutándose
2. Verificar credenciales en `.env`
3. Verificar que la base de datos exista
4. Ejecutar `python scripts/init_database.py`

### Emails No Se Envían

1. Verificar configuración SMTP en `.env`
2. Para Gmail, usar "Contraseñas de aplicaciones"
3. Verificar que `ADMIN_EMAIL` sea válido
4. Revisar logs de errores en la consola

### Panel No Aparece

1. Verificar que el usuario sea "Administrador"
2. Verificar que PostgreSQL esté configurado
3. Revisar errores en la consola de la aplicación

## Seguridad

- Las credenciales se almacenan en variables de entorno
- Las contraseñas se hashean (SHA-256)
- Validación de inputs antes de guardar
- Sanitización de datos antes de mostrar
- Transacciones para operaciones críticas

## Próximas Mejoras

- Exportación de reportes de seguimiento
- Notificaciones por webhook
- Integración con sistemas externos
- Dashboard avanzado con más métricas
- Historial de cambios de estado detallado

