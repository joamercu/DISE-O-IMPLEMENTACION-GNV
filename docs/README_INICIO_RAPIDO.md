# 🚀 Inicio Rápido - Aplicación GNV

## Iniciar la Aplicación

### Opción 1: Script Simple (Recomendado)
Doble clic en: **`iniciar_app.bat`**

### Opción 2: Script con Verificaciones
Doble clic en: **`iniciar_app_verbose.bat`** (muestra más información)

### Opción 3: Manualmente
```bash
cd src
streamlit run calculos_combustible_vehicular.py
```

## Instalar Dependencias

Si es la primera vez que ejecuta la aplicación:
1. Doble clic en: **`instalar_dependencias.bat`**
2. O manualmente:
   ```bash
   pip install -r requirements.txt
   ```

## Requisitos

- Python 3.8 o superior
- Streamlit
- Pandas

## Solución de Problemas

### Error: "Streamlit no está instalado"
Ejecute: `instalar_dependencias.bat`

### Error: "No se encuentra el archivo"
Asegúrese de que el archivo `.bat` esté en la raíz del proyecto.

### La aplicación no se abre en el navegador
Abra manualmente: http://localhost:8501

## Credenciales por Defecto

- **Administrador:** usuario: `admin`, contraseña: `admin123`
- **Cliente:** usuario: `cliente`, contraseña: `cliente123`

