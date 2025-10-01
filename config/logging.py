"""
Configuración de logging estructurado para la aplicación.

Este módulo configura el sistema de logging con diferentes niveles
y formatos para desarrollo y producción.
"""

import os
import logging
import logging.config


def setup_logging(app):
    """
    Configura el sistema de logging para la aplicación Flask.

    Args:
        app: Instancia de la aplicación Flask
    """
    # Determinar el nivel de logging
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())

    # Configuración base del logging
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'json': {
                'format': ('{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                          '"logger": "%(name)s", "message": "%(message)s"}')
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'detailed',
                'filename': app.config.get('LOG_FILE', 'logs/app.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            'app': {
                'level': log_level,
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'werkzeug': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False
            },
            'sqlalchemy': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    }

    # Configuración especial para producción
    if app.config.get('FLASK_ENV') == 'production':
        logging_config['handlers']['file']['formatter'] = 'json'
        logging_config['handlers']['console']['formatter'] = 'json'

    # Aplicar configuración
    logging.config.dictConfig(logging_config)

    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/app.log'))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Logger principal de la aplicación
    env = app.config.get('FLASK_ENV')
    app.logger.info(f"Logging configurado - Nivel: {log_level} - Entorno: {env}")


def get_logger(name):
    """
    Obtiene un logger configurado para un módulo específico.

    Args:
        name: Nombre del módulo/logger

    Returns:
        Logger configurado
    """
    return logging.getLogger(f'app.{name}')


# Logger global para uso general
logger = get_logger('main')
