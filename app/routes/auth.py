from flask import Blueprint, render_template, redirect, url_for, request
from app.forms import *


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/sign-in')
def sign_in():
  return render_template('sign_in.html')

# The route to render the sign-up page
@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()  # Create an instance of the form
    
    if form.validate_on_submit():
        # Handle successful form submission (process data, etc.)
        return redirect(url_for('auth.sign_up2'))  # Redirect to sign-up2 page
    
    return render_template('sign_up.html', form=form)  # Pass the form to the template

@auth_bp.route('/sign-up2', methods=['GET', 'POST'])
def sign_up2():
    if request.method == 'POST':
        # Handle form submission
        pass
    return render_template('sign_up2.html')