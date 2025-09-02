from app import db
from datetime import datetime

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    subject = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), default='abierto')  # abierto, en_proceso, cerrado
    assigned_admin_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('Users', foreign_keys=[user_id])
    assigned_admin = db.relationship('Users', foreign_keys=[assigned_admin_id])
