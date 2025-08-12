import os
from app import create_app, db

app = create_app()

print("Directorio actual:", os.getcwd())
print("Existe carpeta instance:", os.path.isdir("instance"))
print("Permisos de escritura en instance:", os.access("instance", os.W_OK))
print("Contenido de instance:", os.listdir("instance"))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8095)))

