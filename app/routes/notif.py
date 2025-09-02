
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.notifications import Notification
from datetime import datetime

notif_bp = Blueprint('notif', __name__, url_prefix='/notificaciones')

@notif_bp.route('/api/check', methods=['GET'])
@login_required
def check_new():
    # Devuelve la notificación más reciente no leída
    notif = Notification.query.filter_by(user_id=current_user.idUser, leida=False).order_by(Notification.fecha.desc()).first()
    if notif:
        return jsonify({'new': True, 'mensaje': notif.mensaje, 'id': notif.id})
    return jsonify({'new': False})


def get_user_notifs():
    notifs = Notification.query.filter_by(user_id=current_user.idUser).order_by(Notification.fecha.desc()).all()
    return [n.to_dict() for n in notifs]


@notif_bp.route('/')
@login_required
def lista():
    return render_template('client/notificaciones.html', notifs=get_user_notifs())


@notif_bp.route('/marcar_leida/<int:notif_id>', methods=['POST'])
@login_required
def marcar_leida(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.idUser).first()
    if notif:
        notif.leida = True
        db.session.commit()
    return jsonify({'ok': True})


@notif_bp.route('/eliminar/<int:notif_id>', methods=['POST'])
@login_required
def eliminar(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.idUser).first()
    if notif:
        db.session.delete(notif)
        db.session.commit()
    return jsonify({'ok': True})
