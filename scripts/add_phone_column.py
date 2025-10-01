#!/usr/bin/env python3
"""
Script para agregar la columna 'phone' al modelo de usuario.
Ejecutar después de actualizar el modelo.
"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_phone_column():
    """Agrega la columna phone a la tabla user si no existe."""
    try:
        from app.db import db
        from app import create_app

        app = create_app()

        with app.app_context():
            from sqlalchemy import text

            # Verificar si la columna ya existe
            result = db.session.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result.fetchall()]

            if 'phone' not in columns:
                print("Agregando columna 'phone' a la tabla 'user'...")
                try:
                    # Primero agregar la columna sin restricción UNIQUE
                    db.session.execute(text("ALTER TABLE user ADD COLUMN phone VARCHAR(20)"))
                    db.session.commit()
                    print("✅ Columna 'phone' agregada (sin restricción UNIQUE).")

                    # Intentar agregar la restricción UNIQUE
                    try:
                        db.session.execute(text("CREATE UNIQUE INDEX idx_user_phone ON user(phone)"))
                        db.session.commit()
                        print("✅ Restricción UNIQUE agregada a la columna 'phone'.")
                    except Exception as e:
                        print(f"⚠️ No se pudo agregar restricción UNIQUE (posiblemente ya hay datos duplicados): {e}")
                        print("La columna 'phone' funciona pero permite valores duplicados.")

                except Exception as e:
                    print(f"❌ Error al agregar la columna: {e}")
            else:
                print("ℹ️ La columna 'phone' ya existe.")

    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de estar ejecutando desde la raíz del proyecto.")
        print("También verifica que todas las dependencias estén instaladas: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error al agregar la columna: {e}")

if __name__ == "__main__":
    add_phone_column()