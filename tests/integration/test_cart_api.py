"""
Tests de integración para las APIs del carrito de compras.
"""

import json
from datetime import date

import pytest

from app import create_app
from app.db import db
from app.models.products import Product
from app.models.users import Users


class TestCartAPI:
    """Tests para las APIs del carrito de compras."""

    @pytest.fixture
    def app(self):
        """Fixture para crear la aplicación de testing."""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    @pytest.fixture
    def client(self, app):
        """Fixture para el cliente de testing."""
        with app.app_context():
            db.create_all()
            yield app.test_client()
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def auth_headers(self, client):
        """Fixture para crear un usuario autenticado y obtener headers."""
        # Crear usuario de prueba
        user = Users(
            nameUser='Test User',
            email='test@example.com',
            password_user='hashed_password',
            birthdate=date(1990, 1, 1)
        )
        user.is_active_db = True
        db.session.add(user)
        db.session.commit()

        # Simular login (en una implementación real usarías tokens JWT o sesiones)
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.idUser)

        return {'user_id': str(user.idUser)}

    @pytest.fixture
    def sample_product(self):
        """Fixture para crear un producto de prueba."""
        product = Product(
            name='Test Product',
            price=100.0,
            description='Test description',
            category_id=1,
            size='M',
            color='Blue',
            stock=10
        )
        db.session.add(product)
        db.session.commit()
        return product

    def test_get_cart_empty(self, client, auth_headers):
        """Test obtener carrito vacío."""
        response = client.get('/api/cart/', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'items' in data
        assert 'total' in data
        assert len(data['items']) == 0
        assert data['total'] == 0

    def test_add_item_to_cart(self, client, auth_headers, sample_product):
        """Test agregar item al carrito."""
        data = {
            'product_id': sample_product.id,
            'quantity': 2
        }

        response = client.post('/api/cart/add',
                             json=data,
                             headers=auth_headers)

        assert response.status_code == 200
        response_data = json.loads(response.data)

        assert 'success' in response_data
        assert response_data['success'] is True

    def test_update_cart_item(self, client, auth_headers, sample_product):
        """Test actualizar cantidad de item en carrito."""
        # Primero agregar item
        client.post('/api/cart/add',
                   json={'product_id': sample_product.id, 'quantity': 1},
                   headers=auth_headers)

        # Luego actualizar cantidad
        update_data = {
            'item_id': 1,  # Asumiendo que el item tiene ID 1
            'quantity': 3
        }

        response = client.post('/api/cart/update',
                             json=update_data,
                             headers=auth_headers)

        assert response.status_code == 200

    def test_remove_item_from_cart(self, client, auth_headers, sample_product):
        """Test remover item del carrito."""
        # Primero agregar item
        client.post('/api/cart/add',
                   json={'product_id': sample_product.id, 'quantity': 1},
                   headers=auth_headers)

        # Luego remover
        remove_data = {'item_id': 1}

        response = client.post('/api/cart/remove',
                             json=remove_data,
                             headers=auth_headers)

        assert response.status_code == 200

    def test_cart_api_invalid_product(self, client, auth_headers):
        """Test agregar producto inexistente al carrito."""
        data = {
            'product_id': 99999,  # ID inexistente
            'quantity': 1
        }

        response = client.post('/api/cart/add',
                             json=data,
                             headers=auth_headers)

        assert response.status_code == 404

    def test_cart_api_invalid_quantity(self, client, auth_headers, sample_product):
        """Test agregar cantidad inválida al carrito."""
        data = {
            'product_id': sample_product.id,
            'quantity': -1  # Cantidad negativa
        }

        response = client.post('/api/cart/add',
                             json=data,
                             headers=auth_headers)

        assert response.status_code == 400

    def test_cart_api_insufficient_stock(self, client, auth_headers, sample_product):
        """Test agregar más cantidad de la disponible en stock."""
        data = {
            'product_id': sample_product.id,
            'quantity': sample_product.stock + 1
        }

        response = client.post('/api/cart/add',
                              json=data,
                              headers=auth_headers)

        assert response.status_code == 400
