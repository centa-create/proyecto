# ===== DOCKERFILE PARA COOLIFY =====
# Utiliza una imagen oficial de Python como base
FROM python:3.13-slim

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos e instálalos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs instance

# Configurar permisos
RUN chmod +x run.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expone el puerto dinámico de Coolify
EXPOSE $PORT

# Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "4", "--threads", "2", "run:app"]