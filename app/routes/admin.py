

from app.forms import ProductForm
from app.forms import CategoryForm
"""
Bloques de importación organizados: estándar, externas, internas
"""
# --- Estándar ---
import os
import csv
import secrets
from io import StringIO
from datetime import datetime, timedelta

# --- Externas ---
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask_mail import Message
from sqlalchemy import func

# --- Internas (app) ---
from app import db, mail
from app.models.audit_log import AuditLog
from app.models.support_ticket import SupportTicket
from app.models.coupons import Coupon
from app.models.products import Product, Category
from app.models.returns import ReturnRequest
from app.models.orders import Order, OrderDetail
from app.models.users import Users, UserRole
from app.models.notifications import Notification
from app.models.reviews import Review
from app.models.banner import Banner
from app.models.admin_notification import AdminNotification
from app.models.store_config import StoreConfig

from functools import wraps

# --- Decorador para admins ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('Acceso denegado: solo administradores.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# --- Blueprint ---


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- DESCUENTOS ---
@admin_bp.route('/products/<int:product_id>/discount', methods=['GET', 'POST'])
@login_required
@admin_required
def add_discount(product_id):
    product = Product.query.get_or_404(product_id)
    from app.forms import DiscountForm
    form = DiscountForm()
    if form.validate_on_submit():
        discount = form.discount.data
        product.discount = discount
        db.session.commit()
        flash('Descuento asignado al producto.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_discount.html', product=product, form=form)

# --- PROMOCIONES ---
@admin_bp.route('/products/<int:product_id>/promo', methods=['GET', 'POST'])
@login_required
@admin_required
def add_promo(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        promo = request.form.get('promo', '').strip()
        product.promo = promo
        db.session.commit()
        flash('Promoción asignada al producto.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_promo.html', product=product)

# --- Decorador para admins ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('Acceso denegado: solo administradores.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Utilidad para log de acciones admin ---
def log_admin_action(admin_id, action, target_type, target_id=None, details=None):
    log = AuditLog(admin_id=admin_id, action=action, target_type=target_type, target_id=target_id, details=details)
    db.session.add(log)
    db.session.commit()

# --- CONFIGURACIÓN AVANZADA DE LA TIENDA ---
@admin_bp.route('/store_config', methods=['GET', 'POST'])
@login_required
@admin_required
def store_config():
    keys = ['nombre_tienda', 'email_contacto', 'horario', 'mensaje_bienvenida', 'color_principal']
    if request.method == 'POST':
        for key in keys:
            value = request.form.get(key, '').strip()
            config = StoreConfig.query.filter_by(key=key).first()
            if config:
                config.value = value
            else:
                db.session.add(StoreConfig(key=key, value=value))
        db.session.commit()
        flash('Configuración actualizada.', 'success')
        return redirect(url_for('admin.store_config'))
    config_dict = {c.key: c.value for c in StoreConfig.query.all()}
    return render_template('admin/store_config.html', config=config_dict, keys=keys)
"""
Bloques de importación organizados: estándar, externas, internas
"""
# --- Estándar ---
import os
import csv
import secrets
from io import StringIO
from datetime import datetime, timedelta

# --- Externas ---
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask_mail import Message
from sqlalchemy import func

# --- Internas (app) ---
from app import db, mail
from app.models.audit_log import AuditLog
from app.models.support_ticket import SupportTicket
from app.models.coupons import Coupon
from app.models.products import Product, Category
from app.models.returns import ReturnRequest
from app.models.orders import Order, OrderDetail
from app.models.users import Users, UserRole
from app.models.notifications import Notification
from app.models.reviews import Review
from app.models.banner import Banner
from app.models.admin_notification import AdminNotification
from app.models.store_config import StoreConfig
from functools import wraps

from app.models.admin_notification import AdminNotification
# --- NOTIFICACIONES INTERNAS PARA ADMINS ---
@admin_bp.route('/notifications')
@login_required
@admin_required
def admin_notifications():
    notifs = AdminNotification.query.filter((AdminNotification.admin_id == None) | (AdminNotification.admin_id == current_user.idUser)).order_by(AdminNotification.created_at.desc()).all()
    return render_template('admin/admin_notifications.html', notifications=notifs)

@admin_bp.route('/notifications/read/<int:notif_id>', methods=['POST'])
@login_required
@admin_required
def mark_notification_read(notif_id):
    notif = AdminNotification.query.get_or_404(notif_id)
    notif.is_read = True
    db.session.commit()
    return redirect(url_for('admin.admin_notifications'))

# Ruta para crear notificaciones de prueba (puedes eliminarla luego)
@admin_bp.route('/notifications/create', methods=['POST'])
@login_required
@admin_required
def create_admin_notification():
    msg = request.form.get('message', '').strip()
    notif = AdminNotification(message=msg)
    db.session.add(notif)
    db.session.commit()
    flash('Notificación creada.', 'success')
    return redirect(url_for('admin.admin_notifications'))
import csv
from io import StringIO
from flask import Response
# --- EXPORTACIÓN DE DATOS ---
@admin_bp.route('/export/users')
@login_required
@admin_required
def export_users():
    users = Users.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Nombre', 'Email', 'Rol', 'Activo', 'Fecha registro'])
    for u in users:
        cw.writerow([u.idUser, u.nameUser, u.email, u.role, u.is_active_db, u.created_at])
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=usuarios.csv"})

@admin_bp.route('/export/products')
@login_required
@admin_required
def export_products():
    products = Product.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Nombre', 'Precio', 'Stock', 'Categoría', 'Fecha creación'])
    for p in products:
        cw.writerow([p.id, p.name, p.price, p.stock, p.category_id, p.created_at])
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=productos.csv"})

@admin_bp.route('/export/orders')
@login_required
@admin_required
def export_orders():
    orders = Order.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Usuario', 'Total', 'Estado', 'Fecha'])
    for o in orders:
        cw.writerow([o.id, o.user_id, o.total, o.status, o.created_at])
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=pedidos.csv"})
from app.models.banner import Banner
# --- BANNERS Y CONTENIDO DESTACADO ---
@admin_bp.route('/banners')
@login_required
@admin_required
def banners():
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('admin/banners.html', banners=banners)

@admin_bp.route('/banners/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_banner():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        link = request.form.get('link', '').strip()
        active = bool(request.form.get('active'))
        image_file = request.files.get('image')
        if not title or not image_file or not image_file.filename:
            flash('Título e imagen son obligatorios.', 'danger')
            return render_template('admin/banner_form.html', banner=None)
        filename = secure_filename(image_file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static/banners')
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, filename)
        image_file.save(image_path)
        banner = Banner(title=title, image=filename, link=link, active=active)
        db.session.add(banner)
        db.session.commit()
        flash('Banner creado.', 'success')
        return redirect(url_for('admin.banners'))
    return render_template('admin/banner_form.html', banner=None)

@admin_bp.route('/banners/edit/<int:banner_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    if request.method == 'POST':
        banner.title = request.form.get('title', banner.title).strip()
        banner.link = request.form.get('link', banner.link).strip()
        banner.active = bool(request.form.get('active'))
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/banners')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            banner.image = filename
        db.session.commit()
        flash('Banner actualizado.', 'success')
        return redirect(url_for('admin.banners'))
    return render_template('admin/banner_form.html', banner=banner)

@admin_bp.route('/banners/toggle/<int:banner_id>', methods=['POST'])
@login_required
@admin_required
def toggle_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    banner.active = not banner.active
    db.session.commit()
    flash('Estado del banner actualizado.', 'info')
    return redirect(url_for('admin.banners'))

@admin_bp.route('/banners/delete/<int:banner_id>', methods=['POST'])
@login_required
@admin_required
def delete_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    db.session.delete(banner)
    db.session.commit()
    flash('Banner eliminado.', 'danger')
    return redirect(url_for('admin.banners'))
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from app import db, mail
from app.models.audit_log import AuditLog
from app.models.support_ticket import SupportTicket
from app.models.coupons import Coupon
from app.models.products import Product, Category
from app.models.returns import ReturnRequest
from app.models.orders import Order, OrderDetail
from app.models.users import Users, UserRole
from app.models.notifications import Notification
from app.models.reviews import Review
from sqlalchemy import func
from flask_mail import Message
import secrets
from datetime import datetime, timedelta
import os



# Decorador para admins

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('Acceso denegado: solo administradores.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Utilidad para log de acciones admin

def log_admin_action(admin_id, action, target_type, target_id=None, details=None):
    log = AuditLog(admin_id=admin_id, action=action, target_type=target_type, target_id=target_id, details=details)
    db.session.add(log)
    db.session.commit()

# --- SOPORTE Y TICKETS ---
@admin_bp.route('/support_tickets')
@login_required
@admin_required
def support_tickets():
    tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).all()
    for t in tickets:
        t.user = Users.query.get(t.user_id)
        t.assigned_admin = Users.query.get(t.assigned_admin_id) if t.assigned_admin_id else None
    return render_template('admin/support_tickets.html', tickets=tickets)

@admin_bp.route('/support_tickets/<int:ticket_id>')
@login_required
@admin_required
def view_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    ticket.user = Users.query.get(ticket.user_id)
    ticket.assigned_admin = Users.query.get(ticket.assigned_admin_id) if ticket.assigned_admin_id else None
    return render_template('admin/view_ticket.html', ticket=ticket)

@admin_bp.route('/support_tickets/assign/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def assign_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    ticket.assigned_admin_id = current_user.idUser
    ticket.status = 'en_proceso'
    db.session.commit()
    flash('Ticket asignado a ti.', 'info')
    return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))

@admin_bp.route('/support_tickets/respond/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def respond_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    response = request.form.get('response', '').strip()
    if not response:
        flash('Respuesta requerida.', 'danger')
        return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))
    # Aquí podrías guardar la respuesta en una tabla de mensajes/respuestas si se desea historial
    ticket.status = 'en_proceso'
    db.session.commit()
    flash('Respuesta enviada (simulada).', 'success')
    return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))

@admin_bp.route('/support_tickets/close/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def close_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    ticket.status = 'cerrado'
    db.session.commit()
    flash('Ticket cerrado.', 'success')
    return redirect(url_for('admin.support_tickets'))

# --- AUDITORÍA ---
@admin_bp.route('/audit')
@login_required
@admin_required
def audit():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()
    for log in logs:
        log.admin = Users.query.get(log.admin_id)
    return render_template('admin/audit.html', logs=logs)

# --- CUPONES ---
@admin_bp.route('/coupons')
@login_required
@admin_required
def coupons():
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/coupons.html', coupons=coupons, products=products, categories=categories)

@admin_bp.route('/coupons/add', methods=['POST'])
@login_required
@admin_required
def add_coupon():
    code = request.form.get('code', '').strip().upper()
    description = request.form.get('description', '').strip()
    discount_percent = float(request.form.get('discount_percent', 0))
    valid_from = request.form.get('valid_from')
    valid_to = request.form.get('valid_to')
    usage_limit = request.form.get('usage_limit') or None
    product_id = request.form.get('product_id') or None
    category_id = request.form.get('category_id') or None
    coupon = Coupon(
        code=code,
        description=description,
        discount_percent=discount_percent,
        valid_from=valid_from,
        valid_to=valid_to,
        usage_limit=int(usage_limit) if usage_limit else None,
        product_id=int(product_id) if product_id else None,
        category_id=int(category_id) if category_id else None
    )
    db.session.add(coupon)
    db.session.commit()
    flash('Cupón creado.', 'success')
    return redirect(url_for('admin.coupons'))

@admin_bp.route('/coupons/toggle/<int:coupon_id>', methods=['POST'])
@login_required
@admin_required
def toggle_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    coupon.active = not coupon.active
    db.session.commit()
    flash('Estado del cupón actualizado.', 'info')
    return redirect(url_for('admin.coupons'))

@admin_bp.route('/coupons/delete/<int:coupon_id>', methods=['POST'])
@login_required
@admin_required
def delete_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    db.session.delete(coupon)
    db.session.commit()
    flash('Cupón eliminado.', 'danger')
    return redirect(url_for('admin.coupons'))

# --- DEVOLUCIONES ---
@admin_bp.route('/returns')
@login_required
@admin_required
def returns():
    returns = ReturnRequest.query.order_by(ReturnRequest.created_at.desc()).all()
    for r in returns:
        r.user = Users.query.get(r.user_id)
        r.order = Order.query.get(r.order_id)
    return render_template('admin/returns.html', returns=returns)

@admin_bp.route('/returns/approve/<int:return_id>', methods=['POST'])
@login_required
@admin_required
def approve_return(return_id):
    r = ReturnRequest.query.get_or_404(return_id)
    r.status = 'aprobado'
    r.processed_at = datetime.utcnow()
    db.session.commit()
    flash('Devolución aprobada.', 'success')
    return redirect(url_for('admin.returns'))

@admin_bp.route('/returns/reject/<int:return_id>', methods=['POST'])
@login_required
@admin_required
def reject_return(return_id):
    r = ReturnRequest.query.get_or_404(return_id)
    r.status = 'rechazado'
    r.processed_at = datetime.utcnow()
    db.session.commit()
    flash('Devolución rechazada.', 'danger')
    return redirect(url_for('admin.returns'))

@admin_bp.route('/returns/refund/<int:return_id>', methods=['POST'])
@login_required
@admin_required
def refund_return(return_id):
    r = ReturnRequest.query.get_or_404(return_id)
    try:
        amount = float(request.form.get('refund_amount', 0))
        r.status = 'reembolsado'
        r.refund_amount = amount
        r.processed_at = datetime.utcnow()
        db.session.commit()
        flash(f'Reembolso de ${amount:.2f} registrado.', 'info')
    except Exception:
        flash('Error al registrar el reembolso.', 'danger')
    return redirect(url_for('admin.returns'))

# --- PEDIDOS ---
@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    for order in orders:
        order.user = Users.query.get(order.user_id)
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status', order.status)
    order.status = new_status
    db.session.commit()
    flash(f'Estado del pedido {order.id} actualizado a {new_status}.', 'success')
    return redirect(url_for('admin.orders'))

# --- USUARIOS ---
@admin_bp.route('/users/reset_password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_reset_password(user_id):
    user = Users.query.get_or_404(user_id)
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    user.token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    reset_url = url_for('reset.reset_password', token=token, _external=True)
    msg = Message('Recupera tu contraseña', recipients=[user.email])
    msg.body = f'Un administrador ha solicitado el restablecimiento de tu contraseña. Haz clic en el siguiente enlace: {reset_url}\nEste enlace expirará en 1 hora.'
    mail.send(msg)
    flash(f'Se ha enviado un correo de restablecimiento a {user.email}.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/block/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def block_user(user_id):
    log_admin_action(current_user.idUser, 'bloquear', 'usuario', user_id, f'Bloqueado por admin')
    user = Users.query.get_or_404(user_id)
    if user.role == UserRole.ADMIN:
        flash('No se puede bloquear a otro administrador.', 'danger')
        return redirect(url_for('admin.dashboard'))
    user.is_blocked = True
    db.session.commit()
    flash(f'Usuario {user.nameUser} bloqueado.', 'warning')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/unblock/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def unblock_user(user_id):
    log_admin_action(current_user.idUser, 'desbloquear', 'usuario', user_id, f'Desbloqueado por admin')
    user = Users.query.get_or_404(user_id)
    user.is_blocked = False
    db.session.commit()
    flash(f'Usuario {user.nameUser} desbloqueado.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/<int:user_id>/orders')
@login_required
@admin_required
def user_orders(user_id):
    user = Users.query.get_or_404(user_id)
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    for order in orders:
        order.details = OrderDetail.query.filter_by(order_id=order.id).all()
    return render_template('admin/user_orders.html', user=user, orders=orders)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    if user.role == UserRole.ADMIN:
        flash('No se puede eliminar a otro administrador.', 'danger')
        return redirect(url_for('admin.dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado correctamente.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/make_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    log_admin_action(current_user.idUser, 'hacer_admin', 'usuario', user_id, f'Ascendido a admin')
    user = Users.query.get_or_404(user_id)
    user.role = UserRole.ADMIN
    db.session.commit()
    flash(f'El usuario {user.nameUser} ahora es administrador.', 'success')
    return redirect(url_for('admin.dashboard'))

# --- DASHBOARD ---
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    q = request.args.get('q', '').strip()
    query = Users.query
    if q:
        query = query.filter((Users.nameUser.ilike(f'%{q}%')) | (Users.email.ilike(f'%{q}%')))
    usuarios = query.all()
    usuarios_registrados = Users.query.count()
    estadisticas = 87
    notificaciones = Notification.query.count()
    return render_template('admin/dashboard.html', usuarios=usuarios, usuarios_registrados=usuarios_registrados, estadisticas=estadisticas, notificaciones=notificaciones, q=q)

# --- PRODUCTOS Y CATEGORÍAS ---
@admin_bp.route('/products')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/products.html', products=products)

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    """Agrega un nuevo producto con validación y manejo de errores."""
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        try:
            name = form.name.data.strip()
            description = form.description.data.strip()
            price = float(form.price.data)
            stock = int(form.stock.data)
            size = form.size.data.strip()
            color = form.color.data.strip()
            category_id = form.category_id.data
            image_filename = None
            image_file = form.image.data
            if image_file and hasattr(image_file, 'filename') and image_file.filename:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(current_app.root_path, current_app.config.get('UPLOAD_FOLDER', 'static/product_images'))
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, filename)
                image_file.save(image_path)
                image_filename = filename
            product = Product(name=name, description=description, price=price, stock=stock, image=image_filename, size=size, color=color, category_id=category_id)
            db.session.add(product)
            db.session.commit()
            log_admin_action(current_user.idUser, 'crear', 'producto', product.id, f'Producto: {name}')
            flash('Producto agregado correctamente.', 'success')
            return redirect(url_for('admin.products'))
        except ValueError as e:
            current_app.logger.error(f'Error en add_product: {e}')
            flash('Error en los datos numéricos.', 'danger')
            return redirect(url_for('admin.add_product'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error inesperado: {e}')
            flash('Error al agregar producto.', 'danger')
    return render_template('admin/add_product.html', form=form)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    """Edita un producto existente con validación y manejo de errores."""
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        try:
            product.name = request.form.get('name', product.name).strip()
            product.description = request.form.get('description', product.description).strip()
            product.price = float(request.form.get('price') or product.price)
            product.stock = int(request.form.get('stock') or product.stock)
            product.size = request.form.get('size', product.size).strip()
            product.color = request.form.get('color', product.color).strip()
            product.category_id = int(request.form.get('category_id') or product.category_id)
            if product.price <= 0 or product.stock < 0 or not Category.query.get(product.category_id):
                flash('Datos inválidos: precio > 0, stock >= 0 y categoría válida.', 'danger')
                return redirect(url_for('admin.edit_product', product_id=product_id))
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(current_app.root_path, current_app.config.get('UPLOAD_FOLDER', 'static/product_images'))
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, filename)
                image_file.save(image_path)
                product.image = filename
            db.session.commit()
            log_admin_action(current_user.idUser, 'editar', 'producto', product.id, f'Editado: {product.name}')
            flash('Producto actualizado.', 'success')
            return redirect(url_for('admin.products'))
        except ValueError as e:
            current_app.logger.error(f'Error en edit_product: {e}')
            flash('Error en los datos numéricos.', 'danger')
            return redirect(url_for('admin.edit_product', product_id=product_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error inesperado: {e}')
            flash('Error al editar producto.', 'danger')
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    log_admin_action(current_user.idUser, 'eliminar', 'producto', product_id, f'Eliminado por admin')
    if request.form.get('confirm_delete') != 'yes':
        flash('Confirmación requerida para eliminar.', 'danger')
        return redirect(url_for('admin.products'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Producto eliminado.', 'info')
    return redirect(url_for('admin.products'))

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        description = form.description.data.strip()
        if Category.query.filter_by(name=name).first():
            flash('El nombre de la categoría ya existe.', 'danger')
            return redirect(url_for('admin.add_category'))
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        log_admin_action(current_user.idUser, 'crear', 'categoria', category.id, f'Categoría: {name}')
        flash('Categoría agregada.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/add_category.html', form=form)

@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        new_name = request.form.get('name', category.name).strip()
        if Category.query.filter(Category.name == new_name, Category.id != category_id).first():
            flash('Nombre debe ser único.', 'danger')
            return redirect(url_for('admin.edit_category', category_id=category_id))
        category.name = new_name
        category.description = request.form.get('description', category.description).strip()
        db.session.commit()
        log_admin_action(current_user.idUser, 'editar', 'categoria', category.id, f'Editada: {category.name}')
        flash('Categoría actualizada.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/edit_category.html', category=category)

@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    log_admin_action(current_user.idUser, 'eliminar', 'categoria', category_id, f'Eliminada por admin')
    if request.form.get('confirm_delete') != 'yes':
        flash('Confirmación requerida para eliminar.', 'danger')
        return redirect(url_for('admin.categories'))
    category = Category.query.get_or_404(category_id)
    if Product.query.filter_by(category_id=category_id).first():
        flash('No se puede eliminar: hay productos asociados.', 'danger')
        return redirect(url_for('admin.categories'))
    db.session.delete(category)
    db.session.commit()
    flash('Categoría eliminada.', 'info')
    return redirect(url_for('admin.categories'))

# --- INVENTARIO ---
@admin_bp.route('/inventory', methods=['GET'])
@login_required
@admin_required
def inventory():
    products = Product.query.order_by(Product.stock.asc()).all()
    return render_template('admin/inventory.html', products=products)

@admin_bp.route('/inventory/update/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def update_stock(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        new_stock = int(request.form.get('stock', product.stock))
        if new_stock < 0:
            flash('El stock no puede ser negativo.', 'danger')
            return redirect(url_for('admin.inventory'))
        product.stock = new_stock
        db.session.commit()
        flash(f'Stock de "{product.name}" actualizado a {new_stock}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar el stock.', 'danger')
    return redirect(url_for('admin.inventory'))

# --- RESEÑAS ---
@admin_bp.route('/reviews/moderate')
@login_required
@admin_required
def moderate_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/moderate_reviews.html', reviews=reviews)

@admin_bp.route('/reviews/approve/<int:review_id>', methods=['POST'])
@login_required
@admin_required
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.aprobada = True
    db.session.commit()
    flash('Reseña aprobada.', 'success')
    return redirect(url_for('admin.moderate_reviews'))

@admin_bp.route('/reviews/reject/<int:review_id>', methods=['POST'])
@login_required
@admin_required
def reject_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Reseña eliminada.', 'info')
    return redirect(url_for('admin.moderate_reviews'))

# --- REPORTES ---
@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    total_ventas = db.session.query(func.sum(Order.total)).scalar() or 0
    ventas_por_producto = db.session.query(
        Product.name,
        func.sum(OrderDetail.quantity).label('cantidad'),
        func.sum(OrderDetail.price * OrderDetail.quantity).label('total')
    ).join(Product, OrderDetail.product_id == Product.id).group_by(OrderDetail.product_id, Product.name).all()
    ventas_por_fecha = db.session.query(
        func.date(Order.created_at).label('fecha'),
        func.sum(Order.total).label('total')
    ).group_by('fecha').all()
    ventas_por_fecha = [(str(fecha), total) for fecha, total in ventas_por_fecha]
    return render_template('admin/reports.html',
                           total_ventas=total_ventas,
                           ventas_por_producto=ventas_por_producto,
                           ventas_por_fecha=ventas_por_fecha)

# --- API DE VENTAS POR DÍA ---
@admin_bp.route('/api/sales_by_day')
@login_required
@admin_required
def api_sales_by_day():
    ventas_por_fecha = db.session.query(
        func.date(Order.created_at).label('fecha'),
        func.sum(Order.total).label('total')
    ).group_by('fecha').order_by('fecha').all()
    data = {
        'labels': [str(fecha) for fecha, _ in ventas_por_fecha],
        'totals': [float(total) for _, total in ventas_por_fecha]
    }
    return data