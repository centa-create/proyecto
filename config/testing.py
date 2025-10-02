"""
Configuración específica para entorno de testing.
"""

from . import Config


class TestingConfig(Config):
    """
    Configuración para testing con base de datos en memoria
    y configuraciones que facilitan las pruebas.
    """

    TESTING = True
    DEBUG = True
    FLASK_ENV = "testing"

    # Base de datos SQLite en memoria para tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Logging mínimo durante tests
    LOG_LEVEL = "CRITICAL"

    # Rate limiting deshabilitado en tests
    RATELIMIT_DEFAULT = None

    # Caché en memoria para tests
    CACHE_TYPE = "SimpleCache"

    # Sesión en memoria para tests
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = None

    # Claves de prueba para Stripe
    STRIPE_PUBLISHABLE_KEY = "pk_test_testing_key"  # nosec
    STRIPE_SECRET_KEY = "sk_test_testing_key"  # nosec

    # Configuración de correo deshabilitada en tests
    MAIL_SUPPRESS_SEND = True

    # WTF forms sin CSRF en tests
    WTF_CSRF_ENABLED = False

    # Secret keys fijas para tests
    SECRET_KEY = "test_secret_key_for_testing_only"  # nosec
    WTF_CSRF_SECRET_KEY = "test_csrf_secret_key_for_testing_only"  # nosec
