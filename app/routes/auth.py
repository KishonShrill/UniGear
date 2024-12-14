from flask import Blueprint, render_template, redirect, url_for, flash, session, abort, request, session
from google.oauth2 import id_token
from google.auth.transport import requests
from app.models.user import *
from app.routes.website import *
from app.forms import *
import os


auth_bp = Blueprint('auth', __name__)


def login_is_required(function):
  def wrapper(*args, **kwargs):
    if "id" not in session:
      return abort(401)
    return function(*args, **kwargs)
  wrapper.__name__ = function.__name__  # Fixes Flask's view function name requirement
  return wrapper

def seller_required(function):
    def wrapper(*args, **kwargs):
        # Check if the user is logged in
        if "id" not in session:
            flash("You must be logged in to access this page.", "warning")
            return abort(401)
        
        # Retrieve the user's role from the session or database
        user_role = session.get('role')  # Assuming the role is stored in the session
        print(f"Role: {user_role}")
        
        if not user_role or user_role.lower() != "seller":
            flash("Access denied. Only sellers can access this page.", "danger")
            return abort(404)  # HTTP 403 Forbidden
        
        # If everything checks out, allow access
        return function(*args, **kwargs)
    
    wrapper.__name__ = function.__name__  # Fix Flask's view function name requirement
    return wrapper


@auth_bp.route('/sign-in')
def sign_in():
  form = LinkVerify()
  return render_template('sign_in.html', form=form)

# The route to render the sign-up page
@auth_bp.route('/sign-up')
def sign_up():
  form = SignUpForm()
  return render_template('sign_up.html', form=form)  # Pass the form to the template

@auth_bp.route('/sign-up2', methods=['GET', 'POST'])
def sign_up2():
  form = SignUpForm()
  if request.method == 'POST':
    # Check if password confirmation match
    if form.password.data != form.repassword.data:
      flash("Password confirmation don't match", "warning")
      return redirect(url_for('auth.sign_up'))
    
    # Handle form submission
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    return render_template('sign_up2.html', username=username, email=email, password=password, form=form)
  if request.method == 'GET':
    return redirect(url_for('auth.sign_up'))
  
@auth_bp.route('/sign-up/submit', methods=['GET', 'POST'])
def submit_sign_up():
  if request.method == 'POST':
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    city = request.form.get('city')
    barangay = request.form.get('barangay')
    street = request.form.get('address')
    contact = request.form.get('contact')
    
    # Combine the address
    address = f"{street}, {barangay}, {city}"
    
    # Check if user exists or create new one
    user = User.get_by_email(email)
    
    if not user:
      print(f"Debug: {username}, {email}, {password}, {contact}, {address}")
      user = User.create_from_website(username, email, password, contact, address)
      
    flash(f"Account created successfully...", "success")
    return redirect(url_for('auth.sign_in'))
  
  if request.method == "GET":
    abort(404)
  

@auth_bp.route('/auth/callback', methods=['POST'])
def callback():
  form = LinkVerify()
  if request.method == 'POST':
    # Simulate getting data from Google OAuth
    getEmail = request.form.get("email")
    getPassword = request.form.get("password")
    
    print(f"Email: {getEmail}")
    # Check if user exists or create new one
    user = User.get_by_email(getEmail)
    print(f"User: {user}")
    
    # Check if password is the same with database
    isLogin = user.verify_password(getPassword)
    if not isLogin:
      flash(f"Password does not match", "warning")
      return render_template('sign_in.html', form=form)
    
    # Store user info in the session
    session['id'] = user.user_id
    session['name'] = user.user_name
    session['email'] = user.user_email
    session['role'] = user.user_role
    session['org_id'] = user.org_id
    
    flash(f"Welcome {user.user_name}", "success")
    return redirect(url_for('website.explore'))
  
  if request.method == 'GET':
    return redirect(url_for('website.landing'))

@auth_bp.route('/auth/google_callback')
def google_callback():
  form = LinkVerify()
  # Get authorization code from the request
  token = request.args.get("credential")
  
  if not token:
    flash(f"Token is not being recieved properly.", "warning")
    print("No credential received in the callback.")
    return redirect(url_for('auth.sign_in', form=form))
  
  try:
    # Verify the token
    idinfo = id_token.verify_oauth2_token(
      token, 
      requests.Request(), 
      audience="888454362739-8khch6t2lesrhrevs4s22h739a9ek8gh.apps.googleusercontent.com",
      clock_skew_in_seconds=1000,  # Adjust the skew tolerance
      )
    
    # Store user info in the session
    session['name'] = idinfo.get('name')
    session['email'] = idinfo.get('email')
    session['picture'] = idinfo.get('picture')
    
    # Check if user exists or create new one
    user = User.get_by_email(idinfo.get('email'))
    print(f"Role: {user.user_role}")
    session['id'] = user.user_id
    print(f"User ID: {user.user_id}")
    session['role'] = user.user_role
    session['org_id'] = user.org_id
    
    # print(f"User: {user}")  # TODO: For debugging purposes only
    # print(f"I am a: {user.user_role}") # TODO: For debugging purposes only

    flash(f"Welcome {idinfo.get('name')}", "success")
    return redirect(url_for('website.explore'))
  except ValueError as ve:
    print(f"Token verification failed: {ve}")
    return "Invalid token", 400  # Token verification failed
  except Exception as e:
    print(f"Unexpected error: {e}")
    return "An error occurred during authentication. Please try again.", 500
  

@auth_bp.route('/logout')
def logout():
  # Clear session to log out
  session.clear()
  flash(f"User has logged out...", "success")
  return redirect(url_for('website.explore'))
