from flask import Blueprint, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.reviews import Review
import os
from werkzeug.utils import secure_filename

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@reviews_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    image_path = None
    # Manejo de imagen
    if 'image' in request.files:
        image = request.files['image']
        if image and image.filename:
            filename = secure_filename(image.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'review_images')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            image.save(filepath)
            image_path = f'review_images/{filename}'
    if not rating or rating < 1 or rating > 5:
        flash('La calificación debe ser entre 1 y 5.', 'danger')
        return redirect(url_for('catalog.product_detail', product_id=product_id))
    review = Review(user_id=current_user.idUser, product_id=product_id, rating=rating, comment=comment, image_path=image_path)
    db.session.add(review)
    db.session.commit()
    flash('¡Gracias por tu reseña!', 'success')
    return redirect(url_for('catalog.product_detail', product_id=product_id))
