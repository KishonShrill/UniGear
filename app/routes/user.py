from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, session, abort
from app.models.product import Product
from app.models.user import User
from app.forms import ProductForm

import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from werkzeug.utils import secure_filename


user_bp = Blueprint('user', __name__)


# User Route
# User Route
# User Route
def login_is_required(function):
  def wrapper(*args, **kwargs):
    if "id" not in session:
      return abort(401)
    return function(*args, **kwargs)
  wrapper.__name__ = function.__name__  # Fixes Flask's view function name requirement
  return wrapper

@user_bp.route('/user/my-orders')
@login_is_required
def my_orders():
  user = User.get_by_email(session['email'])
  orders = Product.getOrdersWithEmail(user.user_email)
  print(f"User: {user.user_email}")
  print(f"Orders: {orders}")
  return render_template('/user/my_orders.html', orders=orders)


@user_bp.route('/user/profile', methods=['GET', 'POST'])
@login_is_required 
def profile():
   # Mock user data (Replace this with data from your database)
    user = {
        "username": "Lavigne Kyottie",
        "email": "example@example.com",
        "phone": "123-456-7890",
        "city": "Manila",
        "barangay": "Sample Barangay",
        "address": "12345 Sample Street"
    }
    
    if request.method == 'POST':
        # Handle form submission here
        try:
            user['username'] = request.form.get('username')
            user['email'] = request.form.get('email')
            user['phone'] = request.form.get('phone')
            user['city'] = request.form.get('city')
            user['barangay'] = request.form.get('barangay')
            user['address'] = request.form.get('address')
            
            flash("Profile updated successfully!", "success")
            return redirect(url_for('user.profile'))
        
        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for('user.profile'))

    return render_template('user/user_profile.html', user=user)