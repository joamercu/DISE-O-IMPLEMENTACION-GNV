# 🔐 Guía para Crear y Configurar Clave SSH

Esta guía te ayudará a crear una clave SSH para conectarte al servidor Debian sin necesidad de ingresar contraseña cada vez.

## 🚀 Método Rápido (Recomendado)

### Paso 1: Generar la Clave SSH

Ejecuta el script automático:
```batch
scripts\generar_clave_ssh.bat
```

Este script:
- Genera una clave SSH Ed25519 con tu email
- Guarda la clave en `ssh_keys/gnv_server_key`
- Muestra la clave pública para copiarla
- Actualiza automáticamente la configuración

**Durante la ejecución:**
- Cuando pregunte por la ruta, presiona **Enter** para usar la ruta por defecto
- Cuando pregunte por passphrase, puedes:
  - Presionar **Enter** (sin passphrase - más fácil)
  - O ingresar una contraseña (más seguro)

### Paso 2: Copiar la Clave al Servidor

Ejecuta:
```batch
scripts\copiar_clave_servidor.bat
```

Este script intentará copiar automáticamente la clave pública al servidor.

## 📝 Método Manual

Si prefieres hacerlo manualmente o el método automático no funciona:

### 1. Generar la Clave SSH

Abre PowerShell o CMD y ejecuta:
```bash
ssh-keygen -t ed25519 -C "joamercu@gmail.com"
```

**Respuestas a las preguntas:**
- **"Enter file in which to save the key"**: Presiona Enter (usa la ruta por defecto `C:\Users\TuUsuario\.ssh\id_ed25519`)
  - O ingresa una ruta personalizada como: `D:\19-11-25-DISEÑO E IMPLEMENTACION GNV\ssh_keys\gnv_server_key`
- **"Enter passphrase"**: Presiona Enter (sin passphrase) o ingresa una contraseña

### 2. Copiar la Clave Pública al Servidor

#### Opción A: Usando ssh-copy-id (si está disponible)
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@72.61.10.156
```

#### Opción B: Manual (más común en Windows)

1. **Ver el contenido de tu clave pública:**
   ```bash
   type C:\Users\TuUsuario\.ssh\id_ed25519.pub
   ```
   O si la guardaste en otra ubicación:
   ```bash
   type D:\19-11-25-DISEÑO E IMPLEMENTACION GNV\ssh_keys\gnv_server_key.pub
   ```

2. **Copiar todo el contenido** (debe verse algo como):
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... joamercu@gmail.com
   ```

3. **Conectarte al servidor:**
   ```bash
   ssh root@72.61.10.156
   ```
   (Ingresa tu contraseña cuando se solicite)

4. **En el servidor, ejecutar:**
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   nano ~/.ssh/authorized_keys
   ```

5. **Pegar la clave pública** en el archivo `authorized_keys`
   - Presiona `Ctrl+O` para guardar
   - Presiona `Enter` para confirmar
   - Presiona `Ctrl+X` para salir

6. **Ajustar permisos:**
   ```bash
   chmod 600 ~/.ssh/authorized_keys
   exit
   ```

### 3. Probar la Conexión

Ahora prueba conectarte sin contraseña:
```bash
ssh -i C:\Users\TuUsuario\.ssh\id_ed25519 root@72.61.10.156
```

O si guardaste la clave en otra ubicación:
```bash
ssh -i D:\19-11-25-DISEÑO E IMPLEMENTACION GNV\ssh_keys\gnv_server_key root@72.61.10.156
```

Si funciona, ya no te pedirá contraseña.

## ⚙️ Configurar los Scripts de Despliegue

### Si usaste el script automático

El script `generar_clave_ssh.bat` ya actualizó la configuración automáticamente. Solo necesitas ejecutar:
```batch
scripts\config_servidor.bat
```

### Si lo hiciste manualmente

1. **Ejecuta la configuración:**
   ```batch
   scripts\config_servidor.bat
   ```

2. **Edita `scripts\deploy_config.txt`** y actualiza la línea `SSH_KEY` con la ruta completa a tu clave privada:
   ```
   SSH_KEY=C:\Users\TuUsuario\.ssh\id_ed25519
   ```
   O:
   ```
   SSH_KEY=D:\19-11-25-DISEÑO E IMPLEMENTACION GNV\ssh_keys\gnv_server_key
   ```

## 🔍 Verificar que Todo Funciona

Ejecuta:
```batch
scripts\estado_servidor.bat
```

Si se conecta sin pedir contraseña, ¡todo está bien configurado!

## 🛠️ Solución de Problemas

### Error: "Permission denied (publickey)"

**Causa**: La clave no está en el servidor o los permisos son incorrectos.

**Solución**:
1. Verifica que copiaste la clave **pública** (`.pub`), no la privada
2. En el servidor, verifica permisos:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

### Error: "Could not open a connection to your authentication agent"

**Causa**: El agente SSH no está corriendo (normal en Windows).

**Solución**: Usa la opción `-i` para especificar la clave:
```bash
ssh -i ruta\a\tu\clave_privada usuario@servidor
```

### La clave se generó pero no está en la ubicación esperada

**Solución**: 
1. Busca dónde se guardó (normalmente en `C:\Users\TuUsuario\.ssh\`)
2. Cópiala a la ubicación que esperan los scripts
3. O actualiza `deploy_config.txt` con la ruta correcta

### Windows no encuentra `ssh-keygen`

**Causa**: OpenSSH no está instalado o no está en el PATH.

**Solución**:
1. Windows 10/11: OpenSSH viene preinstalado. Si no funciona:
   - Ve a **Configuración** > **Aplicaciones** > **Características opcionales**
   - Busca "OpenSSH Cliente" e instálalo
2. O descarga Git Bash que incluye OpenSSH

## 📁 Estructura de Archivos

Después de generar las claves, tendrás:

```
proyecto/
├── ssh_keys/                    # (si usaste el script automático)
│   ├── gnv_server_key          # Clave privada (¡NUNCA la compartas!)
│   └── gnv_server_key.pub      # Clave pública (esta sí se copia al servidor)
└── scripts/
    └── deploy_config.txt        # Configuración (actualizada automáticamente)
```

O si usaste la ubicación por defecto:
```
C:\Users\TuUsuario\.ssh\
├── id_ed25519                   # Clave privada
└── id_ed25519.pub              # Clave pública
```

## 🔒 Seguridad

- ✅ **Clave privada** (`gnv_server_key` o `id_ed25519`): **NUNCA** la compartas ni la subas a Git
- ✅ **Clave pública** (`.pub`): Esta sí se puede compartir (es lo que copias al servidor)
- ✅ Los scripts ya están configurados para ignorar claves en `.gitignore`
- ✅ Si usas passphrase, la necesitarás cada vez que uses la clave (más seguro pero menos conveniente)

## ✅ Checklist

- [ ] Clave SSH generada
- [ ] Clave pública copiada al servidor
- [ ] Conexión sin contraseña funciona
- [ ] `deploy_config.txt` tiene la ruta correcta a la clave privada
- [ ] Scripts de despliegue funcionan correctamente

## 🎯 Siguiente Paso

Una vez que la clave SSH esté configurada:
```batch
scripts\config_servidor.bat
scripts\deploy_app.bat
```

¡Listo para desplegar! 🚀

