from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, abort,session

from app.models.product import Product
from app.forms import ProductForm
from app.routes.auth import seller_required

import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from werkzeug.utils import secure_filename


seller_bp = Blueprint('seller', __name__)


# Seller Routes
# Seller Routes
# Seller Routes
@seller_bp.route('/dashboard')
@seller_required
def dashboard():
  ...

@seller_bp.route('/seller/my-orders')
@seller_required
def my_orders():
  orders = Product.getOrders()
  print(orders)
  return render_template('/seller/my_orders.html', orders=orders)

@seller_bp.route('/seller/my-products')
@seller_required
def my_products():
    org_id = session.get('org_id')
    print(f"Org ID: ", org_id)
    if not org_id:
        print("Org ID is missing from session")
    products = Product.getProducts(org_id)
    print(f"Products: {products}")
    return render_template('/seller/my_products.html', products=products)

@seller_bp.route('/profile')
@seller_required
def profile():
  ...
  
  
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
         flash (f"You must submit one image: {str(e)}","danger")
         return redirect(url_for('seller.product_new'))
      
      for picture in picture_urls:
         if picture.filename=='':
            flash(f"Upload at least one image", "warning")
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