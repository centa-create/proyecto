#!/usr/bin/env python3
"""
Script para crear datos básicos en PostgreSQL.
Crea usuario admin y productos de ejemplo.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.db import db
from app.models.users import Users, UserRole
from app.models.products import Category, Product
from datetime import datetime

def create_basic_data():
    """Crea datos básicos: admin user y productos de ejemplo."""

    app = create_app()

    with app.app_context():
        print("Creando datos basicos en PostgreSQL...")

        # Crear usuario admin
        admin_user = Users(
            nameUser="Admin",
            email="admin@example.com",
            phone="1234567890",
            password_user="admin123",  # Se hasheará automáticamente
            birthdate=datetime(1990, 1, 1),
            is_active_db=True,
            accepted_terms=True,
            role='admin'  # Usar string directamente para evitar problemas con enum
        )
        admin_user.set_password("admin123")  # Hashear contraseña

        try:
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario admin creado: admin@example.com / admin123")
        except Exception as e:
            print(f"Usuario admin ya existe o error: {e}")
            db.session.rollback()

        # Crear categorías
        categories_data = [
            {"name": "Zapatillas", "description": "Calzado deportivo y casual"},
            {"name": "Ropa", "description": "Prendas de vestir"},
        ]

        for cat_data in categories_data:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"]
            )
            try:
                db.session.add(category)
                db.session.commit()
                print(f"Categoria creada: {cat_data['name']}")
            except Exception as e:
                print(f"Categoria {cat_data['name']} ya existe o error: {e}")
                db.session.rollback()

        # Crear productos de ejemplo
        products_data = [
            {
                "name": "Zapatillas Runner Pro",
                "description": "Zapatillas para running de alta performance",
                "price": 89.99,
                "stock": 10,
                "image": "runnerpro.jpg",
                "category_name": "Zapatillas"
            },
            {
                "name": "Zapatillas Urban Style",
                "description": "Zapatillas urbanas para uso diario",
                "price": 65.50,
                "stock": 15,
                "image": "urbanstyle.jpg",
                "category_name": "Zapatillas"
            }
        ]

        for prod_data in products_data:
            # Buscar categoría
            category = Category.query.filter_by(name=prod_data["category_name"]).first()
            if category:
                product = Product(
                    name=prod_data["name"],
                    description=prod_data["description"],
                    price=prod_data["price"],
                    stock=prod_data["stock"],
                    image=prod_data["image"],
                    category_id=category.id
                )
                try:
                    db.session.add(product)
                    db.session.commit()
                    print(f"Producto creado: {prod_data['name']}")
                except Exception as e:
                    print(f"Producto {prod_data['name']} ya existe o error: {e}")
                    db.session.rollback()
            else:
                print(f"No se encontro categoria: {prod_data['category_name']}")

        print("\nDatos basicos creados exitosamente!")
        print("\nCredenciales de admin:")
        print("Email: admin@example.com")
        print("Password: admin123")

if __name__ == '__main__':
    create_basic_data()