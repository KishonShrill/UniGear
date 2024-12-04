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