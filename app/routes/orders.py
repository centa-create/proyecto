from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.orders import Order, OrderDetail
from app.models.cart import Cart, CartItem
from app.models.products import Product

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.idUser).first()
    if not cart or not cart.items:
        flash('Tu carrito está vacío.', 'danger')
        return redirect(url_for('cart.view_cart'))
    total = sum(item.quantity * item.product.price for item in cart.items)
    order = Order(user_id=current_user.idUser, total=total, status='pendiente')
    db.session.add(order)
    db.session.commit()
    for item in cart.items:
        detail = OrderDetail(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
        db.session.add(detail)
        db.session.delete(item)
    db.session.commit()
    flash('Pedido realizado correctamente. (Simulación, falta pago real)', 'success')
    return redirect(url_for('orders.history'))

@orders_bp.route('/history')
@login_required
def history():
    orders = Order.query.filter_by(user_id=current_user.idUser).order_by(Order.created_at.desc()).all()
    return render_template('orders/history.html', orders=orders)

@orders_bp.route('/detail/<int:order_id>')
@login_required
def detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.idUser:
        flash('No tienes acceso a este pedido.', 'danger')
        return redirect(url_for('orders.history'))
    # Simulación: Si el usuario accede al detalle y el pedido está pendiente, lo marcamos como enviado y notificamos
    if order.status == 'pendiente':
        order.status = 'enviado'
        db.session.commit()
        # Crear notificación
        from app.models.notifications import Notification
        notif = Notification(user_id=current_user.idUser, mensaje=f'Tu pedido #{order.id} ha sido enviado.')
        db.session.add(notif)
        db.session.commit()
        # Emitir notificación en tiempo real por WebSocket
        from app import socketio
        socketio.emit('nueva_notificacion', {'mensaje': notif.mensaje}, room=None)
        return redirect(url_for('orders.history'))
    return render_template('orders/detail.html', order=order)

@orders_bp.route('/pay/<int:order_id>', methods=['GET', 'POST'])
@login_required
def pay(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.idUser:
        flash('No tienes acceso a este pedido.', 'danger')
        return redirect(url_for('orders.history'))

    # Si el pedido ya está pagado, redirigir al detalle
    if order.status == 'pagado':
        flash('Este pedido ya ha sido pagado.', 'info')
        return redirect(url_for('orders.detail', order_id=order.id))

    # Si el pedido no tiene detalles (creado desde simulación), intentar crearlos desde el carrito
    if not order.details:
        cart = Cart.query.filter_by(user_id=current_user.idUser).first()
        if cart and cart.items:
            # Crear detalles del pedido desde el carrito
            for item in cart.items:
                detail = OrderDetail(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price
                )
                db.session.add(detail)
            db.session.commit()

    if request.method == 'POST':
        # Redirigir a la pasarela de pago simulada
        return redirect(url_for('cart.payment_simulated', order_id=order.id))

    return render_template('orders/pay.html', order=order)
