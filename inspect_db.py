import sqlite3

# Ruta a la base de datos
DB_PATH = 'instance/flaskdb.sqlite'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print('Tablas en la base de datos:')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f'\nTabla: {table[0]}')
    cursor.execute(f'PRAGMA table_info({table[0]});')
    columns = cursor.fetchall()
    print('Columnas:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    cursor.execute(f'SELECT COUNT(*) FROM {table[0]};')
    count = cursor.fetchone()[0]
    print(f'Registros: {count}')

conn.close()
