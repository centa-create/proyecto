#!/usr/bin/env python3
"""
Script para probar el envío de emails.
Ejecuta: python test_email.py
"""

import os
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuración de correo desde variables de entorno
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

with app.app_context():
    try:
        msg = Message(
            'Prueba de Email',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=['eloronegro2023@gmail.com']  # Cambia a tu email de prueba
        )
        msg.body = 'Este es un email de prueba para verificar la configuración de Flask-Mail.'
        msg.html = '<p>Este es un email de <strong>prueba</strong> para verificar la configuración.</p>'

        mail.send(msg)
        print("✅ Email enviado exitosamente!")
    except Exception as e:
        print(f"❌ Error enviando email: {e}")