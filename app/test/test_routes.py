"""
Tests para rutas de la aplicación Flask.

Este módulo contiene pruebas para las rutas principales de autenticación,
administración y cliente, utilizando pytest y fixtures.
"""

from datetime import date

import pytest

from app import create_app, db
from app.models.users import Users, UserRole


@pytest.fixture
def app_fixture():
    """Fixture que crea una aplicación de prueba."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Deshabilitar CSRF para tests
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client_fixture(app_fixture):
    """Fixture que crea un cliente de prueba."""
    return app_fixture.test_client()


@pytest.fixture
def admin_user_fixture(app_fixture):
    """Fixture que crea un usuario administrador de prueba."""
    with app_fixture.app_context():
        admin = Users(
            nameUser='Admin User',
            email='admin@example.com',
            passwordUser='adminpass',
            birthdate=date(1980, 1, 1),
            role=UserRole.ADMIN,
            is_active_db=True
        )
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()
        return admin


@pytest.fixture
def regular_user_fixture(app_fixture):
    """Fixture que crea un usuario regular de prueba."""
    with app_fixture.app_context():
        user = Users(
            nameUser='Regular User',
            email='user@example.com',
            passwordUser='userpass',
            birthdate=date(1990, 1, 1),
            role=UserRole.USER,
            is_active_db=True
        )
        user.set_password('userpass')
        db.session.add(user)
        db.session.commit()
        return user


class TestAuthRoutes:
    """Tests para rutas de autenticación."""

    def test_login_page_loads(self, client):
        """Test que la página de login carga correctamente."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_successful_login(self, client, _regular_user):
        """Test de login exitoso."""
        response = client.post('/login', data={
            'email': 'user@example.com',
            'passwordUser': 'userpass'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Debería redirigir al feed
        assert b'feed' in response.data.lower() or b'productos' in response.data.lower()

    def test_failed_login(self, client):
        """Test de login fallido."""
        response = client.post('/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }, follow_redirects=True)
        assert response.status_code == 200
        # El formulario ahora usa validación de WTF, así que debería mostrar errores
        assert b'login' in response.data.lower()

    def test_logout(self, client, _regular_user):
        """Test de logout."""
        # Primero hacer login
        with client:
            client.post('/login', data={
                'email': 'user@example.com',
                'passwordUser': 'userpass'
            })
            # Luego logout
            response = client.get('/logout', follow_redirects=True)
            assert response.status_code == 200
            assert b'login' in response.data.lower()


class TestAdminRoutes:
    """Tests para rutas de administración."""

    def test_admin_dashboard_requires_login(self, client):
        """Test que el dashboard de admin requiere login."""
        response = client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_admin_dashboard_access_denied_for_regular_user(
        self, client, _regular_user
    ):
        """Test que usuario regular no puede acceder al dashboard de admin."""
        with client:
            client.post('/login', data={
                'email': 'user@example.com',
                'passwordUser': 'userpass'
            })
            response = client.get('/admin/dashboard', follow_redirects=True)
            assert response.status_code == 200
            assert (
                b'acceso denegado' in response.data.lower() or
                b'admin' not in response.data.lower()
            )

    def test_admin_dashboard_access_granted_for_admin(
        self, client, _admin_user
    ):
        """Test que admin puede acceder al dashboard."""
        with client:
            client.post('/login', data={
                'email': 'admin@example.com',
                'passwordUser': 'adminpass'
            })
            response = client.get('/admin/dashboard', follow_redirects=True)
            assert response.status_code == 200
            # Debería mostrar dashboard de admin
            assert (
                b'dashboard' in response.data.lower() or
                b'admin' in response.data.lower()
            )

    def test_admin_products_page(self, client, _admin_user):
        """Test que admin puede acceder a la página de productos."""
        with client:
            client.post('/login', data={
                'email': 'admin@example.com',
                'passwordUser': 'adminpass'
            })
            response = client.get('/admin/products')
            assert response.status_code == 200
            assert b'producto' in response.data.lower()

    def test_admin_users_page(self, client, _admin_user):
        """Test que admin puede acceder a la página de usuarios."""
        with client:
            client.post('/login', data={
                'email': 'admin@example.com',
                'passwordUser': 'adminpass'
            })
            response = client.get('/admin/dashboard')  # Dashboard muestra usuarios
            assert response.status_code == 200
            assert b'usuario' in response.data.lower()


class TestClientRoutes:
    """Tests para rutas de cliente."""

    def test_feed_page_loads(self, client):
        """Test que la página de feed carga correctamente."""
        response = client.get('/feed')
        assert response.status_code == 200
        assert (
            b'producto' in response.data.lower() or
            b'feed' in response.data.lower()
        )

    def test_root_redirects_to_feed(self, client):
        """Test que la raíz redirige al feed."""
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert b'feed' in response.data.lower()

    def test_profile_requires_login(self, client):
        """Test que el perfil requiere login."""
        response = client.get('/profile', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_profile_access_for_logged_user(self, client, _regular_user):
        """Test que usuario logueado puede acceder al perfil."""
        with client:
            client.post('/login', data={
                'email': 'user@example.com',
                'passwordUser': 'userpass'
            })
            response = client.get('/profile')
            assert response.status_code == 200
            assert (
                b'perfil' in response.data.lower() or
                b'profile' in response.data.lower()
            )


class TestErrorHandlers:
    """Tests para manejadores de errores."""

    def test_404_error_page(self, client):
        """Test que la página 404 funciona correctamente."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

    def test_500_error_page(self, client, app):
        """Test que la página 500 funciona correctamente."""
        # Forzar un error 500 creando una ruta temporal
        with app.app_context():
            @app.route('/test-error')
            def test_error():
                raise ValueError("Test error")

        response = client.get('/test-error')
        # Flask maneja errores 500 automáticamente
        assert response.status_code == 500

