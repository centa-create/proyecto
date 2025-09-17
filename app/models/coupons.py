from app.db import db
from datetime import datetime

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    discount_percent = db.Column(db.Float, nullable=False)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True)
    usage_limit = db.Column(db.Integer, nullable=True)  # None = ilimitado
    used_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Opcional: asignar a producto/categoría
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
