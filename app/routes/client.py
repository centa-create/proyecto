
from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename
from app import db
import os, json
from app.models.products import Product

client_bp = Blueprint('client', __name__, url_prefix='/client')
@client_bp.route('/social')
@login_required
def social():
    return render_template('client/social.html')

# FEED tipo marketplace
@client_bp.route('/feed')
@login_required
def feed():
    # Productos destacados primero, luego el resto
    destacados = Product.query.filter_by(destacado=True).all()
    normales = Product.query.filter_by(destacado=False).all()
    # Promociones: productos con promo no nulo
    promociones = Product.query.filter(Product.promo != None).all()
    # Mezcla destacados y normales para el feed
    products = destacados + [p for p in normales if p not in destacados]
    return render_template('client/feed.html', products=products, promociones=promociones, destacados=destacados)

@client_bp.route('/dashboard')
@login_required
def dashboard():
    actividad = [
        {'fecha': '2025-07-01', 'descripcion': 'Inicio de sesión exitoso'},
        {'fecha': '2025-06-30', 'descripcion': 'Actualizó su perfil'},
        {'fecha': '2025-06-29', 'descripcion': 'Registró una nueva cuenta'},
    ]
    es_primera_vez = getattr(current_user, 'first_login', False)
    return render_template('client/dashboard.html', actividad=actividad, es_primera_vez=es_primera_vez)

# Edición de perfil y foto
@client_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('nameUser', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('passwordUser', '')
        file = request.files.get('profile_pic')
        user = current_user
        # Validación de email único
        if email and email != user.email:
            from app.models.users import Users
            if Users.query.filter_by(email=email).first():
                flash('El correo ya está registrado por otro usuario.', 'danger')
                return redirect(url_for('client.profile'))
            user.email = email
        if name:
            user.nameUser = name
        if password:
            import bcrypt
            user.passwordUser = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if file and file.filename:
            filename = secure_filename(f"{user.idUser}_" + file.filename)
            path = os.path.join(current_app.root_path, 'static', 'profile_pics', filename)
            file.save(path)
            user.profile_pic = filename
        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('client.profile'))
    return render_template('client/profile.html')

# Descarga de datos personales
@client_bp.route('/download_data')
@login_required
def download_data():
    user = current_user
    data = {
        'id': user.idUser,
        'nombre': user.nameUser,
        'email': user.email,
        'fecha_nacimiento': str(user.birthdate),
        'rol': getattr(user.role, 'name', str(user.role)),
    }
    file_path = os.path.join(current_app.root_path, 'static', f'user_{user.idUser}_data.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return send_file(file_path, as_attachment=True)
