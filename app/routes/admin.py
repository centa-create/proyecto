from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from functools import wraps
from app.models.products import Product, Category
from app.models.orders import Order, OrderDetail
from app.models.users import Users, UserRole
from app.models.notifications import Notification
from app import db
import os
from sqlalchemy import func

def admin_required(f):
    """Decorador para restringir acceso solo a administradores autenticados."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('Acceso denegado: solo administradores.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Permite al administrador eliminar usuarios."""
    user = Users.query.get_or_404(user_id)
    if user.role == UserRole.ADMIN:
        flash('No se puede eliminar a otro administrador.', 'danger')
        return redirect(url_for('admin.dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado correctamente.', 'info')
    return redirect(url_for('admin.dashboard'))

def admin_required(f):
    """Decorador para restringir acceso solo a administradores autenticados."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('Acceso denegado: solo administradores.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/make_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    """Convierte un usuario en administrador."""
    user = Users.query.get_or_404(user_id)
    user.role = UserRole.ADMIN
    db.session.commit()
    flash(f'El usuario {user.nameUser} ahora es administrador.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Panel principal de administración con estadísticas y usuarios paginados."""
    usuarios_registrados = Users.query.count()
    usuarios_activos = Users.query.filter_by(is_active_db=True).count()
    usuarios_inactivos = usuarios_registrados - usuarios_activos
    estadisticas = int((usuarios_activos / usuarios_registrados * 100) if usuarios_registrados > 0 else 0)
    notificaciones = Notification.query.count()
    # Paginación para usuarios (ejemplo: página 1, 20 por página)
    page = request.args.get('page', 1, type=int)
    usuarios = Users.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/dashboard.html',
                           usuarios_registrados=usuarios_registrados,
                           usuarios_activos=usuarios_activos,
                           usuarios_inactivos=usuarios_inactivos,
                           estadisticas=estadisticas,
                           notificaciones=notificaciones,
                           usuarios=usuarios)

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    """Lista paginada de productos."""
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/products.html', products=products)

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    """Lista paginada de categorías."""
    page = request.args.get('page', 1, type=int)
    categories = Category.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    """Agrega un nuevo producto con validación y manejo de errores."""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = float(request.form.get('price') or 0)
            stock = int(request.form.get('stock') or 0)
            size = request.form.get('size', '').strip()
            color = request.form.get('color', '').strip()
            category_id = int(request.form.get('category_id') or 0)
            if not name or price <= 0 or stock < 0 or not Category.query.get(category_id):
                flash('Datos inválidos: nombre, precio > 0, stock >= 0 y categoría válida son obligatorios.', 'danger')
                return redirect(url_for('admin.add_product'))
            image_filename = None
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(current_app.root_path, current_app.config.get('UPLOAD_FOLDER', 'static/product_images'))
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, filename)
                image_file.save(image_path)
                image_filename = filename
            product = Product(name=name, description=description, price=price, stock=stock, image=image_filename, size=size, color=color, category_id=category_id)
            db.session.add(product)
            db.session.commit()
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
    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)

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
    """Elimina un producto tras confirmación."""
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
    """Agrega una nueva categoría con validación de unicidad."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name or Category.query.filter_by(name=name).first():
            flash('Nombre obligatorio y único.', 'danger')
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
    """Edita una categoría existente con validación de unicidad."""
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        new_name = request.form.get('name', category.name).strip()
        if Category.query.filter(Category.name == new_name, Category.id != category_id).first():
            flash('Nombre debe ser único.', 'danger')
            return redirect(url_for('admin.edit_category', category_id=category_id))
        category.name = new_name
        category.description = request.form.get('description', category.description).strip()
        db.session.commit()
        flash('Categoría actualizada.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/edit_category.html', category=category)

@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """Elimina una categoría tras confirmación y si no tiene productos asociados."""
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

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Genera reportes de ventas totales, por producto y por fecha."""
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
    # Formateo para templates (opcional)
    ventas_por_fecha = [(str(fecha), total) for fecha, total in ventas_por_fecha]
    return render_template('admin/reports.html',
                           total_ventas=total_ventas,
                           ventas_por_producto=ventas_por_producto,
                           ventas_por_fecha=ventas_por_fecha)