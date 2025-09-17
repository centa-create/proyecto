"""
Módulo de extensiones Flask.

Este módulo contiene todas las instancias de extensiones de Flask
para evitar importaciones circulares.
"""

"""
Módulo de extensiones Flask.

Este módulo contiene todas las instancias de extensiones de Flask
para evitar importaciones circulares.
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
limiter = Limiter(key_func=get_remote_address, default_limits=["10 per minute"])