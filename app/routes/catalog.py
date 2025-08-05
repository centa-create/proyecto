
from flask import Blueprint, render_template, request
from flask_login import current_user
from app.models.products import Product, Category
from app.models.wishlist import Wishlist
from app import cache
@catalog_bp.route('/destacados')
@cache.cached(timeout=300)
def destacados():
    products = Product.query.filter_by(destacado=True).order_by(Product.created_at.desc()).limit(12).all()
    return render_template('catalog/catalog.html', products=products, categories=Category.query.all(), favoritos=[], pagination=None)

catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalog')

@catalog_bp.route('/')
def catalog():
    category_id = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Número de productos por página
    if category_id:
        products_query = Product.query.filter_by(category_id=category_id)
    else:
        products_query = Product.query
    products_pagination = products_query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()
    favoritos = []
    if hasattr(current_user, 'idUser'):
        favoritos = [w.product_id for w in Wishlist.query.filter_by(user_id=current_user.idUser).all()]
    return render_template('catalog/catalog.html', products=products_pagination.items, categories=categories, favoritos=favoritos, pagination=products_pagination)

from app.models.reviews import Review
from app.models.users import Users

@catalog_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    from app.models.wishlist import Wishlist
    favoritos = []
    if hasattr(current_user, 'idUser'):
        favoritos = [w.product_id for w in Wishlist.query.filter_by(user_id=current_user.idUser).all()]
    # Obtener reseñas del producto
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    # Enriquecer con nombre de usuario
    reviews_data = []
    for r in reviews:
        user = Users.query.get(r.user_id)
        reviews_data.append({
            'user_name': user.nameUser if user else 'Usuario',
            'rating': r.rating,
            'comment': r.comment,
            'date': r.created_at
        })
    return render_template('catalog/product_detail.html', product=product, reviews=reviews_data, favoritos=favoritos)
