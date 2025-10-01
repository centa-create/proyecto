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

        if 'passwordUser' not in column_names:
            print("La columna passwordUser no existe en la base de datos")
            if 'password_user' in column_names:
                print("La columna password_user ya existe y es correcta")
                conn.close()
                return True
            else:
                print("Error: Ninguna columna de contraseña encontrada")
                conn.close()
                return False

        # Si passwordUser existe, proceder con la migración

        print("Iniciando migracion...")

        # Paso 1: Crear nueva columna si no existe
        if 'password_user' not in column_names:
            print("1. Creando nueva columna password_user...")
            cursor.execute("ALTER TABLE user ADD COLUMN password_user VARCHAR(128)")
        else:
            print("1. La columna password_user ya existe, saltando creación...")

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

        # Paso 4: Eliminar columna antigua (SQLite no soporta DROP COLUMN directamente, pero podemos recrear la tabla)
        print("4. Eliminando columna antigua passwordUser...")

        # Obtener la definición completa de la tabla
        cursor.execute("PRAGMA table_info(user)")
        columns_info = cursor.fetchall()

        # Crear nueva definición de tabla sin passwordUser
        new_columns = []
        for col in columns_info:
            if col[1] != 'passwordUser':
                col_def = f"{col[1]} {col[2]}"
                if col[3]:  # not null
                    col_def += " NOT NULL"
                if col[4]:  # default value
                    col_def += f" DEFAULT {col[4]}"
                if col[5]:  # primary key
                    col_def += " PRIMARY KEY"
                new_columns.append(col_def)

        new_table_def = f"CREATE TABLE user_new ({', '.join(new_columns)})"

        # Crear nueva tabla
        cursor.execute(new_table_def)

        # Copiar datos
        columns_to_copy = [col[1] for col in columns_info if col[1] != 'passwordUser']
        cursor.execute(f"INSERT INTO user_new ({', '.join(columns_to_copy)}) SELECT {', '.join(columns_to_copy)} FROM user")

        # Verificar
        cursor.execute("SELECT COUNT(*) FROM user_new")
        new_count = cursor.fetchone()[0]
        if new_count != count_original:
            print("Error: Datos no copiados correctamente a nueva tabla")
            conn.rollback()
            conn.close()
            return False

        # Eliminar tabla antigua y renombrar nueva
        cursor.execute("DROP TABLE user")
        cursor.execute("ALTER TABLE user_new RENAME TO user")

        # Paso 5: Confirmar cambios
        conn.commit()

        print("Migracion completada exitosamente!")
        print(f"   - Registros migrados: {count_with_data}")
        print("   - Nueva columna: password_user")
        print("   - Columna antigua: passwordUser (eliminada)")

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