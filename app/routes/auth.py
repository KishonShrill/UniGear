from flask import Blueprint, render_template, redirect, url_for, session, abort, request
from google.oauth2 import id_token
from google.auth.transport import requests
from app.models.user import User
import os


auth_bp = Blueprint('auth', __name__)


def login_is_required(function):
  def wrapper(*args, **kwargs):
    if "google_id" not in session:
      return abort(401)
    return function(*args, **kwargs)
  wrapper.__name__ = function.__name__  # Fixes Flask's view function name requirement
  return wrapper


@auth_bp.route('/sign-in')
def sign_in():
  return render_template('sign_in.html')

@auth_bp.route('/sign-up')
def sign_up():
  ...

@auth_bp.route('/auth/callback')
def callback():
  # Simulate getting data from Google OAuth
  id = 'some-google-id'
  name = 'John Doe'
  email = 'john.doe@gmail.com'
  contact = '09123456789'  # Prompt user to provide this data
  address = '123 Main St'  # Prompt user to provide this data
  
  # Check if user exists or create new one
  user = User.get_by_email(email)
  
  if not user:
    user = User.create_from_google(id, name, email, contact, address)
  ...

@auth_bp.route('/auth/google_callback')
def google_callback():
  # Get authorization code from the request
  token = request.args.get("credential")
  if token:
    try:
      # Verify the token
      idinfo = id_token.verify_oauth2_token(token, requests.Request(), "888454362739-8khch6t2lesrhrevs4s22h739a9ek8gh.apps.googleusercontent.com")
      
      # Store user info in the session
      session['google_id'] = idinfo.get('sub')  # Unique Google user ID
      session['name'] = idinfo.get('name')
      session['email'] = idinfo.get('email')
      session['picture'] = idinfo.get('picture')
      
      # Check if user exists or create new one
      user = User.get_by_email(idinfo.get('email'))
      
      if not user:
        user = User.create_from_google(idinfo.get('name'), idinfo.get('email'))

      return redirect(url_for('auth.protected_area'))
    except ValueError:
      return "Invalid token", 400  # Token verification failed
  return redirect(url_for('auth.sign_in'))


@auth_bp.route('/logout')
def logout():
  # Clear session to log out
  session.clear()
  return redirect(url_for('auth.sign_in'))
  

@auth_bp.route('/protected_area')
@login_is_required
def protected_area():
  return render_template('protected_auth.html')