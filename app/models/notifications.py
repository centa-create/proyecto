from app import db
from flask_login import current_user
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    leida = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'mensaje': self.mensaje,
            'leida': self.leida,
            'fecha': self.fecha.strftime('%Y-%m-%d')
        }
