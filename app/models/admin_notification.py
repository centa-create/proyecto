from app import db
from datetime import datetime

class AdminNotification(db.Model):
    __tablename__ = 'admin_notifications'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=True)  # null = global para todos los admins
