from app.db import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    image_path = db.Column(db.String(256))  # Ruta de la imagen subida
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    aprobada = db.Column(db.Boolean, default=False)  # Moderación: solo reseñas aprobadas se muestran
