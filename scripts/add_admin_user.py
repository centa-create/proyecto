"""
Script para agregar usuarios de prueba y admin a la base de datos.
"""

from werkzeug.security import generate_password_hash

from app import db, create_app
from app.models.users import Users, UserRole

app = create_app()

with app.app_context():
    # Crear usuario admin si no existe
    admin = Users.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = Users(
            nameUser='Admin',
            email='admin@example.com',
            password_user=generate_password_hash('admin123'),
            role=UserRole.ADMIN,
            is_active_db=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Usuario admin creado: admin@example.com / admin123')
    else:
        print('Usuario admin ya existe.')

    # Crear usuario de prueba
    test_user = Users.query.filter_by(email='test@example.com').first()
    if not test_user:
        test_user = Users(
            nameUser='Usuario de Prueba',
            email='test@example.com',
            password_user=generate_password_hash('test123'),
            role=UserRole.USER,
            is_active_db=True
        )
        db.session.add(test_user)
        db.session.commit()
        print('Usuario de prueba creado: test@example.com / test123')
    else:
        print('Usuario de prueba ya existe.')
