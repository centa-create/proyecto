# 🛍️ SAMMS.FO - Tienda Virtual

Una tienda virtual moderna construida con Flask, featuring un diseño visual impresionante con efectos de fondo estrellado, tema oscuro y una interfaz de usuario premium.

## ✨ Características

- 🎨 **Diseño Premium**: Tema oscuro con efectos visuales avanzados (glassmorphism, glow effects, animaciones 3D)
- 🌟 **Fondo Estrellado**: Sistema de estrellas animadas con nebulosas y meteoritos
- 🛒 **E-commerce Completo**: Carrito de compras, wishlist, sistema de pagos con Stripe
- 👥 **Sistema de Usuarios**: Autenticación, perfiles, dashboard personal
- 📱 **Responsive Design**: Optimizado para móviles y desktop
- 🔒 **Seguridad**: CSRF protection, rate limiting, encriptación de contraseñas
- 📊 **Panel Admin**: Gestión completa de productos, usuarios, pedidos y reportes
- 🔔 **Notificaciones**: Sistema de notificaciones en tiempo real con Socket.IO
- 🌐 **PWA Ready**: Service worker, manifest, offline support

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- pip
- Virtualenv (recomendado)

### Configuración

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/samms-fo.git
   cd samms-fo
   ```

2. **Crea entorno virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. **Instala dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura variables de entorno:**
   ```bash
   cp config/.env.example config/.env
   # Edita config/.env con tus configuraciones
   ```

5. **Ejecuta la aplicación:**
   ```bash
   python run.py
   ```

La aplicación estará disponible en `http://localhost:8095`

## 📁 Estructura del Proyecto

```
samms-fo/
├── 📁 app/                          # Aplicación principal
│   ├── __init__.py                 # Factory de la app
│   ├── db.py                       # Configuración BD
│   ├── extensions.py               # Extensiones Flask
│   ├── 📁 models/                  # Modelos SQLAlchemy
│   ├── 📁 routes/                  # Blueprints
│   ├── 📁 static/                  # CSS, JS, imágenes
│   └── 📁 templates/               # Plantillas Jinja2
├── 📁 config/                      # Configuraciones
│   ├── __init__.py                 # Config base
│   ├── development.py              # Desarrollo
│   ├── production.py               # Producción
│   └── testing.py                  # Testing
├── 📁 scripts/                     # Utilidades
├── 📁 tests/                       # Tests
├── 📁 docs/                        # Documentación
├── 📁 deploy/                      # Docker, deployment
├── run.py                         # Punto de entrada
├── requirements.txt               # Dependencias
└── README.md                      # Este archivo
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **Flask-Login** - Gestión de autenticación
- **Flask-WTF** - Formularios seguros
- **Flask-Mail** - Envío de correos
- **Flask-SocketIO** - WebSockets
- **Flask-Caching** - Sistema de caché
- **Flask-Limiter** - Rate limiting

### Frontend
- **Bootstrap 5** - Framework CSS
- **Montserrat Font** - Tipografía premium
- **CSS Custom Properties** - Sistema de variables
- **Glassmorphism Effects** - Efectos visuales modernos
- **3D CSS Transforms** - Carrusel 3D interactivo

### Base de Datos
- **SQLite** (desarrollo)
- **PostgreSQL** (producción recomendada)

### Pagos
- **Stripe** - Procesamiento de pagos

### Despliegue
- **Docker** - Containerización
- **Gunicorn** - WSGI server
- **Nginx** - Proxy reverso

## 🔧 Configuración de Entornos

### Desarrollo
```bash
export FLASK_ENV=development
python run.py
```

### Producción
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

### Testing
```bash
export FLASK_ENV=testing
pytest
```

## 📊 Scripts Disponibles

- `scripts/add_sample_products.py` - Agrega productos de ejemplo
- `scripts/inspect_db.py` - Inspecciona la base de datos
- `scripts/migrate_password_column.py` - Migra contraseñas

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests específicos
pytest tests/test_models.py
pytest tests/test_routes.py

# Con cobertura
pytest --cov=app --cov-report=html
```

## 🚀 Despliegue

### 🌟 Despliegue con Coolify (Recomendado)

Coolify es la plataforma ideal para desplegar SAMMS.FO con configuración automática y escalado.

#### Pasos para desplegar en Coolify:

1. **Conecta tu repositorio Git:**
   - Ve a Coolify y conecta tu repositorio de GitHub
   - Selecciona la rama `main`

2. **Configura el proyecto:**
   - **Build Pack**: Docker
   - **Dockerfile Path**: `./Dockerfile` (desde raíz)
   - **Puerto interno**: Automático (usará variable `$PORT`)

3. **Variables de entorno:**
   ```env
   FLASK_ENV=production
   SECRET_KEY=tu_clave_secreta_muy_segura_aqui
   DATABASE_URL=postgresql://usuario:password@host:5432/nombre_db
   REDIS_URL=redis://host:6379/0
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=tu_email@gmail.com
   MAIL_PASSWORD=tu_app_password
   STRIPE_PUBLIC_KEY=pk_live_...
   STRIPE_SECRET_KEY=sk_live_...
   WTF_CSRF_SECRET_KEY=otra_clave_secreta_para_csrf
   ```

4. **Base de datos:**
   - Crea una base de datos PostgreSQL en Coolify
   - Configura la URL en las variables de entorno

5. **Despliega:**
   - Coolify construirá automáticamente la imagen Docker
   - La aplicación estará disponible en tu dominio Coolify

#### ✅ ¿Por qué Coolify?
- ✅ **Configuración automática** de Docker
- ✅ **Escalado automático**
- ✅ **Backups automáticos**
- ✅ **SSL automático** con Let's Encrypt
- ✅ **Monitoreo integrado**
- ✅ **Deployments con un click**

### Con Docker (Manual)

```bash
# Construir imagen
docker build -t samms-fo .

# Ejecutar contenedor
docker run -p 8095:8095 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=tu_clave \
  samms-fo
```

### Variables de Entorno Requeridas

```env
# Configuración básica
FLASK_ENV=production
SECRET_KEY=tu_clave_secreta_muy_segura

# Base de datos
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis (opcional)
REDIS_URL=redis://host:6379/0

# Correo electrónico
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu@email.com
MAIL_PASSWORD=tu_app_password

# Pagos (Stripe)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...

# Seguridad adicional
WTF_CSRF_SECRET_KEY=clave_csrf_secreta
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto

- **Autor**: Tu Nombre
- **Email**: tu@email.com
- **Proyecto**: [https://github.com/tu-usuario/samms-fo](https://github.com/tu-usuario/samms-fo)

---

⭐ **Si te gusta este proyecto, ¡dale una estrella!**