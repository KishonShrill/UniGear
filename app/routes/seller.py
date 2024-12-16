from flask import Blueprint, render_template, jsonify, request, session, flash, redirect, url_for, abort
from app.models.product import Product
from app.forms import *
from app.routes.auth import seller_required
from app.models.user import User

import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from werkzeug.utils import secure_filename


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
  
      print(f"Picture URLs: {picture_urls}")
      print(f"Number of files selected: {len(picture_urls)}")  # Debug the number of files selected

      sizes = selected_sizes.split(',')
      URLS = []
      
      # Checks for a valid form \/ \/ \/
      # Checks for a valid form \/ \/ \/
      # Checks for a valid form \/ \/ \/
      
      if len(name) == 0:
         flash (f"Enter a name for the product...","warning")
         return redirect(url_for('seller.product_new'))
      
      if not price.isdigit() or price.startswith("0"):
        flash("Enter a valid price for the product. Must not start with 0.", "warning")
        return redirect(url_for('seller.product_new'))
      
      if int(price) > 10000:
        flash("Product should be affordable for students...", "warning")
        return redirect(url_for('seller.product_new'))
       
      if len(description) <= 50:
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
                        seller_id=session.get('id')
      )
      product.save()

      # Add the size to the product
      for size in sizes:
        product.add_product_sizes(0, size)


      # Handle file uploads
      for picture in picture_urls:
        # Assuming you save the picture and generate a URL
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

    form = ProductForm(obj=product)  # Populate the form with existing product data

    if request.method == 'POST':
        # Extract form data
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        hook = request.form.get("hook")
        product_type = request.form.get("type")
        preorder_type = request.form.get("preorder")
        selected_sizes = request.form.get("selectedSizes")
        picture_urls = request.files.getlist("picture_urls")

        # Validate form data
        if len(name) == 0:
            flash("Enter a name for the product", "warning")
            return redirect(url_for('seller.product_edit', product_id=product_id))

        if not price.isdigit() or price.startswith("0"):
            flash("Enter a valid price for the product", "warning")
            return redirect(url_for('seller.product_edit', product_id=product_id))

        if int(price) > 10000:
            flash("Product should be affordable for students", "warning")
            return redirect(url_for('seller.product_edit', product_id=product_id))

        if len(description) <= 50:
            flash("Description should have at least 100 characters", "warning")
            return redirect(url_for('seller.product_edit', product_id=product_id))

        if not product_type:
            flash("Pick at least one type for the product", "warning")
            return redirect(url_for('seller.product_edit', product_id=product_id))

        # Update product information in the database
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

            # Update sizes
            sizes = selected_sizes.split(',')
            for size in sizes:
                product.add_product_sizes(0, size)

            # Handle file uploads for images
            if picture_urls:
                for picture in picture_urls:
                    filename = secure_filename(picture.filename)
                    cloudinary_url = ""
                    try:
                        # Upload to Cloudinary
                        upload_result = cloudinary.uploader.upload(picture, public_id=filename)
                        cloudinary_url = upload_result.get('secure_url')

                        # Save the Cloudinary URL to the database for this product
                        product.add_product_pictures(cloudinary_url)

                    except Exception as e:
                        flash(f"An error occurred during file upload: {str(e)}", "danger")
                        return redirect(url_for('seller.product_edit', product_id=product_id))

            flash("Product updated successfully!", "success")
            return redirect(url_for('website.merch_details', product_id=product.product_id))

        except Exception as e:
            flash(f"Error updating product: {str(e)}", "danger")
            return redirect(url_for('seller.product_edit', product_id=product_id))

    # If it's a GET request, render the edit form
    return render_template('crud_blueprint/product_page-edit.html', form=form, product=product)
