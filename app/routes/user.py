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
    # Fetch user data from the database
    user = User.get_by_email(session['email'])
    
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('user.profile'))

    # Handle form submission
    if request.method == 'POST':
        try:
            # Get form data
            user.user_name = request.form.get('username')
            user.user_email = request.form.get('email')
            user.user_contact = request.form.get('phone')
            user.user_address = request.form.get('address')
            user.user_role = request.form.get('role')  # If applicable
            user.org_id = request.form.get('org_id')  # If applicable
            # Save updated user data to the database
            user.save()

            flash("Profile updated successfully!", "success")
            return redirect(url_for('user.profile'))
        
        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for('user.profile'))

    # Split the user_address into components for display
    if user and user.user_address:
        parts = user.user_address.split(", ")
        zipcode_street = parts[0] if len(parts) > 0 else ""
        barangay = parts[1] if len(parts) > 1 else ""
        city = parts[2] if len(parts) > 2 else ""
    else:
        zipcode_street, barangay, city = "", "", ""

    # Render the profile page with the current user data
    return render_template('user/user_profile.html', user=user, zipcode_street=zipcode_street, barangay=barangay, city=city)
