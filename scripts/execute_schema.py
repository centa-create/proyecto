#!/usr/bin/env python3
"""
Script para ejecutar el esquema SQL en PostgreSQL.
"""

import psycopg2

# Configuración de conexión
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '2006',
    'database': 'proyect'
}

def execute_schema():
    """Ejecuta el archivo de esquema SQL."""

    # Leer el archivo SQL
    with open('scripts/create_postgres_schema.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Conectar a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # Ejecutar el SQL
        cursor.execute(sql_content)
        conn.commit()
        print("Esquema ejecutado exitosamente!")

    except Exception as e:
        print(f"Error ejecutando esquema: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    execute_schema()