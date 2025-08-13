import stripe
@cart_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    """Página de integración con Stripe, Nequi y Bancolombia."""
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart or not cart.items:
        flash('No hay productos para pagar.', 'warning')
        return redirect(url_for('cart.view_cart'))
    total = sum(item.quantity * item.product.price for item in cart.items)
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', 'sk_test_...')
    if request.method == 'POST':
        metodo = request.form.get('metodo_pago')
        if metodo == 'stripe':
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'cop',
                        'product_data': {
                            'name': 'Pedido en tienda',
                        },
                        'unit_amount': int(total * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=url_for('cart.view_cart', _external=True),
                cancel_url=url_for('cart.payment', _external=True),
            )
            return redirect(session.url)
        elif metodo == 'nequi':
            flash('Realiza tu pago a Nequi: 3001234567 y envía el comprobante.', 'info')
            return redirect(url_for('cart.view_cart'))
        elif metodo == 'bancolombia':
            flash('Realiza tu pago a Bancolombia: 12345678901 y envía el comprobante.', 'info')
            return redirect(url_for('cart.view_cart'))
        else:
            flash('Selecciona un método de pago.', 'danger')
    return render_template('cart/payment.html', total=total)
@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Muestra el resumen del carrito y permite confirmar el pedido antes de pagar."""
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart or not cart.items:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('cart.view_cart'))
    total = sum(item.quantity * item.product.price for item in cart.items)
    if request.method == 'POST':
        # Aquí se crearía el pedido y se redirigiría a la pasarela de pago
        # Puedes guardar el pedido en la base de datos antes de redirigir
        flash('Pedido confirmado. Redirigiendo a la pasarela de pago...', 'success')
        return redirect(url_for('cart.payment'))
    return render_template('cart/checkout.html', items=cart.items, total=total)

@cart_bp.route('/payment', methods=['GET'])
@login_required
def payment():
    """Página de integración con la pasarela de pago (ejemplo: Stripe, MercadoPago)."""
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart or not cart.items:
        flash('No hay productos para pagar.', 'warning')
        return redirect(url_for('cart.view_cart'))
    total = sum(item.quantity * item.product.price for item in cart.items)
    # Aquí se mostraría el formulario o botón de pago de la pasarela
    # Ejemplo: Stripe Checkout, MercadoPago, etc.
    return render_template('cart/payment.html', total=total)
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
