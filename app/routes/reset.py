from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models.users import Users
from app import db, mail
from app.extensions import csrf
from flask_mail import Message
import secrets
from datetime import datetime, timedelta

reset_bp = Blueprint('reset', __name__, url_prefix='/reset')

@reset_bp.route('/password', methods=['GET', 'POST'])
@csrf.exempt
def request_reset():
    if request.method == 'POST':
        recovery_method = request.form.get('recovery_method', 'email')

        if recovery_method == 'email':
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

        elif recovery_method == 'phone':
            phone = request.form.get('phone', '').strip()
            if not phone:
                flash('Por favor ingresa un número de teléfono válido.', 'danger')
                return render_template('reset/request_reset.html')

            # Buscar usuario por teléfono
            user = Users.query.filter_by(phone=phone).first()
            if not user:
                flash('No existe una cuenta con ese número de teléfono.', 'danger')
                return render_template('reset/request_reset.html')

            # Generar token para recuperación
            token = secrets.token_urlsafe(32)
            user.verification_token = token
            user.token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            # Enviar SMS real usando Twilio
            sms_body = f'SAMMS.FO - Código de recuperación: {token[:6].upper()}\nIngresa este código para restablecer tu contraseña. Vence en 1 hora.'

            try:
                from twilio.rest import Client
                import os

                # Configuración de Twilio (deberías usar variables de entorno)
                account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid')
                auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'your_auth_token')
                twilio_phone = os.getenv('TWILIO_PHONE_NUMBER', '+1234567890')

                client = Client(account_sid, auth_token)
                message = client.messages.create(
                    body=sms_body,
                    from_=twilio_phone,
                    to=phone
                )
                print(f"SMS enviado exitosamente a {phone}, SID: {message.sid}")
            except ImportError:
                print(f"SMS simulado (Twilio no instalado) enviado a {phone}: {sms_body}")
            except Exception as e:
                print(f"Error enviando SMS a {phone}: {e}")
                # Fallback: podrías enviar por email si el SMS falla

            flash('Se ha enviado un SMS con instrucciones para restablecer tu contraseña.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('reset/request_reset.html')

@reset_bp.route('/password/<token>', methods=['GET', 'POST'])
@csrf.exempt
def reset_password(token):
    user = Users.query.filter_by(verification_token=token).first()
    if not user or not user.token_expiry or user.token_expiry < datetime.utcnow():
        flash('El código de recuperación es inválido o ha expirado.', 'danger')
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
