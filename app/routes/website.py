from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from app.models.product import Product
from app.forms import ProductForm
import re as regex
from app import mysql
from flask import current_app as app
import pymysql


import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from werkzeug.utils import secure_filename

website_bp = Blueprint('website', __name__)

# Landing Page Route
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

    # College Code mapping
    college_code_mapping = {
        'College of Arts and Social Sciences': 'cass',
        'College of Computer Studies': 'ccs',
        'College of Business Administration': 'cba',
        'College of Health Sciences': 'chs',
        'College of Education': 'ced',
        'College of Engineering': 'coe',
        'College of Science and Mathematics': 'csm'
    }

    merchandise_data = {}
    for row in result:
        college = row[1]
        college_code = college_code_mapping.get(college, '')  # Get the code for the college
        if college not in merchandise_data:
            merchandise_data[college] = {'college_code': college_code, 'products': []}

        merchandise_data[college]['products'].append({
            'product_id': row[0],
            'picture_url': row[2] if row[2] else '/static/images/placeholder.jpg'
        })

    # Define the order of colleges
    college_order = [
        'College of Arts and Social Sciences',
        'College of Computer Studies',
        'College of Business Administration',
        'College of Health Sciences',
        'College of Education',
        'College of Engineering',
        'College of Science and Mathematics'
    ]

    # Sort merchandise_data according to the defined order
    sorted_merchandise_data = {college: merchandise_data.get(college, {}) for college in college_order}

    college_colors = {
        'College of Arts and Social Sciences': '#324831',
        'College of Computer Studies': '#598181',
        'College of Business Administration': '#9A9A71',
        'College of Health Sciences': '#8B9EAF',
        'College of Education': '#414459',
        'College of Engineering': '#593838',
        'College of Science and Mathematics': '#934F50'
    }

    return render_template('explore.html', merchandise_data=sorted_merchandise_data, college_colors=college_colors)

# Product Creation Form Route
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

      for picture in picture_urls:
         print (f"Name: {picture.filename}")

      if len(picture_urls) == 0:
         flash (f"You must submit one image: {str(e)}","Danger")
         return redirect(url_for('website.product_new'))
      
      for picture in picture_urls:
         if picture.filename=='':
            flash(f"Upload at least one image", "Warning")
            return redirect (url_for ('website.product_new'))

      # Put product in the Database and get ID
      product = Product(name, description, hook, product_type, price, preorder_type, 1)
      product.save()
      product_id = product.getID()

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
          return redirect(url_for('website.product_new'))
      flash(f"Profile picture uploaded successfully!", "success")


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





# here ko ga startttt
@website_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def merch_details(product_id):
    from app import mysql

    cursor = mysql.connection.cursor()

    # Fetch product by ID
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product_row = cursor.fetchone()

    if not product_row:
        flash("Product not found.", "danger")
        return redirect(url_for('website.explore'))

    # Convert product row to dictionary
    product = {
        'product_id': product_row[0],
        'name': product_row[1],
        'price': product_row[5],  
        'description': product_row[2], 
        'preorder_count': product_row[0],
        'type': product_row[4],  
        'hook': product_row[3],
    }

    # Fetch product images 
    cursor.execute("SELECT picture_url FROM pictures WHERE picture_id = %s", (product_id,))
    product_images = [img[0] for img in cursor.fetchall()]

    # Fetch product sizes
    cursor.execute("SELECT size_id, product_quantity FROM product_sizes WHERE product_id = %s", (product_id,))
    product_sizes = cursor.fetchall()
    
    # Fetch total count of product quantities from all sizes
    cursor.execute("SELECT SUM(product_quantity) FROM product_sizes WHERE product_id = %s", (product_id,))
    total_quantity = cursor.fetchone()[0]  # Retrieve the sum of quantities
    
    cursor.close()
    
    form = ProductForm()

    return render_template(
        'crud_blueprint/product_details.html',
        product=product,
        images=product_images,
        sizes=product_sizes,
        form=form,
        total_quantity=total_quantity
    )


@website_bp.route('/product/<int:product_id>/preorder', methods=['POST'])
def preorder(product_id):
    from app import mysql
    from flask import request, flash, redirect, url_for

    size = request.form.get('size')
    quantity = int(request.form.get('quantity', 1))

    if not size or quantity <= 0:
        flash("Invalid size or quantity.", "danger")
        return redirect(url_for('website.merch_details', product_id=product_id))

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE products SET preorder_count = preorder_count + %s WHERE product_id = %s",
        (quantity, product_id)
    )

    cursor.execute(
        "INSERT INTO product_preorders (product_id, size, quantity) VALUES (%s, %s, %s)",
        (product_id, size, quantity)
    )
    mysql.connection.commit()
    cursor.close()

    flash("Your pre-order was successful!", "success")
    return redirect(url_for('website.merch_details', product_id=product_id))