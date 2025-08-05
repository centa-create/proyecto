from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models.users import Users
from app import db, mail
from flask_mail import Message
import secrets
from datetime import datetime, timedelta

reset_bp = Blueprint('reset', __name__, url_prefix='/reset')

@reset_bp.route('/password', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = Users.query.filter_by(email=email).first()
        if not user:
            flash('No existe una cuenta con ese correo.', 'danger')
            return render_template('reset/request_reset.html')
        token = secrets.token_urlsafe(32)
        user.verification_token = token
        user.token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        reset_url = url_for('reset.reset_password', token=token, _external=True)
        msg = Message('Recupera tu contraseña', recipients=[user.email])
        msg.body = f'Para restablecer tu contraseña, haz clic en el siguiente enlace: {reset_url}\nEste enlace expirará en 1 hora.'
        mail.send(msg)
        flash('Se ha enviado un correo con instrucciones para restablecer tu contraseña.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset/request_reset.html')

@reset_bp.route('/password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = Users.query.filter_by(verification_token=token).first()
    if not user or not user.token_expiry or user.token_expiry < datetime.utcnow():
        flash('El enlace de recuperación es inválido o ha expirado.', 'danger')
        return redirect(url_for('reset.request_reset'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not password or password != confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('reset/reset_password.html', token=token)
        user.set_password(password)
        user.verification_token = None
        user.token_expiry = None
        db.session.commit()
        flash('Contraseña restablecida correctamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset/reset_password.html', token=token)
