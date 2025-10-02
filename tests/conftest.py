"""
Configuración de fixtures para pruebas con pytest.
"""

import pytest

from app import create_app, db
from app.models.users import Users


@pytest.fixture
def app():
    """Fixture que proporciona la aplicación Flask para pruebas."""
    app_instance = create_app()
    with app_instance.app_context():
        db.create_all()  # Create tables within the context
        yield app_instance
        db.session.remove()  # Cleanup session objects
        db.drop_all()


@pytest.fixture
def client(app_fixture):
    """Fixture que proporciona un cliente de prueba para la aplicación."""
    return app_fixture.test_client()


@pytest.fixture
def user(app_fixture):
    """Fixture que proporciona un usuario de prueba."""
    user_instance = Users(nameUser="test_user", password_user="test_password")
    db.session.add(user_instance)
    db.session.commit()  # Commit changes within the context
    yield user_instance
    # Cleanup changes within the context