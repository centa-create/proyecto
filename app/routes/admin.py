@admin_bp.route('/make_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    from app.models.users import Users, UserRole
    user = Users.query.get_or_404(user_id)
    user.role = UserRole.ADMIN
    db.session.commit()
    flash(f'El usuario {user.nameUser} ahora es administrador.', 'success')
    return redirect(url_for('admin.dashboard'))

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from app.models.products import Product, Category
from app.models.orders import Order, OrderDetail
from app.models.users import UserRole
from app import db
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorador para admin (puedes mejorar con roles)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'role', None) or str(current_user.role) != 'ADMIN':
            flash('Acceso solo para administradores.', 'danger')
            return redirect(url_for('client.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', None) != UserRole.ADMIN:
            flash('Acceso denegado: solo administradores.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@is_admin
def dashboard():
    # Datos reales para el dashboard
    from app.models.users import Users
    from app.models.notifications import Notification
    usuarios_registrados = Users.query.count()
    # Ejemplo de estadística: porcentaje de usuarios activos
    usuarios_activos = Users.query.filter_by(is_active_db=True).count()
    estadisticas = 0
    if usuarios_registrados > 0:
        estadisticas = int((usuarios_activos / usuarios_registrados) * 100)
    notificaciones = Notification.query.count() if 'Notification' in globals() else 0
    # Mostrar lista de usuarios para gestión
    usuarios = Users.query.all()
    return render_template('admin/dashboard.html',
        usuarios_registrados=usuarios_registrados,
        estadisticas=estadisticas,
        notificaciones=notificaciones,
        usuarios=usuarios)

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', type=int)
        size = request.form.get('size', '').strip()
        color = request.form.get('color', '').strip()
        category_id = request.form.get('category_id', type=int)
        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename:
            import os
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.root_path, 'static', 'product_images', filename)
            image_file.save(image_path)
            image_filename = filename
        if not name or not price or not category_id:
            flash('Nombre, precio y categoría son obligatorios.', 'danger')
            return redirect(url_for('admin.add_product'))
        product = Product(name=name, description=description, price=price, stock=stock or 0, image=image_filename, size=size, color=color, category_id=category_id)
        db.session.add(product)
        db.session.commit()
        flash('Producto agregado correctamente.', 'success')
        return redirect(url_for('admin.products'))
    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.description = request.form.get('description', '').strip()
        product.price = request.form.get('price', type=float)
        product.stock = request.form.get('stock', type=int)
        product.size = request.form.get('size', '').strip()
        product.color = request.form.get('color', '').strip()
        product.category_id = request.form.get('category_id', type=int)
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            import os
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.root_path, 'static', 'product_images', filename)
            image_file.save(image_path)
            product.image = filename
        db.session.commit()
        flash('Producto actualizado.', 'success')
        return redirect(url_for('admin.products'))
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Producto eliminado.', 'info')
    return redirect(url_for('admin.products'))

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('El nombre es obligatorio.', 'danger')
            return redirect(url_for('admin.add_category'))
        if Category.query.filter_by(name=name).first():
            flash('Ya existe una categoría con ese nombre.', 'danger')
            return redirect(url_for('admin.add_category'))
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        flash('Categoría agregada.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/add_category.html')

@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        category.name = request.form.get('name', '').strip()
        category.description = request.form.get('description', '').strip()
        db.session.commit()
        flash('Categoría actualizada.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/edit_category.html', category=category)

@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Categoría eliminada.', 'info')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    from sqlalchemy import func
    # Ventas totales
    total_ventas = db.session.query(func.sum(Order.total)).scalar() or 0
    # Ventas por producto
    ventas_por_producto = db.session.query(
        OrderDetail.product_id,
        func.sum(OrderDetail.quantity).label('cantidad'),
        func.sum(OrderDetail.price * OrderDetail.quantity).label('total')
    ).group_by(OrderDetail.product_id).all()
    # Ventas por fecha
    ventas_por_fecha = db.session.query(
        func.date(Order.created_at),
        func.sum(Order.total)
    ).group_by(func.date(Order.created_at)).all()
    return render_template('admin/reports.html', total_ventas=total_ventas, ventas_por_producto=ventas_por_producto, ventas_por_fecha=ventas_por_fecha)
