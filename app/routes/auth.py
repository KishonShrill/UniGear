from flask import Blueprint, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sign-in')
def sign_in():
  return render_template('sign_in.html')


@auth_bp.route('/sign-up2', methods=['GET', 'POST'])
def sign_up2():
    if request.method == 'POST':
        # Handle form submission
        pass
    return render_template('sign_up2.html')


# Create a form class using Flask-WTF
class SignUpForm(FlaskForm):
    username = StringField('Username')
    email = StringField('Email')
    password = PasswordField('Password')
    repassword = PasswordField('Re-enter Password')

# The route to render the sign-up page
@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()  # Create an instance of the form
    
    if form.validate_on_submit():
        # Handle successful form submission (process data, etc.)
        return redirect(url_for('auth.sign_up2'))  # Redirect to sign-up2 page
    
    return render_template('sign_up.html', form=form)  # Pass the form to the template
