from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, SubmitField, SelectField, ValidationError, PasswordField
from wtforms.validators import InputRequired, Length, DataRequired, Regexp

class ProductForm(FlaskForm):
  create_product = SubmitField()
  pre_order = SubmitField()

class LinkVerify(FlaskForm):
  log_in = SubmitField()
  
# Create a form class using Flask-WTF
class SignUpForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired()])
  email = StringField('Email', validators=[InputRequired()])
  password = PasswordField('Password', validators=[InputRequired()])
  repassword = PasswordField('Re-enter Password', validators=[InputRequired()])
