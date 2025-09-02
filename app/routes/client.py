from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
import os, json
from app.models.products import Product
from app.models.support_ticket import SupportTicket

client_bp = Blueprint('client', __name__, url_prefix='/client')

# Crear ticket de soporte
@client_bp.route('/support_ticket/create', methods=['GET', 'POST'])
@login_required
def create_support_ticket():
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        if not subject or not message:
            flash('Asunto y mensaje requeridos.', 'danger')
            return render_template('client/support_ticket_create.html')
        ticket = SupportTicket(user_id=current_user.idUser, subject=subject, message=message)
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket de soporte enviado.', 'success')
        return redirect(url_for('client.list_support_tickets'))
    return render_template('client/support_ticket_create.html')

# Listar tickets del usuario
@client_bp.route('/support_tickets')
@login_required
def list_support_tickets():
    tickets = SupportTicket.query.filter_by(user_id=current_user.idUser).order_by(SupportTicket.created_at.desc()).all()
    return render_template('client/support_ticket_list.html', tickets=tickets)
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
    promociones = Product.query.filter(Product.promo != None).all()
    # Recomendaciones personalizadas por historial de usuario
    recomendaciones_historial = []
    if hasattr(current_user, 'idUser'):
        from app.models.orders import Order, OrderDetail
        user_orders = Order.query.filter_by(user_id=current_user.idUser).all()
        product_ids = set()
        for order in user_orders:
            for detail in order.details:
                product_ids.add(detail.product_id)
        if product_ids:
            # Recomendar productos de la misma categoría que los comprados
            categorias = set([Product.query.get(pid).category_id for pid in product_ids if Product.query.get(pid)])
            recomendaciones_historial = Product.query.filter(Product.category_id.in_(categorias), ~Product.id.in_(product_ids)).limit(8).all()
    # Recomendaciones por productos populares (más vendidos)
    from sqlalchemy import func
    populares = Product.query.join(Product.order_details).group_by(Product.id).order_by(func.count().desc()).limit(8).all()
    # Mezcla destacados y normales para el feed
    products = destacados + [p for p in normales if p not in destacados]
    return render_template('client/feed.html', products=products, promociones=promociones, destacados=destacados, recomendaciones_historial=recomendaciones_historial, populares=populares)

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
