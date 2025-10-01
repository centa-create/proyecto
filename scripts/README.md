# 📜 Scripts de Utilidad - SAMMS.FO

Esta carpeta contiene scripts de utilidad para el mantenimiento y gestión del proyecto SAMMS.FO.

## 📋 Scripts Disponibles

### 🛍️ `add_sample_products.py`
**Propósito**: Agrega productos de ejemplo a la base de datos para desarrollo y testing.

**Uso**:
```bash
python scripts/add_sample_products.py
```

**Funcionalidades**:
- ✅ Crea productos de ejemplo con imágenes
- ✅ Agrega categorías automáticamente
- ✅ Configura precios y descripciones realistas
- ✅ Útil para desarrollo y demostraciones

**Requisitos**: Base de datos configurada y accesible.

---

### 🔍 `inspect_db.py`
**Propósito**: Inspecciona y muestra información detallada sobre el contenido de la base de datos.

**Uso**:
```bash
python scripts/inspect_db.py
```

**Funcionalidades**:
- ✅ Muestra estadísticas generales de la BD
- ✅ Lista todas las tablas y sus registros
- ✅ Verifica integridad de relaciones
- ✅ Útil para debugging y auditorías

**Requisitos**: Base de datos configurada y con datos.

---

### 🔐 `migrate_password_column.py`
**Propósito**: Migra el formato de almacenamiento de contraseñas (legacy → bcrypt).

**Uso**:
```bash
python scripts/migrate_password_column.py
```

**Funcionalidades**:
- ✅ Detecta contraseñas sin hashear
- ✅ Migra a bcrypt de forma segura
- ✅ Verifica integridad post-migración
- ✅ Backup automático antes de migrar

**⚠️ Importante**: Hacer backup de la base de datos antes de ejecutar.

---

### 📱 `add_phone_column.py`
**Propósito**: Agrega la columna 'phone' al modelo de usuario para soporte de recuperación por SMS.

**Uso**:
```bash
python scripts/add_phone_column.py
```

**Funcionalidades**:
- ✅ Agrega columna phone VARCHAR(20) UNIQUE a la tabla user
- ✅ Verifica si la columna ya existe antes de crear
- ✅ Compatible con SQLite y PostgreSQL
- ✅ Seguro para ejecutar múltiples veces

**Requisitos**: Base de datos configurada y accesible.

**Relacionado con**: Recuperación de contraseña por SMS usando Twilio.

---

## 🚀 Automatización con Makefile

Los scripts también se pueden ejecutar usando los comandos del Makefile:

```bash
# Agregar productos de ejemplo
make add-samples

# Inspeccionar base de datos
make inspect-db

# Migrar contraseñas
make migrate-passwords
```

## 📱 Configuración de Twilio para SMS

Para habilitar el envío real de SMS en la recuperación de contraseñas:

### 1. Instalar Twilio
```bash
pip install twilio
```

### 2. Configurar cuenta en Twilio
1. Crear cuenta en [twilio.com](https://twilio.com)
2. Verificar número de teléfono
3. Obtener credenciales:
   - Account SID
   - Auth Token
   - Número de teléfono de Twilio

### 3. Configurar variables de entorno
Agregar a tu archivo `.env`:
```bash
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### 4. Probar configuración
```bash
python -c "from twilio.rest import Client; c = Client('sid', 'token'); print('Twilio OK')"
```

### ⚠️ Notas de Seguridad
- Nunca commits las credenciales de Twilio al repositorio
- Usar variables de entorno en producción
- Monitorear uso de SMS para controlar costos

## 📝 Notas de Desarrollo

### Estructura de los Scripts
Todos los scripts siguen esta estructura estándar:

1. **Imports y configuración**
2. **Función main()** con lógica principal
3. **Manejo de errores** con try/except
4. **Logging apropiado** para debugging
5. **Documentación** con docstrings

### Mejores Prácticas
- ✅ **Idempotentes**: Se pueden ejecutar múltiples veces sin efectos secundarios
- ✅ **Transaccionales**: Usan transacciones de BD cuando es necesario
- ✅ **Logging**: Registran todas las operaciones importantes
- ✅ **Validaciones**: Verifican pre-condiciones antes de ejecutar
- ✅ **Backup**: Crean backups cuando modifican datos críticos

### Variables de Entorno
Los scripts respetan las variables de entorno definidas en `.env`:
- `DATABASE_URL`: URL de conexión a la base de datos
- `FLASK_ENV`: Entorno de ejecución (development/production)

## 🆘 Solución de Problemas

### Error de Conexión a BD
```bash
# Verificar variables de entorno
echo $DATABASE_URL

# Probar conexión manual
python -c "from app.db import db; db.create_all(); print('Conexión OK')"
```

### Permisos de Escritura
```bash
# Verificar permisos en directorio de la app
ls -la app/

# Cambiar permisos si es necesario
chmod 755 scripts/*.py
```

### Dependencias Faltantes
```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import flask, sqlalchemy; print('Dependencias OK')"
```

## 🤝 Contribuyendo

### Agregar Nuevos Scripts
1. Crear archivo en `scripts/nombre_script.py`
2. Seguir la estructura estándar de los scripts existentes
3. Agregar documentación completa
4. Actualizar este README.md
5. Agregar comando al Makefile si corresponde

### Convenciones de Nombres
- Usar `snake_case` para nombres de archivos
- Prefijo descriptivo (add_, inspect_, migrate_, etc.)
- Extensión `.py` siempre

## 📞 Soporte

Si encuentras problemas con los scripts:
1. Revisar los logs de error
2. Verificar la configuración de la base de datos
3. Consultar este documento
4. Abrir un issue en el repositorio