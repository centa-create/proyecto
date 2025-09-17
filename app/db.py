"""
Módulo de base de datos.

Este módulo contiene la instancia de SQLAlchemy para evitar
importaciones circulares entre modelos y la aplicación principal.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()