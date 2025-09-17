"""
Modelo de lista de deseos.

Este módulo define el modelo para las listas de deseos de los usuarios.
"""

from app.db import db


class Wishlist(db.Model):
    """Modelo para las listas de deseos de los usuarios."""
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', backref='wishlists', lazy=True)
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_wishlist'),)
