"""
Configuración específica para entorno de producción.
"""

import os
from . import Config


class ProductionConfig(Config):
    """
    Configuración para producción con seguridad reforzada
    y optimizaciones de rendimiento.
    """

    DEBUG = False
    FLASK_ENV = 'production'
    TESTING = False

    # Base de datos PostgreSQL/MySQL para producción
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'postgresql://user:password@localhost:5432/prod_db'

    # Logging estructurado para producción
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/var/log/flask_app/app.log'

    # Rate limiting más restrictivo en producción
    RATELIMIT_DEFAULT = '10 per minute'
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Caché Redis para producción
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

    # Configuración de Stripe para producción (claves reales)
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

    # Configuración de correo para producción
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # Sesión segura para producción
    SESSION_TYPE = 'redis'
    SESSION_REDIS = os.getenv('REDIS_URL', 'redis://localhost:6379/2')

    # Configuración de seguridad adicional
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY')

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY es requerida en producción")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY es requerida en producción")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY es requerida en producción")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY es requerida en producción")""  
""  
