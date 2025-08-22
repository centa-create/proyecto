import stripe
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.cart import Cart, CartItem
from app.models.products import Product
from app.models.orders import Order, OrderDetail  # Asumiendo modelos de orders del admin blueprint

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def view_cart():
    # Obtener los productos del carrito para el usuario actual
    cart_items = CartItem.query.join(Cart).filter(Cart.user_id==current_user.idUser).all()
    products_in_cart = []
    total = 0
    for item in cart_items:
        if item.product:
            products_in_cart.append({
                'id': item.id,
                'product': item.product,
                'quantity': item.quantity,
                'subtotal': item.product.price * item.quantity
            })
            total += item.product.price * item.quantity
    return render_template('carrito.html', cart_items=products_in_cart, total=total)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        flash('Producto sin stock disponible.', 'danger')
        return redirect(url_for('catalog.catalog'))
    cantidad = request.form.get('cantidad', 1)
    try:
        cantidad = int(cantidad)
    except ValueError:
        cantidad = 1
    if cantidad < 1:
        cantidad = 1
    if cantidad > product.stock:
        flash('No hay suficiente stock disponible.', 'danger')
        return redirect(url_for('catalog.product_detail', product_id=product_id))
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart:
        cart = Cart(user_id=current_user.idUser)
        db.session.add(cart)
        db.session.commit()
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        if item.quantity + cantidad > product.stock:
            flash('No hay suficiente stock.', 'danger')
            return redirect(url_for('catalog.product_detail', product_id=product_id))
        item.quantity += cantidad
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=cantidad, price_snapshot=product.price)
        db.session.add(item)
    db.session.commit()
    flash('Producto agregado al carrito.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.idUser:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('cart.view_cart'))
    db.session.delete(item)
    db.session.commit()
    flash('Producto eliminado del carrito.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart or not cart.items:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('cart.view_cart'))
    total = sum(item.quantity * item.product.price for item in cart.items)
    if request.method == 'POST':
        try:
            # Crear orden
            order = Order(user_id=current_user.idUser, total=total)
            db.session.add(order)
            db.session.commit()  # Commit para obtener order.id
            for item in cart.items:
                detail = OrderDetail(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
                db.session.add(detail)
                # Reducir stock
                item.product.stock -= item.quantity
            db.session.commit()
            # Vaciar carrito
            db.session.delete(cart)
            db.session.commit()
            flash('Pedido confirmado. Redirigiendo a la pasarela de pago...', 'success')
            return redirect(url_for('cart.payment', order_id=order.id))  # Pasar order_id si necesitas
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error en checkout: {e}')
            flash('Error al confirmar pedido.', 'danger')
    return render_template('cart/checkout.html', items=cart.items, total=total)

@cart_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart or not cart.items:
        flash('No hay productos para pagar.', 'warning')
        return redirect(url_for('cart.view_cart'))
    total = sum(item.quantity * item.product.price for item in cart.items)
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    if not stripe.api_key:
        flash('Configuración de pago no disponible.', 'danger')
        return redirect(url_for('cart.view_cart'))
    if request.method == 'POST':
        metodo = request.form.get('metodo_pago')
        if metodo == 'stripe':
            try:
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
                return redirect(session.url, code=303)
            except stripe.error.StripeError as e:
                current_app.logger.error(f'Error en Stripe: {e}')
                flash('Error en el pago con Stripe.', 'danger')
        elif metodo == 'nequi':
            flash('Realiza tu pago a Nequi: 3001234567 y envía el comprobante.', 'info')
            return redirect(url_for('cart.view_cart'))
        elif metodo == 'bancolombia':
            flash('Realiza tu pago a Bancolombia: 12345678901 y envía el comprobante.', 'info')
            return redirect(url_for('cart.view_cart'))
        else:
            flash('Selecciona un método de pago.', 'danger')
    return render_template('cart/payment.html', total=total)