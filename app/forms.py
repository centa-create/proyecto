
"""
Formularios de la aplicación de e-commerce.

Este módulo contiene todos los formularios WTForms utilizados en la aplicación
para validación de entrada de usuarios, productos, categorías y configuraciones.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, SubmitField,
    DecimalField, IntegerField, SelectField, FileField,
    EmailField, DateField, BooleanField
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional


class LoginForm(FlaskForm):
    """Formulario para inicio de sesión de usuarios."""

    email = EmailField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')


class RegisterForm(FlaskForm):
    """Formulario para registro de nuevos usuarios."""

    name = StringField('Nombre completo', validators=[DataRequired(), Length(min=2, max=80)])
    email = EmailField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirmar contraseña',
        validators=[DataRequired(), EqualTo('password')]
    )
    birthdate = DateField('Fecha de nacimiento', validators=[DataRequired()])
    accept_terms = BooleanField(
        'Acepto los términos y condiciones',
        validators=[DataRequired()]
    )
    submit = SubmitField('Registrarse')


class ProfileForm(FlaskForm):
    """Formulario para edición de perfil de usuario."""

    name = StringField('Nombre completo', validators=[DataRequired(), Length(min=2, max=80)])
    email = EmailField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Nueva contraseña', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirmar nueva contraseña',
        validators=[EqualTo('password')]
    )
    profile_pic = FileField('Foto de perfil')
    submit = SubmitField('Actualizar perfil')


class ProductForm(FlaskForm):
    """Formulario para creación y edición de productos."""

    name = StringField('Nombre', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    price = DecimalField('Precio', validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    image = FileField('Imagen')
    size = StringField('Talla', validators=[Optional(), Length(max=20)])
    color = StringField('Color', validators=[Optional(), Length(max=30)])
    category_id = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Agregar producto')


class CategoryForm(FlaskForm):
    """Formulario para creación y edición de categorías."""

    name = StringField('Nombre', validators=[DataRequired(), Length(min=1, max=50)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Agregar categoría')


class DiscountForm(FlaskForm):
    """Formulario para aplicar descuentos a productos."""

    discount = IntegerField(
        'Descuento (%)',
        validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    submit = SubmitField('Aplicar descuento')


class CouponForm(FlaskForm):
    """Formulario para creación y edición de cupones de descuento."""

    code = StringField('Código', validators=[DataRequired(), Length(min=1, max=20)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=255)])
    discount_percent = DecimalField(
        'Descuento (%)',
        validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    valid_from = DateField('Válido desde', validators=[DataRequired()])
    valid_to = DateField('Válido hasta', validators=[DataRequired()])
    usage_limit = IntegerField('Límite de uso', validators=[Optional(), NumberRange(min=1)])
    product_id = SelectField('Producto específico', coerce=int, validators=[Optional()])
    category_id = SelectField('Categoría específica', coerce=int, validators=[Optional()])
    submit = SubmitField('Crear cupón')


class SupportTicketForm(FlaskForm):
    """Formulario para creación de tickets de soporte."""

    subject = StringField('Asunto', validators=[DataRequired(), Length(min=5, max=100)])
    message = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Enviar ticket')


class BannerForm(FlaskForm):
    """Formulario para creación y edición de banners."""

    title = StringField('Título', validators=[DataRequired(), Length(min=1, max=100)])
    link = StringField('Enlace', validators=[Optional(), Length(max=255)])
    image = FileField('Imagen', validators=[DataRequired()])
    active = BooleanField('Activo')
    submit = SubmitField('Crear banner')


class StoreConfigForm(FlaskForm):
    """Formulario para configuración general de la tienda."""

    nombre_tienda = StringField(
        'Nombre de la tienda',
        validators=[DataRequired(), Length(max=100)]
    )
    email_contacto = EmailField(
        'Email de contacto',
        validators=[DataRequired(), Email()]
    )
    horario = StringField('Horario', validators=[Optional(), Length(max=100)])
    mensaje_bienvenida = TextAreaField(
        'Mensaje de bienvenida',
        validators=[Optional(), Length(max=500)]
    )
    color_principal = StringField(
        'Color principal',
        validators=[Optional(), Length(max=7)]
    )  # Para códigos hex
    submit = SubmitField('Guardar configuración')
