"""
Módulo de pruebas para los modelos de la aplicación.

Este módulo contiene pruebas unitarias para los modelos principales
de la aplicación: Users, Products y Orders.
"""

import datetime
import decimal

import pytest
from app import create_app, db
from app.models.orders import Order, OrderDetail
from app.models.products import Category, Product
from app.models.users import UserRole, Users


@pytest.fixture
def test_app():
    """Fixture que crea una aplicación de prueba."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_client(test_app):
    """Fixture que crea un cliente de prueba."""
    return test_app.test_client()


class TestUsersModel:
    """Pruebas para el modelo de usuarios."""

    def test_user_creation(self, test_app):
        """Prueba la creación básica de un usuario."""
        with test_app.app_context():
            user = Users(
                nameUser='Test User',
                email='test@example.com',
                passwordUser='hashedpassword',
                birthdate=datetime.date(1990, 1, 1)
            )
            db.session.add(user)
            db.session.commit()

            assert user.idUser is not None
            assert user.nameUser == 'Test User'
            assert user.email == 'test@example.com'
            assert user.role == UserRole.USER

    def test_user_password_hashing(self, test_app):
        """Prueba el hashing y verificación de contraseñas."""
        with test_app.app_context():
            user = Users(
                nameUser='Test User',
                email='test@example.com',
                passwordUser='plainpassword',
                birthdate=datetime.date(1990, 1, 1)
            )
            user.set_password('plainpassword')
            assert user.check_password('plainpassword')
            assert not user.check_password('wrongpassword')

    def test_user_is_active_property(self, test_app):
        with test_app.app_context():
            # Usuario activo
            user = Users(
                nameUser='Active User',
                email='active@example.com',
                passwordUser='password',
                birthdate='1990-01-01',
                is_active_db=True,
                is_blocked=False
            )
            assert user.is_active

            # Usuario bloqueado
            user.is_blocked = True
            assert not user.is_active

            # Usuario no verificado
            user.is_blocked = False
            user.is_active_db = False
            assert not user.is_active


class TestProductsModel:
    def test_product_creation(self, test_app):
        with test_app.app_context():
            category = Category(name='Test Category', description='Test Description')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                description='Test Description',
                price=29.99,
                stock=10,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            assert product.id is not None
            assert product.name == 'Test Product'
            assert product.price == decimal.Decimal('29.99')
            assert product.stock == 10

    def test_product_image_url(self, app):
        with test_app.app_context():
            category = Category(name='Test Category', description='Test Description')
            db.session.add(category)

            # Producto con imagen
            product_with_image = Product(
                name='Product with Image',
                description='Test',
                price=19.99,
                stock=5,
                image='test.jpg',
                category_id=category.id
            )
            assert product_with_image.image_url() == '/static/product_images/test.jpg'

            # Producto sin imagen
            product_without_image = Product(
                name='Product without Image',
                description='Test',
                price=19.99,
                stock=5,
                category_id=category.id
            )
            assert product_without_image.image_url() == '/static/logo.png'


class TestOrdersModel:
    def test_order_creation(self, app):
        with test_app.app_context():
            user = Users(
                nameUser='Order User',
                email='order@example.com',
                passwordUser='password',
                birthdate=datetime.date(1990, 1, 1)
            )
            db.session.add(user)
            db.session.commit()

            order = Order(
                user_id=user.idUser,
                total=59.98,
                status='pendiente'
            )
            db.session.add(order)
            db.session.commit()

            assert order.id is not None
            assert order.user_id == user.idUser
            assert order.total == 59.98
            assert order.status == 'pendiente'

    def test_order_detail_creation(self, app):
        with test_app.app_context():
            user = Users(
                nameUser='Detail User',
                email='detail@example.com',
                passwordUser='password',
                birthdate=datetime.date(1990, 1, 1)
            )
            category = Category(name='Test Category', description='Test')
            db.session.add_all([user, category])
            db.session.commit()

            product = Product(
                name='Detail Product',
                description='Test',
                price=19.99,
                stock=10,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            order = Order(user_id=user.idUser, total=19.99)
            db.session.add(order)
            db.session.commit()

            order_detail = OrderDetail(
                order_id=order.id,
                product_id=product.id,
                quantity=1,
                price=19.99
            )
            db.session.add(order_detail)
            db.session.commit()

            assert order_detail.id is not None
            assert order_detail.order_id == order.id
            assert order_detail.product_id == product.id
            assert order_detail.quantity == 1
            assert order_detail.price == 19.99 
