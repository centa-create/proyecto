import secrets
from app.models.users import Users
# Generar y guardar un token de enlace público para cada usuario (si no existe)
def get_or_create_wishlist_token(user):
    if not hasattr(user, 'wishlist_token') or not user.wishlist_token:
        token = secrets.token_urlsafe(12)
        user.wishlist_token = token
        db.session.commit()
    return user.wishlist_token

# Ruta para ver la wishlist propia y obtener enlace compartible
from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app import db
from app.models.wishlist import Wishlist
from app.models.products import Product

wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')

@wishlist_bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    from flask import jsonify, request
    if not current_user.is_authenticated:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'login_required': True, 'message': 'Debes iniciar sesión para agregar a favoritos.'}), 401
        return redirect(url_for('auth.login'))
    if Wishlist.query.filter_by(user_id=current_user.idUser, product_id=product_id).first():
        return jsonify({'success': False, 'message': 'El producto ya está en tu lista de deseos.'}), 400
    db.session.add(Wishlist(user_id=current_user.idUser, product_id=product_id))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto agregado a tu lista de deseos.'})

@wishlist_bp.route('/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    item = Wishlist.query.filter_by(user_id=current_user.idUser, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Producto eliminado de tu lista de deseos.', 'info')
    return redirect(url_for('wishlist.view_wishlist'))

@wishlist_bp.route('/')
@login_required
def view_wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.idUser).all()
    token = get_or_create_wishlist_token(current_user)
    share_url = url_for('wishlist.shared_wishlist', token=token, _external=True)
    return render_template('wishlist/wishlist.html', items=items, share_url=share_url)

# Ruta pública para ver la wishlist compartida
@wishlist_bp.route('/shared/<token>')
def shared_wishlist(token):
    user = Users.query.filter_by(wishlist_token=token).first()
    if not user:
        flash('Lista de deseos no encontrada.', 'danger')
        return redirect(url_for('catalog.catalog'))
    items = Wishlist.query.filter_by(user_id=user.idUser).all()
    return render_template('wishlist/shared_wishlist.html', items=items, user=user)
