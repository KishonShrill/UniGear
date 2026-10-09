"""WTForms form definitions for UniGear."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    DecimalField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, InputRequired


class LinkVerify(FlaskForm):
    """Simple verification form with a submit button."""

    log_in = SubmitField()


class SignUpForm(FlaskForm):
    """User registration form."""

    username = StringField("Username", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    repassword = PasswordField("Re-enter Password", validators=[InputRequired()])


class ProductForm(FlaskForm):
    """Product creation and update form."""

    name = StringField("Product Name", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    hook = StringField("Hook")
    type = SelectField(
        "Type",
        choices=[("type1", "Type 1"), ("type2", "Type 2")],
    )
    preorder = SelectField(
        "Pre-order Type",
        choices=[("yes", "Yes"), ("no", "No")],
    )
    selectedSizes = StringField("Sizes", validators=[DataRequired()])
    picture_urls = FileField(
        "Upload Images",
        validators=[FileAllowed(["jpg", "png", "jpeg"], "Images only!")],
    )
