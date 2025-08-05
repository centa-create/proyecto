from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app import db
from app.models.wishlist import Wishlist
from app.models.products import Product

wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')

@wishlist_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    if Wishlist.query.filter_by(user_id=current_user.idUser, product_id=product_id).first():
        flash('El producto ya está en tu lista de deseos.', 'info')
    else:
        db.session.add(Wishlist(user_id=current_user.idUser, product_id=product_id))
        db.session.commit()
        flash('Producto agregado a tu lista de deseos.', 'success')
    return redirect(url_for('catalog.product_detail', product_id=product_id))

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
    return render_template('wishlist/wishlist.html', items=items)
