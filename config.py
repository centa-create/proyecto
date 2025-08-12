import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'flaskdb.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    SECRET_KEY = os.getenv('SECRET_KEY') or 'a2e4c8b7f1d9e3a6c5b8d7f2e1c4a9b6e7d3c2b1f8a6e5d4c3b2a1f9e8d7c6b5'
    # Configuración de caché
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))