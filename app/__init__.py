"""
Módulo principal de la aplicación Flask.

Este módulo configura y crea la aplicación Flask con todas sus extensiones,
blueprints y configuraciones necesarias para el funcionamiento del e-commerce.
"""

import os
from flask import Flask, redirect, render_template, url_for

# Imports de rutas, base de datos y extensiones
from app.db import db
from app.extensions import socketio, login_manager, mail, csrf, cache, limiter
from app.routes.social import social_bp, google_bp, facebook_bp
from app.routes import auth
from app.routes import register
from app.routes import client
from app.routes import notif
from app.routes.catalog import catalog_bp
from app.routes.cart import cart_bp
from app.routes.cart_api import cart_api_bp, webhook_bp
from app.routes.admin import admin_bp
from app.routes.wishlist import wishlist_bp
from app.routes.reviews import reviews_bp
from app.routes.orders import orders_bp
from app.routes.reset import reset_bp


def create_app():
    """Crea y configura la aplicación Flask con todas sus extensiones."""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Registrar blueprints sociales
    app.register_blueprint(google_bp, url_prefix="/login")
    app.register_blueprint(facebook_bp, url_prefix="/login")
    app.register_blueprint(social_bp)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    cache.init_app(app)
    socketio.init_app(app)

    mail.init_app(app)
    # Limiter activado para producción y pruebas
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """Carga un usuario por su ID para Flask-Login."""
        from app.models.users import Users
        return Users.query.get(int(user_id))
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

    @app.route('/')
    def index():
        # Ahora el blueprint client_bp maneja '/'
        return redirect(url_for('client.feed'))

    # Manejo de errores personalizados
    @app.errorhandler(404)
    def not_found_error(_error):
        """Maneja errores 404 - Página no encontrada."""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(_error):
        """Maneja errores 500 - Error interno del servidor."""
        return render_template('errors/500.html'), 500

    return app
 
