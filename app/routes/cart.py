"""
Rutas para la gestión del carrito de compras en la interfaz web.

Este módulo maneja la visualización, adición, eliminación y checkout del carrito.
"""

import hashlib
import uuid

import requests
from flask import (
    Blueprint, jsonify, render_template, redirect, url_for,
    request, flash, current_app
)
from flask_login import login_required, current_user
from app import db
from app.models.cart import Cart, CartItem
from app.models.products import Product
from app.models.orders import (
    Order, OrderDetail
)

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def view_cart():
    """Muestra el contenido del carrito del usuario."""
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
def add_to_cart(product_id):
    """Agrega un producto al carrito."""
    if not current_user.is_authenticated:
        # Si es petición AJAX, devolver JSON especial
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'login_required': True,
                'message': 'Debes iniciar sesión para agregar al carrito.'
            }), 401
        # Si no, redirigir a login
        return redirect(url_for('auth.login'))
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        return jsonify({'success': False, 'message': 'Producto sin stock disponible.'}), 400
    cantidad = request.form.get('cantidad', 1)
    try:
        cantidad = int(cantidad)
    except ValueError:
        cantidad = 1
    if cantidad < 1:
        cantidad = 1
    if cantidad > product.stock:
        return jsonify({'success': False, 'message': 'No hay suficiente stock disponible.'}), 400
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart:
        cart = Cart(user_id=current_user.idUser)
        db.session.add(cart)
        db.session.commit()
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        if item.quantity + cantidad > product.stock:
            return jsonify({'success': False, 'message': 'No hay suficiente stock.'}), 400
        item.quantity += cantidad
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=cantidad,
            price_snapshot=product.price
        )
        db.session.add(item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto agregado al carrito.'})

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remueve un item del carrito."""
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
    """Maneja el proceso de checkout del carrito."""
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
                detail = OrderDetail(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price
                )
                db.session.add(detail)
                # Reducir stock
                item.product.stock -= item.quantity
            db.session.commit()
            # Vaciar carrito
            db.session.delete(cart)
            db.session.commit()
            flash('Pedido confirmado. Redirigiendo a la pasarela de pago...', 'success')
            return redirect(url_for('cart.payment', order_id=order.id))
        except (ValueError, TypeError) as e:
            db.session.rollback()
            current_app.logger.error(f'Error en checkout: {e}')
            flash('Error al confirmar pedido.', 'danger')
    return render_template('cart/checkout.html', items=cart.items, total=total)

@cart_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    """Maneja la selección y procesamiento del método de pago."""
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart or not cart.items:
        flash('No hay productos para pagar.', 'warning')
        return redirect(url_for('cart.view_cart'))
    total = sum(item.quantity * item.product.price for item in cart.items)

    # Verificar configuración PayU
    api_key = current_app.config.get('PAYU_API_KEY')
    api_login = current_app.config.get('PAYU_API_LOGIN')
    merchant_id = current_app.config.get('PAYU_MERCHANT_ID')
    account_id = current_app.config.get('PAYU_ACCOUNT_ID')

    if not all([api_key, api_login, merchant_id, account_id]):
        flash('Configuración de pago no disponible.', 'danger')
        return redirect(url_for('cart.view_cart'))

    if request.method == 'POST':
        metodo = request.form.get('metodo_pago')
        if metodo == 'simulada':
            # Crear orden primero
            order = Order(user_id=current_user.idUser, total=total, status='pendiente')
            db.session.add(order)
            db.session.commit()
            return redirect(url_for('cart.payment_simulated', order_id=order.id))
        elif metodo == 'payu':
            try:
                # Crear orden primero
                order = Order(user_id=current_user.idUser, total=total, status='pendiente')
                db.session.add(order)
                db.session.commit()

                # Configuración PayU
                test_mode = current_app.config.get('PAYU_TEST_MODE', True)
                base_url = (
                    'https://sandbox.checkout.payulatam.com' if test_mode
                    else 'https://checkout.payulatam.com'
                )
                response_url = url_for('cart.view_cart', _external=True)
                confirmation_url = url_for('webhook.payu_webhook', _external=True)

                # Generar referencia única
                reference_code = f"ORDER_{order.id}_{uuid.uuid4().hex[:8]}"

                # Crear firma MD5
                signature_string = f"{api_key}~{merchant_id}~{reference_code}~{int(total)}~COP"
                signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()

                # Datos para PayU
                payu_data = {
                    'merchantId': merchant_id,
                    'accountId': account_id,
                    'description': f'Compra en SAMMS.FO - Orden {order.id}',
                    'referenceCode': reference_code,
                    'amount': str(int(total)),
                    'currency': 'COP',
                    'tax': '0',
                    'taxReturnBase': '0',
                    'signature': signature,
                    'test': '1' if test_mode else '0',
                    'buyerEmail': current_user.email,
                    'buyerFullName': current_user.nameUser,
                    'responseUrl': response_url,
                    'confirmationUrl': confirmation_url,
                    'extra1': str(order.id),
                    'lng': 'es'
                }

                # Enviar a PayU y redirigir
                response = requests.post(
                    f'{base_url}/ppp-web-gateway-payu/',
                    data=payu_data,
                    timeout=30,
                    allow_redirects=False
                )
                if response.status_code in [200, 302]:
                    return redirect(response.headers.get('Location', response.url), code=303)
                else:
                    current_app.logger.error(
                        f'PayU error: {response.status_code} - {response.text}'
                    )
                    flash('Error al procesar pago.', 'danger')

            except requests.RequestException as e:
                current_app.logger.error(f'PayU request failed: {e}')
                flash('Error de conexión con PayU.', 'danger')

        elif metodo == 'nequi':
            flash('Realiza tu pago a Nequi: 3001234567 y envía el comprobante.', 'info')
            return redirect(url_for('cart.view_cart'))
        elif metodo == 'bancolombia':
            flash('Realiza tu pago a Bancolombia: 12345678901 y envía el comprobante.', 'info')
            return redirect(url_for('cart.view_cart'))
        else:
            flash('Selecciona un método de pago.', 'danger')

    return render_template('cart/payment.html', total=total)

@cart_bp.route('/payment/simulated/<int:order_id>', methods=['GET', 'POST'])
@login_required
def payment_simulated(order_id):
    """Maneja el pago simulado para pruebas."""
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.idUser:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('cart.view_cart'))

    if request.method == 'POST':
        # Simular procesamiento de pago
        import time
        time.sleep(2)  # Simular delay de procesamiento

        # Marcar orden como pagada
        order.status = 'pagado'
        db.session.commit()

        # Procesar carrito solo si el pedido no tiene detalles
        if not order.details:
            cart = Cart.query.filter_by(user_id=current_user.idUser).first()
            if cart:
                for item in cart.items:
                    detail = OrderDetail(
                        order_id=order.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        price=item.price_snapshot
                    )
                    db.session.add(detail)
                    product = Product.query.get(item.product_id)
                    if product:
                        product.stock = max(0, product.stock - item.quantity)
                    db.session.delete(item)
                db.session.delete(cart)
        else:
            # Si el pedido ya tiene detalles, reducir stock de los productos
            for detail in order.details:
                product = Product.query.get(detail.product_id)
                if product:
                    product.stock = max(0, product.stock - detail.quantity)

        db.session.commit()

        flash('Pago simulado exitoso. ¡Gracias por tu compra!', 'success')
        return redirect(url_for('orders.detail', order_id=order.id))

    return render_template('cart/payment_simulated.html', order=order)
