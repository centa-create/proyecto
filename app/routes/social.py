from flask import Blueprint, redirect, url_for, flash
from flask_login import login_user
from flask_dance.contrib.google import make_google_blueprint, google
from app.models.users import Users, UserRole
from app import db
import os

social_bp = Blueprint('social', __name__)

google_bp = make_google_blueprint(
    client_id=os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
    scope=["profile", "email"],
    redirect_url="/social/google/authorized"
)

@social_bp.route('/social/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash('No se pudo autenticar con Google.', 'danger')
        return redirect(url_for('auth.login'))
    info = resp.json()
    email = info.get('email')
    user = Users.query.filter_by(email=email).first()
    if not user:
        user = Users(
            nameUser=info.get('name', email.split('@')[0]),
            email=email,
            passwordUser=os.urandom(32).hex(),
            is_active_db=True,
            role=UserRole.USER
        )
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('Inicio de sesión con Google exitoso.', 'success')
    return redirect(url_for('client.feed'))
