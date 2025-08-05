from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.cart import Cart, CartItem
from app.models.products import Product

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    items = cart.items if cart else []
    return render_template('cart/cart.html', items=items)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart:
        cart = Cart(user_id=current_user.idUser)
        db.session.add(cart)
        db.session.commit()
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        item.quantity += 1
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=1)
        db.session.add(item)
    db.session.commit()
    flash('Producto agregado al carrito.', 'success')
    return redirect(url_for('catalog.catalog'))

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Producto eliminado del carrito.', 'info')
    return redirect(url_for('cart.view_cart'))
