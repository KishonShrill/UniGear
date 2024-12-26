from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, session, abort
from app.models.product import Product
from app.models.user import User
from app.models.order import Order
from app.forms import *
from app.models.order import Order
import math
import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from werkzeug.utils import secure_filename
from app import mysql

import sys

user_bp = Blueprint('user', __name__)


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
  form = LinkVerify()
  user = User.get_by_email(session['email'])
  
  total_items = Product.countOrdersWithEmail(user.user_email)
  items_per_page = 10
  total_pages = math.ceil(total_items / items_per_page)
  
  current_page  = int(request.args.get('page', 1))
  orders = Product.getOrdersWithEmail(user.user_email)
  return render_template('/user/my_orders.html', orders=orders, form=form, current_page=current_page, total_pages=total_pages   )

@user_bp.route('/user/my-orders/delete', methods=['POST','GET'])
@login_is_required
def delete_order():
    if request.method == 'POST':
        try:
            data = request.get_json()  # Parse the JSON body
            print(f"Received data: {data}")  # Log received data

            order_id = data.get('order_id')  # Extract product_id
            if not order_id:
                return jsonify({"error": "Order ID is required"}), 400
            print(f"\nOrder ID: {order_id}")
            
            
            picture = Order.fetchReceipt(order_id)
            if picture:
                old_public_id = picture.split('/')[-1]  # Get the filename
                old_public_id = '.'.join(old_public_id.split('.')[:-1])  # Remove the last extension
                print(f"Filename: {old_public_id}")
                cloudinary.api.delete_resources(old_public_id, resource_type="image", type="upload")
            print(f"Picture: {picture}")
            
            status = Order.deleteOrder(order_id)
            print(f"Status: {status}")
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Something went wrong"}), 500
    if request.method == 'GET':
        return abort(404)

@user_bp.route('/user/receipt/delete', methods=['POST'])
@login_is_required
def delete_receipt():
    try:
        data = request.get_json()  # Parse the JSON body
        print(f"Received data: {data}")  # Log received data
        
        picture = data.get('picture')  # Extract product_id
    
        if picture:
            old_public_id = picture.split('/')[-1]  # Get the filename
            old_public_id = '.'.join(old_public_id.split('.')[:-1])  # Remove the last extension
            result = cloudinary.api.delete_resources(old_public_id, resource_type="image", type="upload")
            print(f"Result: {result}")
        
        status = Order.deleteReceipt(picture)
        print(f"Delete Status: {status}")
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Receipt Del ERR: {e}")
        return jsonify({"error": e})

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

@user_bp.route('/user/my-orders/upload', methods=['POST'])
def upload_file():
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        order_id = request.form.get('order_id')
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not order_id:
            return jsonify({'error': 'No order ID provided'}), 400

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(file)
        cloudinary_url = upload_result['secure_url']
        
        # Save the URL to database
        save_proof_to_database(order_id, cloudinary_url)
        
        return jsonify({
            'success': True,
            'url': cloudinary_url
        }), 200
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def save_proof_to_database(order_id, cloudinary_url):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        query = "UPDATE ordered_by SET proof_of_payment = %s WHERE order_id = %s"
        cursor.execute(query, (cloudinary_url, order_id))
        mysql.connection.commit()
        print(f"Successfully saved proof of payment for order {order_id}")
        return True
    except Exception as e:
        print(f"Database error: {str(e)}")
        if cursor:
            mysql.connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()