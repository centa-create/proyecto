#!/usr/bin/env python3
"""
Script de migración para renombrar la columna passwordUser a password_user
en la base de datos SQLite existente.
"""

import sqlite3
import os

def migrate_password_column():
    """Migra la columna passwordUser a password_user en SQLite."""

    db_path = os.path.join('instance', 'flaskdb.sqlite')

    if not os.path.exists(db_path):
        print("Base de datos no encontrada en instance/flaskdb.sqlite")
        return False

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Verificando estructura de la tabla user...")

        # Verificar la estructura actual
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'password_user' in column_names:
            print("La columna password_user ya existe")
            conn.close()
            return True

        if 'passwordUser' not in column_names:
            print("La columna passwordUser no existe en la base de datos")
            conn.close()
            return False

        print("Iniciando migracion...")

        # Paso 1: Crear nueva columna
        print("1. Creando nueva columna password_user...")
        cursor.execute("ALTER TABLE user ADD COLUMN password_user VARCHAR(128)")

        # Paso 2: Copiar datos
        print("2. Copiando datos de passwordUser a password_user...")
        cursor.execute("UPDATE user SET password_user = passwordUser")

        # Paso 3: Verificar que los datos se copiaron correctamente
        cursor.execute("SELECT COUNT(*) FROM user WHERE password_user IS NOT NULL")
        count_with_data = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user WHERE passwordUser IS NOT NULL")
        count_original = cursor.fetchone()[0]

        if count_with_data != count_original:
            print("Error: Los datos no se copiaron correctamente")
            conn.rollback()
            conn.close()
            return False

        # Paso 4: Confirmar cambios
        conn.commit()

        print("Migracion completada exitosamente!")
        print(f"   - Registros migrados: {count_with_data}")
        print("   - Nueva columna: password_user")
        print("   - Columna antigua: passwordUser (aun existe)")

        conn.close()
        return True

    except Exception as e:
        print(f"Error durante la migracion: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("Iniciando migracion de columna passwordUser -> password_user")
    print("=" * 60)

    success = migrate_password_column()

    if success:
        print("\nMigracion completada exitosamente!")
        print("Ahora puedes ejecutar la aplicacion con: .venv\\Scripts\\python run.py")
    else:
        print("\nLa migracion fallo. Revisa los errores arriba.")

    print("=" * 60)