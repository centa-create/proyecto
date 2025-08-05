from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.reviews import Review

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@reviews_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    if not rating or rating < 1 or rating > 5:
        flash('La calificación debe ser entre 1 y 5.', 'danger')
        return redirect(url_for('catalog.product_detail', product_id=product_id))
    review = Review(user_id=current_user.idUser, product_id=product_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    flash('¡Gracias por tu reseña!', 'success')
    return redirect(url_for('catalog.product_detail', product_id=product_id))
