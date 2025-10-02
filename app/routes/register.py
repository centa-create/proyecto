"""
Rutas de registro de usuarios.

Este módulo maneja el registro de nuevos usuarios en el sistema.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime, date
import re
import secrets
from email_validator import validate_email, EmailNotValidError
import bcrypt

bp = Blueprint('users', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Maneja el registro de nuevos usuarios."""
    from app import db
    from app.models.users import Users, UserRole
    from app import mail

    if request.method == 'POST':
        nameUser = request.form.get('nameUser', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('passwordUser', '')
        confirm_password = request.form.get('confirm_password', '')
        birthdate_str = request.form.get('birthdate', '')
        terms = request.form.get('terms')

        # Validaciones
        if not all([nameUser, email, password, confirm_password, birthdate_str, terms]):
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('register.html')
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError:
            flash('Correo electrónico no válido.', 'danger')
            return render_template('register.html')
        if Users.query.filter_by(email=email).first():
            flash('El correo ya está registrado.', 'danger')
            return render_template('register.html')
        if phone and Users.query.filter_by(phone=phone).first():
            flash('El número de teléfono ya está registrado.', 'danger')
            return render_template('register.html')
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'\d', password):
            flash('La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número.', 'danger')
            return render_template('register.html')
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register.html')
        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Fecha de nacimiento inválida.', 'danger')
            return render_template('register.html')
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        if age < 18:
            flash('Debes ser mayor de 18 años.', 'danger')
            return render_template('register.html')
        if not terms:
            flash('Debes aceptar los términos y condiciones.', 'danger')
            return render_template('register.html')
        # Hash de contraseña
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Token de verificación
        token = secrets.token_urlsafe(32)
        # Si es el primer usuario, será admin; si no, user normal
        if Users.query.count() == 0:
            rol = UserRole.ADMIN
        else:
            rol = UserRole.USER
        user = Users(
            nameUser=nameUser,
            email=email,
            phone=phone if phone else None,
            password_user=hashed,
            birthdate=birthdate,
            is_active_db=False,  # Usuario inactivo hasta verificar email
            verification_token=token,
            accepted_terms=True,
            role=rol
        )
        db.session.add(user)
        db.session.commit()

        # Enviar email de verificación
        try:
            from flask_mail import Message
            verify_url = url_for('users.verify', token=token, _external=True)
            msg = Message('Verifica tu cuenta',
                          sender=current_app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[email])
            msg.body = f'Hola {nameUser},\n\nPara activar tu cuenta, haz clic en el siguiente enlace:\n{verify_url}\n\nSi no solicitaste esta cuenta, ignora este mensaje.'
            msg.html = f'<p>Hola {nameUser},</p><p>Para activar tu cuenta, haz clic en el siguiente enlace:</p><p><a href="{verify_url}">Verificar cuenta</a></p><p>Si no solicitaste esta cuenta, ignora este mensaje.</p>'
            mail.send(msg)
            print(f"Email enviado a: {email}")
        except Exception as e:
            print(f"Error enviando email: {e}")
            # Para desarrollo: mostrar URL en consola
            verify_url = url_for('users.verify', token=token, _external=True)
            print(f"URL de verificación: {verify_url}")
            flash('Error enviando email. Revisa la consola para la URL de verificación.', 'warning')

        flash('Registro exitoso. Revisa tu correo electrónico para verificar tu cuenta.', 'success')
        return render_template('register_success.html')
    return render_template('register.html')

@bp.route('/verify/<token>')
def verify(token):
    """Verifica la cuenta de usuario usando el token de verificación."""
    from app import db
    from app.models.users import Users

    user = Users.query.filter_by(verification_token=token).first()
    if not user or user.is_active_db:
        return render_template('verify_error.html')
    user.is_active_db = True
    user.verification_token = None
    db.session.commit()
    return render_template('verify_success.html')
