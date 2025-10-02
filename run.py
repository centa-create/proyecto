"""
SAMMS.FO - Tienda Virtual
Script principal para ejecutar la aplicación Flask.
"""

import os
from app import create_app, db

# Asegurar que el directorio instance existe
os.makedirs('instance', exist_ok=True)

app = create_app()

print("Directorio actual:", os.getcwd())
print("Existe carpeta instance:", os.path.isdir("instance"))
print("Permisos de escritura en instance:", os.access("instance", os.W_OK))
print("Contenido de instance:", os.listdir("instance"))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Configuración para Coolify y otros entornos de producción
    port = int(os.environ.get('PORT', 8095))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'

    if debug_mode:
        print(f"\n{'='*50}")
        print("SAMMS.FO - Servidor Iniciado")
        print(f"{'='*50}")
        print(f"URL Local: http://127.0.0.1:{port}")
        print(f"URL Red: http://0.0.0.0:{port}")
        print("Modo: Debug=True")
        print(f"Puerto: {port}")
        print(f"{'='*50}\n")

    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=port,
        threaded=True
    )
