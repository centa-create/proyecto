"""
Módulo de extensiones de Flask.

Este módulo configura todas las extensiones utilizadas por la aplicación Flask,
incluyendo caching, rate limiting, autenticación, correo, CSRF y WebSocket.
"""

from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO

# Extensiones de Flask
socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
cache = Cache()
limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per minute"])
