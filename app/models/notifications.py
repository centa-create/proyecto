"""
Modelo de notificaciones.

Este módulo define el modelo para las notificaciones del sistema.
"""

from datetime import datetime

from app.db import db


class Notification(db.Model):
    """Modelo para las notificaciones del sistema."""
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    leida = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convierte la notificación a un diccionario."""
        return {
            'id': self.id,
            'mensaje': self.mensaje,
            'leida': self.leida,
            'fecha': self.fecha.strftime('%Y-%m-%d')
        }
