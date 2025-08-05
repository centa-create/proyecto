from app import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255))  # Nombre del archivo de imagen
    size = db.Column(db.String(20))
    color = db.Column(db.String(30))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    promo = db.Column(db.String(255))  # Texto de promoción, si aplica
    destacado = db.Column(db.Boolean, default=False)  # Si es producto destacado

    def image_url(self):
        """Devuelve la URL de la imagen del producto."""
        if self.image:
            return f"/static/product_images/{self.image}"
        return "/static/logo.png"
