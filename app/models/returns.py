from app import db
from datetime import datetime

class ReturnRequest(db.Model):
    __tablename__ = 'return_requests'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(32), default='pendiente')  # pendiente, aprobado, rechazado, reembolsado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    refund_amount = db.Column(db.Float, nullable=True)

    order = db.relationship('Order', backref='return_requests')
    user = db.relationship('Users', backref='return_requests')
