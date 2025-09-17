"""
Modelo de carrito de compras.

Este módulo define las clases para manejar el carrito de compras
y los items del carrito.
"""

from app.db import db


class Cart(db.Model):
    """Modelo para el carrito de compras de un usuario."""
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

class CartItem(db.Model):
    """Modelo para los items individuales del carrito de compras."""
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price_snapshot = db.Column(db.Float, nullable=False)  # Precio al añadir el producto
    __table_args__ = (db.UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),)
    # Relación para acceder al producto desde el item
    from app.models.products import Product
    product = db.relationship('Product', backref='cart_items', lazy=True, uselist=False, primaryjoin="CartItem.product_id==Product.id")
