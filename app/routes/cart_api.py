"""
API endpoints para la gestión del carrito de compras.

Este módulo proporciona rutas para agregar, actualizar, remover items del carrito,
y procesar pagos a través de PayU.
"""

import hashlib
import uuid

import requests
from flask import Blueprint, jsonify, request, current_app, url_for
from flask_login import login_required, current_user
from app import db
from app.models.cart import Cart, CartItem
from app.models.products import Product
from app.models.orders import Order, OrderDetail

cart_api_bp = Blueprint('cart_api', __name__, url_prefix='/api/cart')

@cart_api_bp.route('/', methods=['GET'])
@login_required
def get_cart():
    """Obtiene los items del carrito del usuario actual."""
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    items = cart.items if cart else []
    result = [
        {
            'id': item.id,
            'product_id': item.product_id,
            'name': item.product.name,
            'quantity': item.quantity,
            'price_snapshot': item.price_snapshot
        } for item in items
    ]
    total = sum(item['quantity'] * item['price_snapshot'] for item in result)
    return jsonify({'items': result, 'total': total})

@cart_api_bp.route('/add', methods=['POST'])
@login_required
def add_item():
    """Agrega un item al carrito."""
    data = request.json
    product_id = data.get('product_id')
    qty = int(data.get('quantity', 1))
    product = Product.query.get_or_404(product_id)
    if product.stock < qty:
        return jsonify({'success': False, 'message': 'Sin stock suficiente'}), 400
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart:
        cart = Cart(user_id=current_user.idUser)
        db.session.add(cart)
        db.session.commit()
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        item.quantity += qty
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=qty,
            price_snapshot=product.price
        )
        db.session.add(item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto eliminado del carrito.'})

@cart_api_bp.route('/update', methods=['POST'])
@login_required
def update_item():
    """Actualiza la cantidad de un item en el carrito."""
    data = request.json
    item_id = data['id']
    qty = int(data['quantity'])
    item = CartItem.query.filter_by(id=item_id).first_or_404()
    if item.cart.user_id != current_user.idUser:
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
    if qty <= 0:
        db.session.delete(item)
    else:
        if item.product.stock < qty:
            return jsonify({'success': False, 'message': 'Sin stock suficiente'}), 400
        item.quantity = qty
        # Si el precio cambió, actualiza el snapshot
        if item.price_snapshot != item.product.price:
            item.price_snapshot = item.product.price
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto actualizado en el carrito.'})

@cart_api_bp.route('/remove', methods=['POST'])
@login_required
def remove_item():
    """Remueve un item del carrito."""
    data = request.json
    item_id = data['id']
    item = CartItem.query.filter_by(id=item_id).first_or_404()
    if item.cart.user_id != current_user.idUser:
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto agregado al carrito.'})

@cart_api_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Crea una sesión de checkout con PayU."""
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    items = cart.items if cart else []
    if not items:
        return jsonify({'error': 'Carrito vacío'}), 400

    total = sum(item.quantity * item.price_snapshot for item in items)

    # Crear orden primero
    order = Order(user_id=current_user.idUser, total=total, status='pendiente')
    db.session.add(order)
    db.session.commit()

    # Configuración PayU
    api_key = current_app.config.get('PAYU_API_KEY')
    api_login = current_app.config.get('PAYU_API_LOGIN')
    merchant_id = current_app.config.get('PAYU_MERCHANT_ID')
    account_id = current_app.config.get('PAYU_ACCOUNT_ID')
    test_mode = current_app.config.get('PAYU_TEST_MODE', True)

    if not all([api_key, api_login, merchant_id, account_id]):
        return jsonify({'error': 'Configuración de PayU incompleta'}), 500

    # URLs de PayU
    base_url = (
        'https://sandbox.checkout.payulatam.com' if test_mode
        else 'https://checkout.payulatam.com'
    )
    response_url = (
        request.host_url.rstrip('/') +
        url_for('cart_api.checkout_success')
    )
    confirmation_url = (
        request.host_url.rstrip('/') +
        url_for('webhook.payu_webhook')
    )

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
        'extra1': str(order.id),  # ID de la orden para referencia
        'lng': 'es'
    }

    # Enviar a PayU
    try:
        response = requests.post(f'{base_url}/ppp-web-gateway-payu/', data=payu_data, timeout=30)
        if response.status_code == 200:
            # PayU redirige automáticamente, devolver la URL
            return jsonify({'url': response.url, 'order_id': order.id})
        else:
            current_app.logger.error(f'PayU error: {response.status_code} - {response.text}')
            return jsonify({'error': 'Error al procesar pago'}), 500
    except requests.RequestException as e:
        current_app.logger.error(f'PayU request failed: {e}')
        return jsonify({'error': 'Error de conexión con PayU'}), 500

@cart_api_bp.route('/success')
def checkout_success():
    """Página de éxito del checkout."""
    return 'Pago recibido, regresando...'

@cart_api_bp.route('/cancel')
def checkout_cancel():
    """Página de cancelación del checkout."""
    return 'Pago cancelado'

# Webhook PayU
webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook_bp.route('/payu', methods=['POST'])
def payu_webhook():
    """Webhook para procesar notificaciones de PayU."""
    # PayU envía datos por POST sin firma especial
    data = request.form

    # Verificar firma
    api_key = current_app.config.get('PAYU_API_KEY')
    merchant_id = data.get('merchant_id')
    reference_sale = data.get('reference_sale')
    value = data.get('value')
    currency = data.get('currency')
    state_pol = data.get('state_pol')
    sign = data.get('sign')

    # Recalcular firma
    signature_string = f"{api_key}~{merchant_id}~{reference_sale}~{value}~{currency}~{state_pol}"
    expected_sign = hashlib.md5(signature_string.encode('utf-8')).hexdigest()

    if sign != expected_sign:
        current_app.logger.error('PayU webhook signature mismatch')
        return 'ERROR', 400

    # Procesar pago aprobado
    if state_pol == '4':  # Aprobado
        # Extraer order_id de reference_sale (formato: ORDER_{order_id}_{random})
        try:
            order_id = int(reference_sale.split('_')[1])
        except (IndexError, ValueError):
            current_app.logger.error(f'Invalid reference_sale format: {reference_sale}')
            return 'ERROR', 400

        order = Order.query.get(order_id)
        if not order:
            current_app.logger.error(f'Order not found: {order_id}')
            return 'ERROR', 400

        # Marcar orden como pagada
        order.status = 'pagado'
        db.session.commit()

        # Procesar carrito (si existe)
        cart = Cart.query.filter_by(user_id=order.user_id).first()
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
            db.session.commit()

        current_app.logger.info(f'PayU payment approved for order {order_id}')

    return 'OK', 200
