
"""
Módulo de rutas de reseñas.

Este módulo maneja todas las rutas relacionadas con las reseñas
de productos: mostrar reseñas, agregar reseñas, etc.
"""

from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/reviews')
def reviews_home():
    """Mostrar la página principal de reseñas."""
    return 'Página de reseñas'

# Nueva ruta para agregar reseña
@reviews_bp.route('/reviews/add/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    """Agregar una nueva reseña para un producto."""
    # Aquí deberías procesar y guardar la reseña en la base de datos
    # Por ahora solo redirige y muestra un mensaje
    flash('Reseña enviada (funcionalidad demo).', 'success')
    return redirect(url_for('catalog.product_detail', product_id=product_id))
