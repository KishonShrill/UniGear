from flask import Blueprint, render_template, jsonify, request, session, flash, redirect, url_for, abort, Response
from app.models.product import Product
from app.forms import *
from app.routes.auth import seller_required
from app.models.user import User
from app.models.order import Order
import math

import os
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


@seller_bp.route('/seller/my-orders')
@seller_required
def my_orders():
  total_items = Product.countOrders(session['org_id'])
  items_per_page = 10
  total_pages = math.ceil(total_items / items_per_page)
  
  current_page  = int(request.args.get('page', 1))
  orders = Product.getOrdersInPage(session['org_id'], current_page)
  return render_template('/seller/my_orders.html', orders=orders, current_page=current_page, total_pages=total_pages)
  

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

@seller_bp.route('/seller/my-orders/delete', methods=['POST','GET'])
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
            Order.deleteOrder(order_id)
            
            return None
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Something went wrong"}), 500
    if request.method == 'GET':
        return abort(404) 



@seller_bp.route('/seller/my-products')
@seller_required
def my_products():
  total_items = Product.countProducts(session['org_id'])
  items_per_page = 10
  total_pages = math.ceil(total_items / items_per_page)
  
  current_page  = int(request.args.get('page', 1))
  products = Product.getProducts(session['org_id'])
  return render_template('/seller/my_products.html', products=products, current_page=current_page, total_pages=total_pages)

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
        print(f"Filename: {filename}")

        max_size = 25 * 1024 * 1024  # Example: 25MB
        if len(picture.read()) > max_size:
          flash("File size exceeds the limit of 25MB.", "warning")
          return redirect(url_for('seller.product_new'))
        
        picture.seek(0)  # Reset file pointer after reading

        # Upload to Cloudinary
        try:
          filename = os.path.splitext(filename)[0]
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
  formatted_sizes = ','.join(map(str, product_sizes))  # Convert list to "2,3,4"
  count, _ = product.countPreorder()

  return render_template('crud_blueprint/product_page-edit.html', form=form, product=product, count=count,
                          product_pictures=product_pictures, product_sizes=product_sizes, formatted_sizes=formatted_sizes)

@seller_bp.route('/product/edit/<int:product_id>/submit', methods=['GET','POST'])
@seller_required
def product_edit_submit(product_id):
  if request.method == 'POST':
    name = request.form.get("name")
    price = request.form.get("price")
    description = request.form.get("description")
    hook = request.form.get("hook")
    product_type = request.form.get("type")
    preorder_type = request.form.get("preorder")
    selected_sizes = request.form.get("selectedSizes")
    picture_urls = request.files.getlist("picture_urls")  # New pictures to upload
    slides_data = request.form.get("slides_data")
    date = request.form.get("preorderDate")
    number_of_days = request.form.get('number_of_days')
    product_id = request.form.get('product_id')

    slides_data = slides_data.split(',')
    slides_data = [slide for slide in slides_data if slide.startswith('https://res.cloudinary.com')]

    if date == '': date = None
    sizes = selected_sizes.split(',')
    URLS = []
    

    print(f"\n\nname: {name}")
    print(f"price: {price}")
    print(f"description: {description}")
    print(f"hook: {hook}")
    print(f"product_type: {product_type}")
    print(f"selected_sizes: {selected_sizes}")
    print(f"preorder_type: {preorder_type}")
    print(f"picture_urls: {picture_urls}")
    print(f"slides_data: {slides_data}")
    print(f"date: {date}")
    print(f"number_of_days: {number_of_days}")
    print(f"product_id: {product_id}")
    
    
    # Checks for a valid form \/ \/ \/
    # Checks for a valid form \/ \/ \/
    # Checks for a valid form \/ \/ \/
    if len(name) == 0:
      flash (f"Enter a name for the product...","warning")
      return redirect(url_for('seller.product_edit', product_id=product_id))
    
    if preorder_type == '':
      flash (f"Please select an order type...","warning")
      return redirect(url_for('seller.product_edit', product_id=product_id))
    if not price.isdigit() or price.startswith("0"):
      flash("Enter a valid price for the product. Must not start with 0.", "warning")
      return redirect(url_for('seller.product_edit', product_id=product_id))
    
    if float(price) > 10000:
      flash("Product should be affordable for students...", "warning")
      return redirect(url_for('seller.product_edit', product_id=product_id))
    
    if len(description) <= 10:
      flash(f"A minimum of 100 characters for description...","warning")
      flash(f"Chracter Length: {len(description)}","info")
      return redirect(url_for('seller.product_edit', product_id=product_id))
    
    if product_type == '':
      flash(f"Please select what kind of product you have...","warning")
      return redirect(url_for('seller.product_edit', product_id=product_id))
    
    if preorder_type == 1:
      if date == '' or date == None:
        flash (f"Select which date to release...","warning")
        return redirect(url_for('seller.product_edit', product_id=product_id))
      
      if int(number_of_days) <= 6:
        flash (f"Please give a deadline of 1 week or more...","warning")
        return redirect(url_for('seller.product_edit', product_id=product_id))
    # Checks for a valid form /\ /\ /\
    # Checks for a valid form /\ /\ /\
    # Checks for a valid form /\ /\ /\
      
    existing_pictures = Product.fetch_product_pictures(product_id=product_id)
    print(f"Existing: {existing_pictures}")
    
    # Get items in `slides_data` that are not in `existing_pictures`
    unmatched = [item for item in existing_pictures if item not in slides_data]   
    print(f"\nNo Match: {unmatched}")

    # Extract the public_id from the URL and delete the image
    for image in unmatched:
      Product.delete_product_pictures(image)
      
      old_public_id = image.split('/')[-1]  # Get the filename
      old_public_id = '.'.join(old_public_id.split('.')[:-1])  # Remove the last extension
      cloudinary.api.delete_resources(old_public_id, resource_type="image", type="upload")
    
    if picture_urls:
      for picture in picture_urls:
        filename = secure_filename(picture.filename)
        print(f"Filename: {filename}")
        
        # Break Loop if nothing is to be uploaded
        if filename == '':
          break
        
        max_size = 25 * 1024 * 1024  # Example: 25MB
        if len(picture.read()) > max_size:
          flash("File size exceeds the limit of 25MB.", "warning")
          return redirect(url_for('seller.product_edit', product_id=product_id))
        
        picture.seek(0)  # Reset file pointer after reading
        
        
        # Upload to Cloudinary
        try:
          filename = os.path.splitext(filename)[0]
          print(f"Final Name: {filename}")
          upload_result = cloudinary.uploader.upload(picture, public_id=filename)
          cloudinary_url = upload_result.get('secure_url')  # Get the URL of the uploaded image

          # Save the Cloudinary URL to the database for this product
          Product.add_product_pictures(product_id, cloudinary_url)
          print(f"cloudinary_url: {cloudinary_url}")
        
        except Exception as e:
          flash(f"An error occurred during file upload: {str(e)}", "danger")
          return redirect(url_for('seller.product_edit', product_id=product_id))
      
    # Put product in the Database and get ID
    product = Product(
      product_name=name,
      description=description,
      hook=hook,
      type=product_type,
      price=price,
      order_type=preorder_type,
      seller_id=session.get('id'),
      release_date=date,
      product_id=product_id
    )
    product.update()
    product.delete_product_sizes()
    
    for size in sizes:
      product.add_product_sizes(size)
    
    flash(f"Successfully edited product #{product_id}", "success")  
    return redirect(url_for('website.merch_details', product_id=product_id))
  if request.method == 'GET':
    return abort(404)

@seller_bp.route('/toggle_order_status', methods=['POST'])
@seller_required
def toggle_order_status():
    if request.method == 'POST':
        try:
            data = request.get_json()  # Parse the JSON body
            print(f"Received data: {data}")  # Log received data

            order_id = data.get('order_id')  # Extract order_id
            if not order_id:
                return jsonify({"error": "Order ID is required"}), 400

            print(f"\nOrder ID: {order_id}")

            # Call the toggle_status method in the Order class to toggle the status in the database
            success, new_status = Order.toggle_status(order_id)

            if success:
                # Return success and the updated status
                return jsonify({"success": True, "new_status": new_status}), 200
            else:
                return jsonify({"error": "Failed to update status"}), 500

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Something went wrong"}), 500
