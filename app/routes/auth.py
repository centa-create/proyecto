from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.users import Users
import bcrypt

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        passwordUser = request.form.get('passwordUser', '')
        user = Users.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(passwordUser.encode('utf-8'), user.passwordUser.encode('utf-8')):
            if user.is_blocked:
                flash('Tu cuenta ha sido bloqueada por un administrador.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            flash("¡Inicio de sesión exitoso!", "success")
            # Redirigir a dashboard admin si es admin, si no al FEED tipo marketplace
            role = getattr(user, 'role', None)
            if role is not None:
                role_str = str(role.value) if hasattr(role, 'value') else str(role)
                if role_str.lower() == 'admin':
                    return redirect(url_for('admin.dashboard'))
            return redirect(url_for('client.feed'))
        else:
            flash('Credenciales inválidas. Intenta de nuevo.', 'danger')
    if current_user.is_authenticated:
        # Si ya está autenticado, mándalo al feed si es user, o admin dashboard si es admin
        role = getattr(current_user, 'role', None)
        if role is not None:
            role_str = str(role.value) if hasattr(role, 'value') else str(role)
            if role_str.lower() == 'admin':
                return redirect(url_for('admin.dashboard'))
        return redirect(url_for('client.feed'))
    return render_template("login.html")

@bp.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    role = getattr(user, 'role', None)
    if role is not None:
        role_str = str(role.value) if hasattr(role, 'value') else str(role)
        if role_str.lower() == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role_str.lower() == 'user':
            return redirect(url_for('client.dashboard'))
        # Puedes agregar más roles aquí si los tienes
    # Si el usuario no tiene un rol válido, muestra error y cierra sesión
    flash('Tu cuenta no tiene un rol válido. Contacta al administrador.', 'danger')
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))
