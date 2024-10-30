from flask import Blueprint, render_template

seller_bp  = Blueprint('seller', __name__)

@seller_bp.route('/dashboard')
def dashboard():
  ...

@seller_bp.route('/my-orders')
def my_orders():
  ...

@seller_bp.route('/my-products')
def my_products():
  ...

@seller_bp.route('/profile')
def profile():
  ...