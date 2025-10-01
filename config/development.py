"""
Configuración específica para entorno de desarrollo.
"""

from . import Config


class DevelopmentConfig(Config):
    """
    Configuración para desarrollo con debugging activado
    y base de datos SQLite local.
    """

    DEBUG = True
    FLASK_ENV = 'development'

    # Base de datos de desarrollo
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/flaskdb_dev.sqlite'

    # Logging más verboso en desarrollo
    LOG_LEVEL = 'DEBUG'

    # Rate limiting menos restrictivo en desarrollo
    RATELIMIT_DEFAULT = '100 per minute'

    # Configuración de Stripe para pruebas (usa claves de prueba)
    STRIPE_PUBLISHABLE_KEY = 'pk_test_...'
    STRIPE_SECRET_KEY = 'sk_test_...'"" 
