#!/usr/bin/env python3
"""
Script para probar la conexión a PostgreSQL.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.db import db

def test_connection():
    """Prueba la conexión a PostgreSQL."""
    try:
        # Forzar configuración de desarrollo
        os.environ['FLASK_ENV'] = 'development'
        app = create_app()

        print("Probando conexion a PostgreSQL...")
        print(f"URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

        with app.app_context():
            # Intentar conectar
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("Conexion exitosa a PostgreSQL!")

            # Verificar tablas - usar consulta compatible con SQLite y PostgreSQL
            if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
                # PostgreSQL
                result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            else:
                # SQLite
                result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))

            tables = [row[0] for row in result]

            print(f"Tablas encontradas: {len(tables)}")
            for table in sorted(tables):
                print(f"  - {table}")

    except Exception as e:
        print(f"Error de conexion: {e}")
        print("\nPosibles soluciones:")
        print("1. Verifica que PostgreSQL este ejecutandose")
        print("2. Revisa las credenciales en config/development.py")
        print("3. Asegurate de que la base de datos 'proyect' existe")
        print("4. Verifica que psycopg2-binary este instalado")
        return False

    return True

if __name__ == '__main__':
    test_connection()