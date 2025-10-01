"""
Health check endpoints para monitoreo de la aplicación.

Este módulo proporciona endpoints para verificar el estado de salud
de la aplicación y sus dependencias.
"""

import time
from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Import opcional de psutil para métricas del sistema
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

# Import de base de datos
from app.db import db

health_bp = Blueprint('health', __name__)

# Timestamp de inicio de la aplicación
START_TIME = time.time()


@health_bp.route('/health')
def health_check():
    """
    Health check básico - verifica que la aplicación esté respondiendo.

    Returns:
        JSON con estado básico de la aplicación
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'samms-fo',
        'version': current_app.config.get('VERSION', '1.0.0')
    })


@health_bp.route('/ready')
def readiness_check():
    """
    Readiness check - verifica que la aplicación esté lista para recibir tráfico.

    Checks:
    - Database connection
    - Required services availability

    Returns:
        JSON con estado de readiness
    """
    checks = {
        'database': _check_database(),
        'memory': _check_memory(),
        'disk': _check_disk_space()
    }

    all_healthy = all(check['status'] == 'healthy' for check in checks.values())

    response = {
        'status': 'ready' if all_healthy else 'not ready',
        'timestamp': time.time(),
        'checks': checks
    }

    status_code = 200 if all_healthy else 503
    return jsonify(response), status_code


@health_bp.route('/metrics')
def metrics():
    """
    Métricas detalladas para monitoring.

    Returns:
        JSON con métricas del sistema y aplicación
    """
    uptime = time.time() - START_TIME

    return jsonify({
        'timestamp': time.time(),
        'uptime_seconds': uptime,
        'memory': {
            'used_mb': psutil.virtual_memory().used / 1024 / 1024,
            'available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'percentage': psutil.virtual_memory().percent
        },
        'cpu': {
            'percentage': psutil.cpu_percent(interval=1)
        },
        'disk': {
            'used_gb': psutil.disk_usage('/').used / 1024 / 1024 / 1024,
            'free_gb': psutil.disk_usage('/').free / 1024 / 1024 / 1024,
            'percentage': psutil.disk_usage('/').percent
        }
    })


def _check_database():
    """Verifica la conexión a la base de datos."""
    try:
        # Ejecuta una consulta simple
        db.session.execute(text('SELECT 1'))
        return {'status': 'healthy', 'message': 'Database connection OK'}
    except (SQLAlchemyError, ConnectionError) as e:
        return {'status': 'unhealthy', 'message': f'Database error: {str(e)}'}


def _check_memory():
    """Verifica el uso de memoria."""
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        return {'status': 'warning', 'message': f'High memory usage: {memory.percent}%'}
    return {'status': 'healthy', 'message': f'Memory usage: {memory.percent}%'}


def _check_disk_space():
    """Verifica el espacio en disco."""
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        return {'status': 'warning', 'message': f'Low disk space: {disk.percent}% used'}
    return {'status': 'healthy', 'message': f'Disk usage: {disk.percent}%'}