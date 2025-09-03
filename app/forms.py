
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DecimalField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, NumberRange

class DiscountForm(FlaskForm):
    discount = IntegerField('Descuento (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Guardar')

class ProductForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    description = TextAreaField('Descripción')
    price = DecimalField('Precio', validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    image = FileField('Imagen')
    size = StringField('Talla')
    color = StringField('Color')
    category_id = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Agregar')
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class CategoryForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    description = TextAreaField('Descripción')
    submit = SubmitField('Agregar')
