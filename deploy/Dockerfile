# Utiliza una imagen oficial de Python como base
FROM python:3.13-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de requerimientos e instálalos
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto en el que corre la app (ajusta si usas otro puerto)
EXPOSE 8095

# Comando por defecto para ejecutar la aplicación (ajusta si usas otro archivo)
CMD ["python", "run.py"]
