from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from app.models.product import Product
from app.forms import *
import re as regex

import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from werkzeug.utils import secure_filename

website_bp = Blueprint('website', __name__)

@website_bp.route('/')
def landing():
    return render_template('landing.html')

@website_bp.route('/explore')
def explore():
    from app import mysql
    cursor = mysql.connection.cursor()

    query = """
        SELECT p.product_id AS 'Product', 
               col.college_name AS 'College', 
               pic.picture_url AS 'Picture'
        FROM products p
        LEFT JOIN user u ON p.seller_id = u.user_id
        LEFT JOIN organization org ON u.org_id = org.org_id
        LEFT JOIN college col ON org.college_id = col.college_id
        LEFT JOIN pictures pic ON p.product_id = pic.picture_id
    """
    cursor.execute(query)
    result = cursor.fetchall()

    merchandise_data = {}
    for row in result:
        college = row[1]
        if college not in merchandise_data:
            merchandise_data[college] = []

        merchandise_data[college].append({
            'product_id': row[0],
            'picture_url': row[2] if row[2] else '/static/images/placeholder.jpg'
        })

    # Define the order of colleges
    college_order = [
        'College of Arts and Sciences',
        'College of Computer Studies',
        'College of Business Administration',
        'College of Health Sciences',
        'College of Education',
        'College of Engineering',
        'College of Science and Mathematics'
    ]

    # Sort merchandise_data according to the defined order
    sorted_merchandise_data = {college: merchandise_data.get(college, []) for college in college_order}

    college_colors = {
        'College of Arts and Sciences': '#324831',
        'College of Computer Studies': '#598181',
        'College of Business Administration': '#9A9A71',
        'College of Health Sciences': '#8B9EAF',
        'College of Education': '#414459',
        'College of Engineering': '#593838',
        'College of Science and Mathematics': '#934F50'
    }

    return render_template('explore.html', merchandise_data=sorted_merchandise_data, college_colors=college_colors)

@website_bp.route('/product/new')
def product_new():
  form = ProductForm()
  return render_template('/crud_blueprint/product_page-create.html', form=form)

@website_bp.route('/product/new/submit', methods=['POST'])
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

      # Put product in the Database and get ID
      product = Product(name, description, hook, product_type, price, preorder_type, 1)
      product.save()
      product_id = product.getID()

      # Add the size to the product
      for size in sizes:
        product.add_product_sizes(0, size)

      if picture_urls == None:
        flash(f"You must submit at least one image: {str(e)}", "danger")
        return redirect(url_for('website.product_new'))
      
      for picture in picture_urls:
        if picture.filename == '' or picture.content_length == 0:
          flash(f"Upload at least one image.", "warning")
          return redirect(url_for('website.product_new'))

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
          flash(f"Profile picture uploaded successfully!", "success")
        except Exception as e:
          flash(f"An error occurred during file upload: {str(e)}", "danger")
          return redirect(url_for('website.product_new'))

      # Create a dictionary to store and return all the data
      product_data = {
        "id": product_id,
        "name": name,
        "description": description,
        "hook": hook,
        "type": product_type,
        "price": price,
        "preorder": preorder_type,
        "selectedSizes": selected_sizes,
        "picture_urls": URLS,
        "seller_id": 1,
      }

      # TODO: Change return to redirect to dashboard page
      return jsonify(success=True, data=product_data), 200
    except Exception as e:
      # If there’s an error, return it as part of the JSON response
      return jsonify(success=False, error=str(e)), 400