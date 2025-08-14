import os
import stripe
from flask import Blueprint, jsonify, request, current_app, url_for
from flask_login import login_required, current_user
from app import db
from app.models.cart import Cart, CartItem
from app.models.products import Product
from app.models.orders import Order, OrderDetail

cart_api_bp = Blueprint('cart_api', __name__, url_prefix='/api/cart')

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@cart_api_bp.route('/', methods=['GET'])
@login_required
def get_cart():
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
    data = request.json
    product_id = data.get('product_id')
    qty = int(data.get('quantity', 1))
    product = Product.query.get_or_404(product_id)
    if product.stock < qty:
        return jsonify({'error': 'Sin stock suficiente'}), 400
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart:
        cart = Cart(user_id=current_user.idUser)
        db.session.add(cart)
        db.session.commit()
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        item.quantity += qty
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=qty, price_snapshot=product.price)
        db.session.add(item)
    db.session.commit()
    return jsonify({'ok': True})

@cart_api_bp.route('/update', methods=['POST'])
@login_required
def update_item():
    data = request.json
    item_id = data['id']
    qty = int(data['quantity'])
    item = CartItem.query.filter_by(id=item_id).first_or_404()
    if item.cart.user_id != current_user.idUser:
        return jsonify({'error': 'Acceso denegado'}), 403
    if qty <= 0:
        db.session.delete(item)
    else:
        if item.product.stock < qty:
            return jsonify({'error': 'Sin stock suficiente'}), 400
        item.quantity = qty
        # Si el precio cambió, actualiza el snapshot
        if item.price_snapshot != item.product.price:
            item.price_snapshot = item.product.price
    db.session.commit()
    return jsonify({'ok': True})

@cart_api_bp.route('/remove', methods=['POST'])
@login_required
def remove_item():
    data = request.json
    item_id = data['id']
    item = CartItem.query.filter_by(id=item_id).first_or_404()
    if item.cart.user_id != current_user.idUser:
        return jsonify({'error': 'Acceso denegado'}), 403
    db.session.delete(item)
    db.session.commit()
    return jsonify({'ok': True})

@cart_api_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    items = cart.items if cart else []
    if not items:
        return jsonify({'error': 'Carrito vacío'}), 400
    line_items = []
    total = 0
    for item in items:
        line_items.append({
            'price_data': {
                'currency': 'cop',
                'product_data': {'name': item.product.name},
                'unit_amount': int(item.price_snapshot * 100)
            },
            'quantity': item.quantity
        })
        total += item.quantity * item.price_snapshot
    base_url = request.host_url.rstrip('/')
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=base_url + url_for('cart_api.checkout_success'),
        cancel_url=base_url + url_for('cart_api.checkout_cancel'),
        metadata={'user_id': str(current_user.idUser)}
    )
    order = Order(user_id=current_user.idUser, total=total, status='pendiente')
    db.session.add(order)
    db.session.commit()
    return jsonify({'sessionId': checkout_session.id, 'url': checkout_session.url})

@cart_api_bp.route('/success')
def checkout_success():
    return 'Pago recibido, regresando...'

@cart_api_bp.route('/cancel')
def checkout_cancel():
    return 'Pago cancelado'

# Webhook Stripe
webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        current_app.logger.error(f'Webhook signature failed: {e}')
        return '', 400
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = int(session['metadata']['user_id'])
        cart = Cart.query.filter_by(user_id=user_id).first()
        if cart:
            for item in cart.items:
                detail = OrderDetail(order_id=session['id'], product_id=item.product_id, quantity=item.quantity, price=item.price_snapshot)
                db.session.add(detail)
                product = Product.query.get(item.product_id)
                if product:
                    product.stock = max(0, product.stock - item.quantity)
                db.session.delete(item)
            db.session.delete(cart)
            db.session.commit()
    return '', 200
