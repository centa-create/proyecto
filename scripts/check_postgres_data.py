#!/usr/bin/env python3
"""
Script para verificar datos en PostgreSQL.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.db import db
from app.models.users import Users
from app.models.products import Category, Product

def check_data():
    """Verifica que los datos básicos estén en PostgreSQL."""

    app = create_app()

    with app.app_context():
        print("Verificando datos en PostgreSQL...")

        # Verificar usuarios
        users = Users.query.all()
        print(f"Usuarios: {len(users)}")
        for user in users:
            print(f"  - {user.email} (rol: {user.role})")

        # Verificar categorías
        categories = Category.query.all()
        print(f"Categorias: {len(categories)}")
        for cat in categories:
            print(f"  - {cat.name}")

        # Verificar productos
        products = Product.query.all()
        print(f"Productos: {len(products)}")
        for prod in products:
            print(f"  - {prod.name} (${prod.price})")

if __name__ == '__main__':
    check_data()