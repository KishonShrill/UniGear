from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, MultipleFileField
from wtforms import StringField, IntegerField, SubmitField, SelectField, ValidationError, PasswordField, DecimalField, TextAreaField
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

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    hook = StringField('Hook')
    type = SelectField('Type', choices=[('type1', 'Type 1'), ('type2', 'Type 2')])  # Adjust to your product types
    preorder = SelectField('Pre-order Type', choices=[('yes', 'Yes'), ('no', 'No')])  # Adjust as necessary
    selectedSizes = StringField('Sizes', validators=[DataRequired()])
    picture_urls = FileField('Upload Images', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
