from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, SubmitField, SelectField, ValidationError
from wtforms.validators import InputRequired, Length, DataRequired, Regexp

class ProductForm(FlaskForm):
  create_product = SubmitField()