#!/usr/bin/env python3
"""
Script para crear solo el usuario admin.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.db import db
from app.models.users import Users

def create_admin():
    """Crea usuario admin."""

    app = create_app()

    with app.app_context():
        print("Creando usuario admin...")

        # Verificar si ya existe
        existing_admin = Users.query.filter_by(email='admin@example.com').first()
        if existing_admin:
            print("Usuario admin ya existe")
            return

        # Crear usuario admin
        admin_user = Users(
            nameUser="Admin",
            email="admin@example.com",
            phone="1234567890",
            password_user="admin123",  # Se hasheará automáticamente
            birthdate=datetime(1990, 1, 1),
            is_active_db=True,
            accepted_terms=True,
            role='ADMIN'  # Usar mayúscula para PostgreSQL
        )
        admin_user.set_password("admin123")

        try:
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario admin creado: admin@example.com / admin123")
        except SQLAlchemyError as e:
            print(f"Error creando admin: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_admin()
