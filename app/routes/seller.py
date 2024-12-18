from flask import Blueprint, render_template, jsonify, request, session, flash, redirect, url_for, abort, Response
from decimal import Decimal
from datetime import datetime
from app.models.product import Product
from app.forms import *
from app.routes.auth import seller_required
from app.models.user import User

import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


seller_bp = Blueprint('seller', __name__)


# Seller Routes
# Seller Routes
# Seller Routes
def login_is_required(function):
  
  def wrapper(*args, **kwargs):
    if "id" not in session:
      return abort(401)
    return function(*args, **kwargs)
  wrapper.__name__ = function.__name__  # Fixes Flask's view function name requirement
  return wrapper

@seller_bp.route('/dashboard')
@seller_required
def dashboard():
  ...

@seller_bp.route('/seller/my-orders')
@seller_required
def my_orders():
  form = LinkVerify()
  orders = Product.getOrders(session['org_id'])
  print(orders)
  return render_template('/seller/my_orders.html', orders=orders)

@seller_bp.route('/seller/my-orders/export')
@seller_required
def export_my_orders():
  orders = Product.getOrders(session['org_id'])
  
  def generate():
    # CSV header
    header = ["Order", "Customer", "Total Cost", "Product", "Size", "Quantity", "Type", "Status", "Order Date"]
    yield ','.join(header) + '\n'

    # Convert each order to a row
    for order in orders:
        row = [
            str(order['Order']),                               # Convert integer to string
            order['Customer'],                                # String already
            f"{order['Total Cost']:.2f}",                     # Format Decimal as string
            order['Product'],                                 # String already
            order['Size'],                                    # String already
            str(order['Quantity']),                           # Convert integer to string
            "Time" if order['Type'] == 1 else "Order",        # Convert integer type to label
            "Paid" if order['Status'] == 1 else "Not Paid",        # Convert integer status to label
            order['Order Date'].strftime('%Y-%m-%d %H:%M:%S') # Format datetime to string
        ]
        yield ','.join(row) + '\n'

  # Return the CSV response
  return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=orders.csv"})

@seller_bp.route('/seller/my-products')
@seller_required
def my_products():
  products = Product.getProducts(session['org_id'])
  return render_template('/seller/my_products.html', products=products)

@seller_bp.route('/seller/my-products/delete', methods=['POST','GET'])
@login_is_required
def delete_product():
    if request.method == 'POST':
        try:
            data = request.get_json()  # Parse the JSON body
            print(f"Received data: {data}")  # Log received data

            product_id = data.get('product_id')  # Extract product_id
            if not product_id:
                return jsonify({"error": "Order ID is required"}), 400

            print(f"\nOrder ID: {product_id}")
            Product.delete(product_id)
            
            return None
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Something went wrong"}), 500
    if request.method == 'GET':
        return abort(404)

# Seller Profile Route
@seller_bp.route('/seller/profile', methods=['GET', 'POST'])
@seller_required 
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
            return redirect(url_for('seller.profile'))
        
        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for('seller.profile'))

    # Split the user_address into components for display
    if user and user.user_address:
        parts = user.user_address.split(", ")
        zipcode_street = parts[0] if len(parts) > 0 else ""
        barangay = parts[1] if len(parts) > 1 else ""
        city = parts[2] if len(parts) > 2 else ""
    else:
        zipcode_street, barangay, city = "", "", ""

    # Render the profile page with the current user data
    return render_template('seller/seller_profile.html', user=user, zipcode_street=zipcode_street, barangay=barangay, city=city)

  
# Product Creation Form Route
# Product Creation Form Route
# Product Creation Form Route
@seller_bp.route('/product/new')
@seller_required
def product_new():
  form = ProductForm()
  return render_template('/crud_blueprint/product_page-create.html', form=form)


@seller_bp.route('/product/new/submit', methods=['POST', 'GET'])
@seller_required
def product_new_submit():
  if request.method == 'POST':
    # Ensure you include CSRF protection checks here if needed
    try:
      name = request.form.get("name")
      price = request.form.get("price")
      description = request.form.get("description")
      hook = request.form.get("hook")
      product_type = request.form.get("type")
      preorder_type = request.form.get("preorder")
      selected_sizes = request.form.get("selectedSizes")
      picture_urls = request.files.getlist("picture_urls")
      date = request.form.get("preorderDate")
      number_of_days = request.form.get('number_of_days')
  
      print(f"Picture URLs: {picture_urls}")
      print(f"Number of files selected: {len(picture_urls)}")  # Debug the number of files selected
      print(f"Date: {date}")
      print(f"Days: {number_of_days}")

      if date == '': date = None
      sizes = selected_sizes.split(',')
      URLS = []
      
      
      # Checks for a valid form \/ \/ \/
      # Checks for a valid form \/ \/ \/
      # Checks for a valid form \/ \/ \/
      if int(preorder_type) == 1:
        if date == '':
          flash (f"Select which date to release...","warning")
          return redirect(url_for('seller.product_new'))
        
        if int(number_of_days) <= 6:
          flash (f"Please give a deadline of 1 week or more...","warning")
          return redirect(url_for('seller.product_new'))
      
      if len(name) == 0:
         flash (f"Enter a name for the product...","warning")
         return redirect(url_for('seller.product_new'))
      
      if not price.isdigit() or price.startswith("0"):
        flash("Enter a valid price for the product. Must not start with 0.", "warning")
        return redirect(url_for('seller.product_new'))
      
      if int(price) > 10000:
        flash("Product should be affordable for students...", "warning")
        return redirect(url_for('seller.product_new'))
       
      if len(description) <= 10:
         flash(f"A minimum of 100 characters for description...","warning")
         flash(f"Chracter Length: {len(description)}","info")
         return redirect(url_for('seller.product_new'))
       
      if product_type == '':
        flash (f"Pick atleast one size for product...","warning")
        return redirect(url_for('seller.product_new'))

      for picture in picture_urls:
         print (f"Name: {picture.filename}")

      if len(picture_urls) == 0:
         flash (f"You must submit one image: {str(e)}","Danger")
         return redirect(url_for('seller.product_new'))
      
      for picture in picture_urls:
         if picture.filename=='':
            flash(f"Upload at least one image", "Warning")
            return redirect(url_for('seller.product_new'))
          
      # Checks for a valid form /\ /\ /\
      # Checks for a valid form /\ /\ /\
      # Checks for a valid form /\ /\ /\
   
      print (f"Type: {preorder_type}")
         # Put product in the Database and get ID
      product = Product(product_name=name,
                        description=description,
                        hook=hook,
                        type=product_type,
                        price=price,
                        order_type=preorder_type,
                        seller_id=session.get('id'),
                        release_date=date
      )
      product.save()

      for size in sizes:
        product.add_product_sizes(size)


      # Handle file uploads
      for picture in picture_urls:
        cloudinary_url = ""

        filename = secure_filename(picture.filename)
        print(f"Filename of Photo: {filename}")

        # Upload to Cloudinary
        try:
          upload_result = cloudinary.uploader.upload(picture, public_id=filename)
          cloudinary_url = upload_result.get('secure_url')  # Get the URL of the uploaded image

          # Save the Cloudinary URL to the database for this product
          product.add_product_pictures(cloudinary_url)
          URLS.append(cloudinary_url)

          print(f"cloudinary_url: {cloudinary_url}")

        except Exception as e:
          flash(f"An error occurred during file upload: {str(e)}", "danger")
          return redirect(url_for('seller.product_new'))


      
      # TODO: Change return to redirect to dashboard page
      flash(f"Product created successfully!", "success")
# After successfully saving the product
      return redirect(url_for('website.merch_details', product_id=product.product_id))
    except Exception as e:
      # If there’s an error, return it as part of the JSON response
      return jsonify(success=False, error=str(e)), 400
    
  if request.method == 'GET':
    return abort(404)
  
@seller_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@seller_required
def product_edit(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for('seller.dashboard'))

    form = ProductForm(obj=product)
    product_pictures = product.get_product_pictures(product_id)  # List of existing picture URLs
    product_sizes = product.get_product_sizes(product_id)  # List of existing sizes

    if request.method == 'POST':
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        hook = request.form.get("hook")
        product_type = request.form.get("type")
        preorder_type = request.form.get("preorder")
        selected_sizes = request.form.get("selectedSizes")
        picture_urls = request.files.getlist("picture_urls")  # New pictures to upload
        slides_data = request.form.get("slidesData")

        if not name or not price or not description:
            flash("Name, price, and description are required.", "danger")
            return redirect(url_for('seller.product_edit', product_id=product_id))

        new_pictures = picture_urls
        current_picture_urls = product_pictures
        pictures_to_keep = [pic for pic in current_picture_urls if pic in [pic.filename for pic in picture_urls]]
        pictures_to_upload = pictures_to_keep + [pic for pic in new_pictures if pic not in pictures_to_keep]

        try:
            product.remove_product_picture(product_id)  # Remove previous pictures
        except Exception as e:
            flash(f"Error removing existing pictures: {str(e)}", "danger")
            return redirect(url_for('seller.product_edit', product_id=product_id))

        # Upload new and kept pictures
        for picture in pictures_to_upload:
            try:
                if isinstance(picture, FileStorage):
                    filename = secure_filename(picture.filename)
                    upload_result = cloudinary.uploader.upload(picture, public_id=filename)
                    cloudinary_url = upload_result.get('secure_url')
                    product.add_product_pictures(cloudinary_url)
                else:
                    product.add_product_pictures(picture)

            except Exception as e:
                flash(f"Error uploading picture {picture.filename if isinstance(picture, FileStorage) else picture}: {str(e)}", "danger")
                return redirect(url_for('seller.product_edit', product_id=product_id))

        # Update product details
        try:
            Product.update(
                product_id=product_id,
                product_name=name,
                description=description,
                hook=hook,
                type=product_type,
                price=price,
                order_type=preorder_type
            )

            sizes = selected_sizes.split(',') if selected_sizes else []
            product.clear_sizes(product_id)
            for size in sizes:
                product.add_product_sizes(size)

            flash("Product updated successfully!", "success")
            return redirect(url_for('website.merch_details', product_id=product.product_id))

        except Exception as e:
            flash(f"Error updating product: {str(e)}", "danger")
            return redirect(url_for('seller.product_edit', product_id=product_id))

    return render_template('crud_blueprint/product_page-edit.html', form=form, product=product,
                           product_pictures=product_pictures, product_sizes=product_sizes)
