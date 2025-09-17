"""
Configuración de la aplicación Flask.

Este módulo contiene la configuración centralizada para diferentes entornos
(desarrollo, producción) usando variables de entorno.
"""

import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Configuración base de la aplicación Flask.

    Utiliza variables de entorno para configuración flexible
    entre diferentes entornos de despliegue.
    """

    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'flaskdb.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad
    SECRET_KEY = os.getenv('SECRET_KEY') or \
        'a2e4c8b7f1d9e3a6c5b8d7f2e1c4a9b6e7d3c2b1f8a6e5d4c3b2a1f9e8d7c6b5'
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY') or SECRET_KEY

    # Correo
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # Stripe (pagos)
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

    # Caché
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))

    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

    # Uploads
    UPLOAD_FOLDER = os.getenv(
        'UPLOAD_FOLDER',
        os.path.join(basedir, 'app', 'static', 'product_images')
    )
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB

    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '10 per minute')
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')

    # Sesión
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
    SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR', os.path.join(basedir, 'instance', 'sessions'))
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora 
