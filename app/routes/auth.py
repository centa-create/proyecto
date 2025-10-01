"""
Módulo de rutas de autenticación.

Este módulo maneja todas las rutas relacionadas con la autenticación
de usuarios: login, logout y dashboard.
"""

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.forms import LoginForm
from app.models.users import UserRole, Users

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión de usuarios."""
    if current_user.is_authenticated:
        # Si ya está autenticado, redirigir según rol
        if current_user.role == UserRole.ADMIN:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('client.feed'))  # Se mantiene para consistencia,
        # pero la navbar ya apunta a '/'

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            if user.is_blocked:
                flash('Tu cuenta ha sido bloqueada por un administrador.', 'danger')
                return redirect(url_for('auth.login'))
            if not user.is_active:
                flash('Tu cuenta no está activada. Revisa tu correo electrónico.', 'warning')
                return redirect(url_for('auth.login'))

            login_user(user)
            flash("¡Inicio de sesión exitoso!", "success")

            # Redirigir según rol
            if user.role == UserRole.ADMIN:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('client.feed'))  # Se mantiene para consistencia,
            # pero la navbar ya apunta a '/'
        else:
            flash('Credenciales inválidas. Intenta de nuevo.', 'danger')

    return render_template("login.html", form=form)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Redirige al dashboard apropiado según el rol del usuario."""
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
    """Cierra la sesión del usuario actual."""
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))
