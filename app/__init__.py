from flask_socketio import SocketIO
socketio = SocketIO(cors_allowed_origins="*")
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_caching import Cache
import os


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
cache = Cache()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from flask import redirect, url_for
    @app.route('/')
    def index():
        # Ahora el blueprint client_bp maneja '/'
        return redirect(url_for('client.feed'))

    app = Flask(__name__)
    app.config.from_object('config.Config')
    from app.routes.social import social_bp, google_bp, facebook_bp
    # Registrar blueprints sociales después de crear y configurar la app
    app.register_blueprint(google_bp, url_prefix="/login")
    app.register_blueprint(facebook_bp, url_prefix="/login")
    app.register_blueprint(social_bp)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    cache.init_app(app)
    socketio.init_app(app)

    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    mail.init_app(app)
    # Limiter activado para producción y pruebas
    limiter = Limiter(key_func=get_remote_address, default_limits=["10 per minute"])
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(idUser):
        from .models.users import Users
        return Users.query.get(int(idUser))

    from app.routes import auth
    from app.routes import register
    from app.routes import admin
    from app.routes import client
    from app.routes import notif
    from app.models.notifications import Notification  # Asegura que el modelo esté registrado
    from app.routes.catalog import catalog_bp
    from app.routes.cart import cart_bp
    from app.routes.cart_api import cart_api_bp, webhook_bp
    from app.routes.admin import admin_bp
    from app.routes.wishlist import wishlist_bp
    from app.routes.reviews import reviews_bp
    from app.routes.orders import orders_bp
    from app.routes.reset import reset_bp
    app.register_blueprint(auth.bp)
    app.register_blueprint(register.bp)
    app.register_blueprint(client.client_bp)
    app.register_blueprint(notif.notif_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(cart_api_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reset_bp)

    # Manejo de errores personalizados
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app