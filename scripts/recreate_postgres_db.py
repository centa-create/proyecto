#!/usr/bin/env python3
"""
Script para recrear la base de datos PostgreSQL con el esquema corregido.
"""

import psycopg2
from psycopg2 import sql

# Configuración de conexión
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '2006'
}

DB_NAME = 'proyect'

def recreate_database():
    """Elimina y recrea la base de datos."""

    # Conectar a postgres (base de datos por defecto)
    conn = psycopg2.connect(**DB_CONFIG, dbname='postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Terminar conexiones activas a la base de datos
        cursor.execute(sql.SQL("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid()
        """), [DB_NAME])

        # Eliminar la base de datos si existe
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(DB_NAME)))
        print(f"Base de datos '{DB_NAME}' eliminada.")

        # Crear la base de datos
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"Base de datos '{DB_NAME}' creada.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    print("Base de datos recreada exitosamente.")

if __name__ == '__main__':
    recreate_database()