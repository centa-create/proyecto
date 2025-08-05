from app import db
from app.models.products import Product

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', backref='wishlists', lazy=True)
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_wishlist'),)
