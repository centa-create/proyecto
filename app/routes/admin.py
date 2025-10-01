

"""
Rutas de administración para la aplicación Flask.

Este módulo contiene todas las rutas relacionadas con la administración
del sistema, incluyendo gestión de productos, usuarios, pedidos, etc.
"""

import os
import csv
import secrets
from datetime import datetime, timedelta
from functools import wraps
from io import StringIO

from flask import (
    Blueprint, Response, current_app, flash, redirect,
    render_template, request, url_for
)
from flask_login import current_user, login_required
from flask_mail import Message
from sqlalchemy import func
from werkzeug.utils import secure_filename

from app import db, mail
from app.extensions import csrf
from app.forms import CategoryForm, DiscountForm, ProductForm, CouponForm
from app.models.admin_notification import AdminNotification
from app.models.audit_log import AuditLog
from app.models.banner import Banner
from app.models.coupons import Coupon
from app.models.notifications import Notification
from app.models.orders import Order, OrderDetail
from app.models.products import Category, Product
from app.models.returns import ReturnRequest
from app.models.reviews import Review
from app.models.store_config import StoreConfig
from app.models.support_ticket import SupportTicket
from app.models.users import UserRole, Users
from app.models.wishlist import Wishlist

def admin_required(view_func):
    """Decorador que verifica si el usuario actual es administrador."""
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('Acceso denegado: solo administradores.', 'danger')
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return decorated_function


def log_admin_action(admin_id, action, target_type, target_id=None, details=None):
    """Registra una acción administrativa en el log de auditoría."""
    log_entry = AuditLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    db.session.add(log_entry)
    db.session.commit()


# --- Blueprint ---


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- DESCUENTOS ---
@admin_bp.route('/products/<int:product_id>/discount', methods=['GET', 'POST'])
@login_required
@admin_required
def add_discount(product_id):
    """Agrega un descuento a un producto específico."""
    product_obj = Product.query.get_or_404(product_id)
    form = DiscountForm()
    if form.validate_on_submit():
        discount_value = form.discount.data
        product_obj.discount = discount_value
        db.session.commit()
        flash('Descuento asignado al producto.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_discount.html', product=product_obj, form=form)


# --- PROMOCIONES ---
@admin_bp.route('/products/<int:product_id>/promo', methods=['GET', 'POST'])
@login_required
@admin_required
def add_promo(product_id):
    """Agrega una promoción a un producto específico."""
    product_obj = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        promo_text = request.form.get('promo', '').strip()
        product_obj.promo = promo_text
        db.session.commit()
        flash('Promoción asignada al producto.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_promo.html', product=product_obj)


# --- CONFIGURACIÓN AVANZADA DE LA TIENDA ---
@admin_bp.route('/store_config', methods=['GET', 'POST'])
@login_required
@admin_required
def store_config():
    """Gestiona la configuración avanzada de la tienda."""
    keys = ['nombre_tienda', 'email_contacto', 'horario', 'mensaje_bienvenida', 'color_principal']
    if request.method == 'POST':
        for key in keys:
            value = request.form.get(key, '').strip()
            config_obj = StoreConfig.query.filter_by(key=key).first()
            if config_obj:
                config_obj.value = value
            else:
                db.session.add(StoreConfig(key=key, value=value))
        db.session.commit()
        flash('Configuración actualizada.', 'success')
        return redirect(url_for('admin.store_config'))
    config_dict = {c.key: c.value for c in StoreConfig.query.all()}
    return render_template('admin/store_config.html', config=config_dict, keys=keys)
# --- NOTIFICACIONES INTERNAS PARA ADMINS ---
@admin_bp.route('/notifications')
@login_required
@admin_required
def admin_notifications():
    """Muestra las notificaciones internas para administradores."""
    notifications_list = AdminNotification.query.filter(
        (AdminNotification.admin_id.is_(None)) |
        (AdminNotification.admin_id == current_user.idUser)
    ).order_by(AdminNotification.created_at.desc()).all()
    return render_template('admin/admin_notifications.html', notifications=notifications_list)


@admin_bp.route('/notifications/read/<int:notif_id>', methods=['POST'])
@login_required
@admin_required
def mark_notification_read(notif_id):
    """Marca una notificación como leída."""
    notification = AdminNotification.query.get_or_404(notif_id)
    notification.is_read = True
    db.session.commit()
    return redirect(url_for('admin.admin_notifications'))


# Ruta para crear notificaciones de prueba (puedes eliminarla luego)
@admin_bp.route('/notifications/create', methods=['POST'])
@login_required
@admin_required
def create_admin_notification():
    """Crea una notificación de prueba para administradores."""
    message = request.form.get('message', '').strip()
    notification = AdminNotification(message=message)
    db.session.add(notification)
    db.session.commit()
    flash('Notificación creada.', 'success')
    return redirect(url_for('admin.admin_notifications'))
# --- EXPORTACIÓN DE DATOS ---
@admin_bp.route('/export/users')
@login_required
@admin_required
def export_users():
    """Exporta la lista de usuarios a CSV."""
    users_list = Users.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nombre', 'Email', 'Rol', 'Activo', 'Fecha registro'])
    for user in users_list:
        writer.writerow([
            user.idUser, user.nameUser, user.email,
            user.role, user.is_active_db, user.created_at
        ])
    csv_content = output.getvalue()
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=usuarios.csv"}
    )


@admin_bp.route('/export/products')
@login_required
@admin_required
def export_products():
    """Exporta la lista de productos a CSV."""
    products_list = Product.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nombre', 'Precio', 'Stock', 'Categoría', 'Fecha creación'])
    for product in products_list:
        writer.writerow([
            product.id, product.name, product.price,
            product.stock, product.category_id, product.created_at
        ])
    csv_content = output.getvalue()
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=productos.csv"}
    )


@admin_bp.route('/export/orders')
@login_required
@admin_required
def export_orders():
    """Exporta la lista de pedidos a CSV."""
    orders_list = Order.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Usuario', 'Total', 'Estado', 'Fecha'])
    for order in orders_list:
        writer.writerow([
            order.id, order.user_id, order.total, order.status, order.created_at
        ])
    csv_content = output.getvalue()
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=pedidos.csv"}
    )
# --- BANNERS Y CONTENIDO DESTACADO ---
@admin_bp.route('/banners')
@login_required
@admin_required
def banners():
    """Muestra la lista de banners."""
    banners_list = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('admin/banners.html', banners=banners_list)


@admin_bp.route('/banners/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_banner():
    """Agrega un nuevo banner."""
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
        banner_obj = Banner(title=title, image=filename, link=link, active=active)
        db.session.add(banner_obj)
        db.session.commit()
        flash('Banner creado.', 'success')
        return redirect(url_for('admin.banners'))
    return render_template('admin/banner_form.html', banner=None)


@admin_bp.route('/banners/edit/<int:banner_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_banner(banner_id):
    """Edita un banner existente."""
    banner_obj = Banner.query.get_or_404(banner_id)
    if request.method == 'POST':
        banner_obj.title = request.form.get('title', banner_obj.title).strip()
        banner_obj.link = request.form.get('link', banner_obj.link).strip()
        banner_obj.active = bool(request.form.get('active'))
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/banners')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            banner_obj.image = filename
        db.session.commit()
        flash('Banner actualizado.', 'success')
        return redirect(url_for('admin.banners'))
    return render_template('admin/banner_form.html', banner=banner_obj)


@admin_bp.route('/banners/toggle/<int:banner_id>', methods=['POST'])
@login_required
@admin_required
def toggle_banner(banner_id):
    """Activa/desactiva un banner."""
    banner_obj = Banner.query.get_or_404(banner_id)
    banner_obj.active = not banner_obj.active
    db.session.commit()
    flash('Estado del banner actualizado.', 'info')
    return redirect(url_for('admin.banners'))


@admin_bp.route('/banners/delete/<int:banner_id>', methods=['POST'])
@login_required
@admin_required
def delete_banner(banner_id):
    """Elimina un banner."""
    banner_obj = Banner.query.get_or_404(banner_id)
    db.session.delete(banner_obj)
    db.session.commit()
    flash('Banner eliminado.', 'danger')
    return redirect(url_for('admin.banners'))

# --- SOPORTE Y TICKETS ---
@admin_bp.route('/support_tickets')
@login_required
@admin_required
def support_tickets():
    """Muestra la lista de tickets de soporte."""
    tickets_list = SupportTicket.query.order_by(SupportTicket.created_at.desc()).all()
    for ticket in tickets_list:
        ticket.user = Users.query.get(ticket.user_id)
        ticket.assigned_admin = (
            Users.query.get(ticket.assigned_admin_id)
            if ticket.assigned_admin_id else None
        )
    return render_template('admin/support_tickets.html', tickets=tickets_list)


@admin_bp.route('/support_tickets/<int:ticket_id>')
@login_required
@admin_required
def view_ticket(ticket_id):
    """Muestra los detalles de un ticket específico."""
    ticket_obj = SupportTicket.query.get_or_404(ticket_id)
    ticket_obj.user = Users.query.get(ticket_obj.user_id)
    ticket_obj.assigned_admin = (
        Users.query.get(ticket_obj.assigned_admin_id)
        if ticket_obj.assigned_admin_id else None
    )
    return render_template('admin/view_ticket.html', ticket=ticket_obj)


@admin_bp.route('/support_tickets/assign/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def assign_ticket(ticket_id):
    """Asigna un ticket de soporte al administrador actual."""
    ticket_obj = SupportTicket.query.get_or_404(ticket_id)
    ticket_obj.assigned_admin_id = current_user.idUser
    ticket_obj.status = 'en_proceso'
    db.session.commit()
    flash('Ticket asignado a ti.', 'info')
    return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))


@admin_bp.route('/support_tickets/respond/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def respond_ticket(ticket_id):
    """Responde a un ticket de soporte."""
    ticket_obj = SupportTicket.query.get_or_404(ticket_id)
    response_text = request.form.get('response', '').strip()
    if not response_text:
        flash('Respuesta requerida.', 'danger')
        return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))
    # Aquí podrías guardar la respuesta en una tabla de mensajes/respuestas si se desea historial
    ticket_obj.status = 'en_proceso'
    db.session.commit()
    flash('Respuesta enviada (simulada).', 'success')
    return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))


@admin_bp.route('/support_tickets/close/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def close_ticket(ticket_id):
    """Cierra un ticket de soporte."""
    ticket_obj = SupportTicket.query.get_or_404(ticket_id)
    ticket_obj.status = 'cerrado'
    db.session.commit()
    flash('Ticket cerrado.', 'success')
    return redirect(url_for('admin.support_tickets'))

# --- AUDITORÍA ---
@admin_bp.route('/audit')
@login_required
@admin_required
def audit():
    """Muestra el registro de auditoría de acciones administrativas."""
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()
    for log_entry in audit_logs:
        log_entry.admin = Users.query.get(log_entry.admin_id)
    return render_template('admin/audit.html', logs=audit_logs)

# --- CUPONES ---
@admin_bp.route('/coupons')
@login_required
@admin_required
def coupons():
    """Muestra la lista de cupones."""
    coupons_list = Coupon.query.order_by(Coupon.created_at.desc()).all()
    products_list = Product.query.all()
    categories_list = Category.query.all()
    form = CouponForm()
    # Opciones dinámicas para selects
    form.product_id.choices = [(0, 'Producto (opcional)')] + [(p.id, p.name) for p in products_list]
    form.category_id.choices = (
        [(0, 'Categoría (opcional)')] +
        [(c.id, c.name) for c in categories_list]
    )
    return render_template(
        'admin/coupons.html',
        coupons=coupons_list,
        products=products_list,
        categories=categories_list,
        form=form
    )


@admin_bp.route('/coupons/add', methods=['POST'])
@login_required
@admin_required
def add_coupon():
    """Agrega un nuevo cupón."""
    form = CouponForm()
    products_list = Product.query.all()
    categories_list = Category.query.all()
    form.product_id.choices = [(0, 'Producto (opcional)')] + [(p.id, p.name) for p in products_list]
    form.category_id.choices = (
        [(0, 'Categoría (opcional)')] +
        [(c.id, c.name) for c in categories_list]
    )
    if form.validate_on_submit():
        coupon_obj = Coupon(
            code=form.code.data.strip().upper(),
            description=form.description.data.strip(),
            discount_percent=float(form.discount_percent.data),
            valid_from=form.valid_from.data,
            valid_to=form.valid_to.data,
            usage_limit=form.usage_limit.data or None,
            product_id=form.product_id.data if form.product_id.data else None,
            category_id=form.category_id.data if form.category_id.data else None
        )
        db.session.add(coupon_obj)
        db.session.commit()
        flash('Cupón creado.', 'success')
    else:
        flash('Error en el formulario de cupón.', 'danger')
    return redirect(url_for('admin.coupons'))


@admin_bp.route('/coupons/toggle/<int:coupon_id>', methods=['POST'])
@login_required
@admin_required
def toggle_coupon(coupon_id):
    """Activa/desactiva un cupón."""
    coupon_obj = Coupon.query.get_or_404(coupon_id)
    coupon_obj.active = not coupon_obj.active
    db.session.commit()
    flash('Estado del cupón actualizado.', 'info')
    return redirect(url_for('admin.coupons'))


@admin_bp.route('/coupons/delete/<int:coupon_id>', methods=['POST'])
@login_required
@admin_required
def delete_coupon(coupon_id):
    """Elimina un cupón."""
    coupon_obj = Coupon.query.get_or_404(coupon_id)
    db.session.delete(coupon_obj)
    db.session.commit()
    flash('Cupón eliminado.', 'danger')
    return redirect(url_for('admin.coupons'))

# --- DEVOLUCIONES ---
@admin_bp.route('/returns')
@login_required
@admin_required
def returns():
    """Muestra la lista de solicitudes de devolución."""
    returns_list = ReturnRequest.query.order_by(ReturnRequest.created_at.desc()).all()
    for return_request in returns_list:
        return_request.user = Users.query.get(return_request.user_id)
        return_request.order = Order.query.get(return_request.order_id)
    return render_template('admin/returns.html', returns=returns_list)


@admin_bp.route('/returns/approve/<int:return_id>', methods=['POST'])
@login_required
@admin_required
def approve_return(return_id):
    """Aprueba una solicitud de devolución."""
    return_request = ReturnRequest.query.get_or_404(return_id)
    return_request.status = 'aprobado'
    return_request.processed_at = datetime.utcnow()
    db.session.commit()
    flash('Devolución aprobada.', 'success')
    return redirect(url_for('admin.returns'))


@admin_bp.route('/returns/reject/<int:return_id>', methods=['POST'])
@login_required
@admin_required
def reject_return(return_id):
    """Rechaza una solicitud de devolución."""
    return_request = ReturnRequest.query.get_or_404(return_id)
    return_request.status = 'rechazado'
    return_request.processed_at = datetime.utcnow()
    db.session.commit()
    flash('Devolución rechazada.', 'danger')
    return redirect(url_for('admin.returns'))


@admin_bp.route('/returns/refund/<int:return_id>', methods=['POST'])
@login_required
@admin_required
def refund_return(return_id):
    """Procesa el reembolso de una devolución."""
    return_request = ReturnRequest.query.get_or_404(return_id)
    try:
        amount = float(request.form.get('refund_amount', 0))
        return_request.status = 'reembolsado'
        return_request.refund_amount = amount
        return_request.processed_at = datetime.utcnow()
        db.session.commit()
        flash(f'Reembolso de ${amount:.2f} registrado.', 'info')
    except ValueError:
        flash('Monto de reembolso inválido.', 'danger')
    except (TypeError, OverflowError) as exc:
        current_app.logger.error(f'Error al procesar reembolso: {exc}')
        flash('Error al registrar el reembolso.', 'danger')
    return redirect(url_for('admin.returns'))

# --- PEDIDOS ---
@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    """Muestra la lista de pedidos."""
    orders_list = Order.query.order_by(Order.created_at.desc()).all()
    for order_obj in orders_list:
        order_obj.user = Users.query.get(order_obj.user_id)
    return render_template('admin/orders.html', orders=orders_list)


@admin_bp.route('/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """Actualiza el estado de un pedido."""
    order_obj = Order.query.get_or_404(order_id)
    new_status = request.form.get('status', order_obj.status)
    order_obj.status = new_status
    db.session.commit()
    flash(f'Estado del pedido {order_obj.id} actualizado a {new_status}.', 'success')
    return redirect(url_for('admin.orders'))

# --- USUARIOS ---
@admin_bp.route('/users/reset_password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_reset_password(user_id):
    """Envía un correo de restablecimiento de contraseña para un usuario."""
    user_obj = Users.query.get_or_404(user_id)
    reset_token = secrets.token_urlsafe(32)
    user_obj.verification_token = reset_token
    user_obj.token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    reset_url = url_for('reset.reset_password', token=reset_token, _external=True)
    msg = Message('Recupera tu contraseña', recipients=[user_obj.email])
    msg.body = (
        'Un administrador ha solicitado el restablecimiento de tu contraseña. '
        f'Haz clic en el siguiente enlace: {reset_url}\n'
        'Este enlace expirará en 1 hora.'
    )
    mail.send(msg)
    flash(f'Se ha enviado un correo de restablecimiento a {user_obj.email}.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/block/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def block_user(user_id):
    """Bloquea a un usuario."""
    log_admin_action(current_user.idUser, 'bloquear', 'usuario', user_id, 'Bloqueado por admin')
    user_obj = Users.query.get_or_404(user_id)
    if user_obj.role == UserRole.ADMIN:
        flash('No se puede bloquear a otro administrador.', 'danger')
        return redirect(url_for('admin.dashboard'))
    user_obj.is_blocked = True
    db.session.commit()
    flash(f'Usuario {user_obj.nameUser} bloqueado.', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/unblock/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def unblock_user(user_id):
    """Desbloquea a un usuario."""
    log_admin_action(
        current_user.idUser, 'desbloquear', 'usuario',
        user_id, 'Desbloqueado por admin'
    )
    user_obj = Users.query.get_or_404(user_id)
    user_obj.is_blocked = False
    db.session.commit()
    flash(f'Usuario {user_obj.nameUser} desbloqueado.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<int:user_id>/orders')
@login_required
@admin_required
def user_orders(user_id):
    """Muestra los pedidos de un usuario específico."""
    user_obj = Users.query.get_or_404(user_id)
    user_orders_list = (
        Order.query.filter_by(user_id=user_id)
        .order_by(Order.created_at.desc()).all()
    )
    for order_obj in user_orders_list:
        order_obj.details = OrderDetail.query.filter_by(order_id=order_obj.id).all()
    return render_template('admin/user_orders.html', user=user_obj, orders=user_orders_list)


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Elimina a un usuario."""
    user_obj = Users.query.get_or_404(user_id)
    if user_obj.role == UserRole.ADMIN:
        flash('No se puede eliminar a otro administrador.', 'danger')
        return redirect(url_for('admin.dashboard'))
    db.session.delete(user_obj)
    db.session.commit()
    flash('Usuario eliminado correctamente.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/make_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    """Concede permisos de administrador a un usuario."""
    log_admin_action(current_user.idUser, 'hacer_admin', 'usuario', user_id, 'Ascendido a admin')
    user_obj = Users.query.get_or_404(user_id)
    user_obj.role = UserRole.ADMIN
    db.session.commit()
    flash(f'El usuario {user_obj.nameUser} ahora es administrador.', 'success')
    return redirect(url_for('admin.dashboard'))

# --- DASHBOARD ---
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Muestra el panel de administración principal."""
    search_query = request.args.get('q', '').strip()
    user_query = Users.query
    if search_query:
        user_query = user_query.filter(
            (Users.nameUser.ilike(f'%{search_query}%')) |
            (Users.email.ilike(f'%{search_query}%'))
        )
    users_list = user_query.all()
    total_registered_users = Users.query.count()
    # Estadísticas reales
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_sales = db.session.query(func.sum(Order.total)).scalar() or 0.0
    stats = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_sales': float(total_sales)
    }
    total_notifications = Notification.query.count()
    return render_template(
        'admin/dashboard.html',
        usuarios=users_list,
        usuarios_registrados=total_registered_users,
        estadisticas=stats,
        notificaciones=total_notifications,
        q=search_query
    )

# --- PRODUCTOS Y CATEGORÍAS ---
@admin_bp.route('/products')
@login_required
@admin_required
def products():
    """Muestra la lista paginada de productos."""
    page = request.args.get('page', 1, type=int)
    products_paginated = Product.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/products.html', products=products_paginated)


@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def categories():
    """Muestra la lista paginada de categorías y maneja la creación de nuevas."""
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        description = form.description.data.strip()
        if Category.query.filter_by(name=name).first():
            flash('El nombre de la categoría ya existe.', 'danger')
        else:
            category_obj = Category(name=name, description=description)
            db.session.add(category_obj)
            db.session.commit()
            log_admin_action(
                current_user.idUser, 'crear', 'categoria',
                category_obj.id, f'Categoría: {name}'
            )
            flash('Categoría agregada correctamente.', 'success')
        return redirect(url_for('admin.categories'))
    page = request.args.get('page', 1, type=int)
    categories_paginated = Category.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/categories.html', categories=categories_paginated, form=form)

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
            price = form.price.data  # Decimal, se guarda tal cual
            stock = int(form.stock.data)
            size = form.size.data.strip()
            color = form.color.data.strip()
            category_id = form.category_id.data
            image_filename = None
            image_file = form.image.data
            if image_file and hasattr(image_file, 'filename') and image_file.filename:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(
                    current_app.root_path,
                    current_app.config.get('UPLOAD_FOLDER', 'static/product_images')
                )
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, filename)
                image_file.save(image_path)
                image_filename = filename
            product_obj = Product(
                name=name, description=description, price=price, stock=stock,
                image=image_filename, size=size, color=color, category_id=category_id
            )
            db.session.add(product_obj)
            db.session.commit()
            log_admin_action(
                current_user.idUser, 'crear', 'producto',
                product_obj.id, f'Producto: {name}'
            )
            flash('Producto agregado correctamente.', 'success')
            return redirect(url_for('admin.products'))
        except ValueError as exc:
            current_app.logger.error(f'Error en add_product: {exc}')
            flash('Error en los datos numéricos.', 'danger')
            return redirect(url_for('admin.add_product'))
        except (OSError, IOError) as exc:
            db.session.rollback()
            current_app.logger.error(f'Error de archivo: {exc}')
            flash('Error al procesar imagen.', 'danger')
    return render_template('admin/add_product.html', form=form)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    """Edita un producto existente con validación y manejo de errores."""
    product_obj = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        try:
            from decimal import Decimal
            product_obj.name = request.form.get('name', product_obj.name).strip()
            product_obj.description = request.form.get(
                'description', product_obj.description
            ).strip()
            # Mantener consistencia con add_product usando Decimal
            price_str = request.form.get('price')
            if price_str:
                product_obj.price = Decimal(price_str)
            product_obj.stock = int(request.form.get('stock') or product_obj.stock)
            product_obj.size = request.form.get('size', product_obj.size).strip()
            product_obj.color = request.form.get('color', product_obj.color).strip()
            product_obj.category_id = int(
                request.form.get('category_id') or product_obj.category_id
            )
            if (product_obj.price <= 0 or product_obj.stock < 0 or
                not Category.query.get(product_obj.category_id)):
                flash('Datos inválidos: precio > 0, stock >= 0 y categoría válida.', 'danger')
                return redirect(url_for('admin.edit_product', product_id=product_id))
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(
                    current_app.root_path,
                    current_app.config.get('UPLOAD_FOLDER', 'static/product_images')
                )
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, filename)
                image_file.save(image_path)
                product_obj.image = filename
            db.session.commit()
            log_admin_action(
                current_user.idUser, 'editar', 'producto',
                product_obj.id, f'Editado: {product_obj.name}'
            )
            flash('Producto actualizado.', 'success')
            return redirect(url_for('admin.products'))
        except ValueError as exc:
            current_app.logger.error(f'Error en edit_product: {exc}')
            flash('Error en los datos numéricos.', 'danger')
            return redirect(url_for('admin.edit_product', product_id=product_id))
        except (OSError, IOError) as exc:
            db.session.rollback()
            current_app.logger.error(f'Error de archivo: {exc}')
            flash('Error al procesar imagen.', 'danger')
    categories_list = Category.query.all()
    return render_template(
        'admin/edit_product.html',
        product=product_obj,
        categories=categories_list
    )

@admin_bp.route('/products/delete/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_product(product_id):
    """Elimina un producto."""
    log_admin_action(current_user.idUser, 'eliminar', 'producto', product_id, 'Eliminado por admin')
    if request.form.get('confirm_delete') != 'yes':
        flash('Confirmación requerida para eliminar.', 'danger')
        return redirect(url_for('admin.products'))
    product_obj = Product.query.get_or_404(product_id)

    # Eliminar order_details y wishlists relacionadas para evitar constraint violation
    OrderDetail.query.filter_by(product_id=product_id).delete()
    Wishlist.query.filter_by(product_id=product_id).delete()

    db.session.delete(product_obj)
    db.session.commit()
    flash('Producto eliminado.', 'info')
    return redirect(url_for('admin.products'))

csrf.exempt(delete_product)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Agrega una nueva categoría."""
    form = CategoryForm()
    if form.validate_on_submit():
        category_name = form.name.data.strip()
        category_description = form.description.data.strip()
        if Category.query.filter_by(name=category_name).first():
            flash('El nombre de la categoría ya existe.', 'danger')
            return redirect(url_for('admin.add_category'))
        category_obj = Category(name=category_name, description=category_description)
        db.session.add(category_obj)
        db.session.commit()
        log_admin_action(
            current_user.idUser, 'crear', 'categoria',
            category_obj.id, f'Categoría: {category_name}'
        )
        flash('Categoría agregada.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/add_category.html', form=form)


@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """Edita una categoría existente."""
    category_obj = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        new_category_name = request.form.get('name', category_obj.name).strip()
        if Category.query.filter(
            Category.name == new_category_name,
            Category.id != category_id
        ).first():
            flash('Nombre debe ser único.', 'danger')
            return redirect(url_for('admin.edit_category', category_id=category_id))
        category_obj.name = new_category_name
        category_obj.description = request.form.get(
            'description', category_obj.description
        ).strip()
        db.session.commit()
        log_admin_action(
            current_user.idUser, 'editar', 'categoria',
            category_obj.id, f'Editada: {category_obj.name}'
        )
        flash('Categoría actualizada.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/edit_category.html', category=category_obj)


@admin_bp.route('/categories/delete/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_category(category_id):
    """Elimina una categoría."""
    log_admin_action(current_user.idUser, 'eliminar', 'categoria', category_id, 'Eliminada por admin')
    if request.form.get('confirm_delete') != 'yes':
        flash('Confirmación requerida para eliminar.', 'danger')
        return redirect(url_for('admin.categories'))
    category_obj = Category.query.get_or_404(category_id)
    if Product.query.filter_by(category_id=category_id).first():
        pass
        flash('No se puede eliminar: hay productos asociados.', 'danger')
        return redirect(url_for('admin.categories'))
    db.session.delete(category_obj)
    db.session.commit()
    flash('Categoría eliminada.', 'info')
    return redirect(url_for('admin.categories'))

csrf.exempt(delete_category)

# --- INVENTARIO ---
@admin_bp.route('/inventory', methods=['GET'])
@login_required
@admin_required
def inventory():
    """Muestra el inventario de productos ordenado por stock."""
    products_list = Product.query.order_by(Product.stock.asc()).all()
    return render_template('admin/inventory.html', products=products_list)

@admin_bp.route('/inventory/update/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def update_stock(product_id):
    """Actualiza el stock de un producto."""
    product_obj = Product.query.get_or_404(product_id)
    try:
        new_stock = int(request.form.get('stock', product_obj.stock))
        if new_stock < 0:
            flash('El stock no puede ser negativo.', 'danger')
            return redirect(url_for('admin.inventory'))
        product_obj.stock = new_stock
        db.session.commit()
        flash(f'Stock de "{product_obj.name}" actualizado a {new_stock}.', 'success')
    except ValueError:
        flash('Valor de stock inválido.', 'danger')
    except (TypeError, OverflowError) as exc:
        db.session.rollback()
        current_app.logger.error(f'Error al actualizar stock: {exc}')
        flash('Error al actualizar el stock.', 'danger')
    return redirect(url_for('admin.inventory'))

# --- RESEÑAS ---
@admin_bp.route('/reviews/moderate')
@login_required
@admin_required
def moderate_reviews():
    """Muestra las reseñas pendientes de moderación."""
    reviews_list = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/moderate_reviews.html', reviews=reviews_list)


@admin_bp.route('/reviews/approve/<int:review_id>', methods=['POST'])
@login_required
@admin_required
def approve_review(review_id):
    """Aprueba una reseña."""
    review_obj = Review.query.get_or_404(review_id)
    review_obj.aprobada = True
    db.session.commit()
    flash('Reseña aprobada.', 'success')
    return redirect(url_for('admin.moderate_reviews'))


@admin_bp.route('/reviews/reject/<int:review_id>', methods=['POST'])
@login_required
@admin_required
def reject_review(review_id):
    """Rechaza y elimina una reseña."""
    review_obj = Review.query.get_or_404(review_id)
    db.session.delete(review_obj)
    db.session.commit()
    flash('Reseña eliminada.', 'info')
    return redirect(url_for('admin.moderate_reviews'))


# --- REPORTES ---
@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Muestra reportes de ventas y estadísticas."""
    total_sales = db.session.query(func.sum(Order.total)).scalar() or 0
    sales_by_product = db.session.query(
        Product.name,
        func.sum(OrderDetail.quantity).label('cantidad'),
        func.sum(OrderDetail.price * OrderDetail.quantity).label('total')
    ).join(Product, OrderDetail.product_id == Product.id).group_by(
        OrderDetail.product_id, Product.name
    ).all()
    sales_by_date = db.session.query(
        func.date(Order.created_at).label('fecha'),
        func.sum(Order.total).label('total')
    ).group_by('fecha').all()
    sales_by_date_formatted = [(str(fecha), total) for fecha, total in sales_by_date]
    return render_template(
        'admin/reports.html',
        total_ventas=total_sales,
        ventas_por_producto=sales_by_product,
        ventas_por_fecha=sales_by_date_formatted
    )


# --- API DE VENTAS POR DÍA ---
@admin_bp.route('/api/sales_by_day')
@login_required
@admin_required
def api_sales_by_day():
    """API que retorna datos de ventas por día en formato JSON."""
    sales_by_date = db.session.query(
        func.date(Order.created_at).label('fecha'),
        func.sum(Order.total).label('total')
    ).group_by('fecha').order_by('fecha').all()
    sales_data = {
        'labels': [str(fecha) for fecha, _ in sales_by_date],
        'totals': [float(total) for _, total in sales_by_date]
    }
    return sales_data
