from flask import Blueprint, render_template, flash, redirect, url_for, request, session, abort,jsonify
from datetime import datetime, timedelta
from config import MAILTRAP_SERVER,MAILTRAP_PORT,MAILTRAP_USERNAME,MAILTRAP_PASSWORD
from app.models.product import Product
from app.models.user import User
from app.models.order import Order
from app.forms import ProductForm

import smtplib
from email.mime.text import MIMEText


website_bp = Blueprint('website', __name__)


def login_is_required(function):
  def wrapper(*args, **kwargs):
    if "id" not in session:
      return abort(401)
    return function(*args, **kwargs)
  wrapper.__name__ = function.__name__  # Fixes Flask's view function name requirement
  return wrapper

@website_bp.route('/api/check-login', methods=['GET'])
def check_login():
    return {"logged_in": "id" in session}


# Landing Page Route
@website_bp.route('/')
def landing():
    return render_template('landing.html')

@website_bp.route('/explore')
def explore():
    from app import mysql
    cursor = mysql.connection.cursor()

    query = """
        WITH PictureSelection AS (
            SELECT 
                p.product_id,
                pic.picture_url,
                ROW_NUMBER() OVER (PARTITION BY p.product_id ORDER BY pic.picture_url) AS row_num
            FROM products p
            LEFT JOIN pictures pic ON p.product_id = pic.picture_id
        )
        SELECT 
            p.product_id AS 'Product',
            p.product_name AS 'Name',
            col.college_name AS 'College', 
            ps.picture_url AS 'Picture'
        FROM products p
        LEFT JOIN user u ON p.seller_id = u.user_id
        LEFT JOIN organization org ON u.org_id = org.org_id
        LEFT JOIN college col ON org.college_id = col.college_id
        LEFT JOIN PictureSelection ps ON p.product_id = ps.product_id AND ps.row_num = 1
        GROUP BY p.product_id, p.product_name, col.college_name, ps.picture_url;
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

    # Initialize merchandise data with all colleges
    merchandise_data = {
        college: {'college_code': code, 'products': []}
        for college, code in college_code_mapping.items()
    }

    # Populate merchandise data with query results
    for row in result:
        college = row[2]
        if college in merchandise_data:
            merchandise_data[college]['products'].append({
                'product_id': row[0],
                'product_name': row[1],
                'picture_url': row[3] if row[3] else '/static/images/placeholder.jpg'
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

@website_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def merch_details(product_id):
    from app import mysql

    user_id = session.get("id")  # Get logged-in user's ID from session
    cursor = mysql.connection.cursor()

    # Fetch product by ID with order type
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product_row = cursor.fetchone()

    if not product_row:
        flash("Product not found.", "danger")
        return redirect(url_for('website.explore'))

    # Convert product row to dictionary
    product = {
        'product_id': product_row[0],
        'name': product_row[1],
        'description': product_row[2], 
        'hook': product_row[3],
        'type': product_row[4],  
        'price': product_row[5],  
        'order_type': product_row[6],
        'release_date': product_row[10],
    }

    # Fetch product images
    cursor.execute("SELECT picture_url FROM pictures WHERE picture_id = %s", (product_id,))
    product_images = [img[0] for img in cursor.fetchall()]

    # Fetch product sizes
    cursor.execute("SELECT size_id, product_quantity FROM product_sizes WHERE product_id = %s", (product_id,))
    product_sizes = cursor.fetchall()

    # Fetch total count of product quantities from all sizes
    cursor.execute("SELECT SUM(product_quantity) FROM product_sizes WHERE product_id = %s", (product_id,))
    total_quantity = cursor.fetchone()[0]  

    is_favorite = False
    if user_id:
        cursor.execute(
            "SELECT * FROM favorites WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )
        is_favorite = cursor.fetchone() is not None

    cursor.close()

    form = ProductForm()

    if request.method == 'POST' and user_id:  
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT * FROM favorites WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )
        favorite = cursor.fetchone()

        if favorite:
            # Remove favorite
            cursor.execute(
                "DELETE FROM favorites WHERE user_id = %s AND product_id = %s",
                (user_id, product_id)
            )
            mysql.connection.commit()
            flash("Removed from favorites.", "info")
        else:
            # Add favorite
            cursor.execute(
                "INSERT INTO favorites (user_id, product_id) VALUES (%s, %s)",
                (user_id, product_id)
            )
            mysql.connection.commit()
            flash("Added to favorites.", "success")

        cursor.close()
        return redirect(url_for('website.merch_details', product_id=product_id))

    return render_template(
        'crud_blueprint/product_details.html',
        product=product,
        images=product_images,
        sizes=product_sizes,
        form=form,
        total_quantity=total_quantity,
        is_favorite=is_favorite  
    )


@website_bp.route('/product/<int:product_id>/preorder', methods=['POST'])
@login_is_required
def preorder(product_id):
    user = User.get_by_email(session['email'])
    product = Product.get_by_id(product_id)
    
    size = request.form.get('selectedSizes')
    quantity = request.form.get("quantity")
    global order_number

    # Input and Picture validation
    try:
      quantityCheck = int(quantity)
      
      if not size:
        flash("Please pick a size before pre-ordering.", "warning")
        return redirect(url_for('website.merch_details', product_id=product_id))
      if not 1 <= quantityCheck <= 20 :
        flash("Quantity should only be between 0 and 20.", "warning")
        return redirect(url_for('website.merch_details', product_id=product_id))
    except ValueError:
      flash("Quantity should only numbers", "danger")
      return redirect(url_for('website.merch_details', product_id=product_id))

    try:
        order_number = Order.preorderProduct(user.user_id, product.product_id, size, quantity, product.price)
        preorder_count, goal = product.countPreorder()
        
        if preorder_count >= goal:
            # Get the current date
            current_date = datetime.now()

            # Add 8 days
            new_date = current_date + timedelta(days=8)

            # Format the date as YYYY-MM-DD
            formatted_date = new_date.strftime('%Y-%m-%d')

            print(formatted_date)
            
            product.goal_to_time(formatted_date)
            
            # TODO: GET ALL USERS
            # TODO: INFORM ALL USERS AS A GROUP THAT THE PRODUCT THEY PREORDERED HAS NOW STARTED PRESELLING
        
    except Exception as e:
      print(f"Error occurred: {e}")
      flash("Something went wrong while pre-ordering the product. Please order again later...", "danger")
      return redirect(url_for('website.merch_details', product_id=product_id))
    
    # sizeInText = convert_size(int(size))
    # summaryTotal = int(quantity) * product.price
    
    # # Plain text content
    # text = f"""\
    # <html>
    # <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    #     <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
    #         <h1 style="text-align: center; color: white; background-color: #1a1a1a; padding: 15px; margin: 0;">Unigear Team</h1>
            
    #         <div style="padding: 20px;">
    #             <h2>Thank you for your purchase!</h2>
    #             <p style="font-size: 16px;">Hello <strong>{user.user_name}</strong>, we were notified of your successful preorder of the product '{product.product_name}'.<br/>We will notify you when it is has reached the minimum pre-order goal.</p>
                
    #             <h3>Order Summary</h3>
    #             <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    #                 <tr style="background-color: #f4f4f4;">
    #                     <th style="text-align: left; padding: 10px; border: 1px solid #ddd;">Product Name</th>
    #                     <th style="text-align: left; padding: 10px; border: 1px solid #ddd;">Size</th>
    #                     <th style="text-align: left; padding: 10px; border: 1px solid #ddd;">Quantity</th>
    #                     <th style="text-align: left; padding: 10px; border: 1px solid #ddd;">Price</th>
    #                 </tr>
    #                 <tr>
    #                     <td style="padding: 10px; border: 1px solid #ddd;">{product.product_name}</td>
    #                     <td style="padding: 10px; border: 1px solid #ddd;">{sizeInText}</td>
    #                     <td style="padding: 10px; border: 1px solid #ddd;">{quantity}</td>
    #                     <td style="padding: 10px; border: 1px solid #ddd;">₱{summaryTotal}</td>
    #                 </tr>
    #             </table>
                
    #             <p style="font-size: 16px;">Thank you for using our service!</p>
                
    #             <div style="text-align: center; margin-top: 20px;">
    #                 <a href="http://localhost:5000/user/my-orders" style="font-size:16px; text-decoration:none; display:inline-block; color:#fff; padding:20px 25px; background-color:#2a9d8f; text-align:center; border-radius:5px; max-width:200px; margin:0 auto;">
    #                     View Your Order
    #                 </a>
    #             </div>
    #         </div>
            
    #         <footer style="text-align: center; background-color: #1a1a1a; color: white; padding: 15px; margin: 0;">
    #             <p style="margin: 0;">&copy; 2024 College Marketplace</p>
    #         </footer>
    #     </div>
    # </body>
    # </html>
    # """
    
    # # Email Configuration
    # sender_email = "Unigear Team <seller@demomailtrap.com>"
    # receiver_email = user.user_email
    
    # # Create MIMEText object
    # message = MIMEText(text, "html")
    # message["Subject"] = f"Preorder #{order_number} Confirmed"
    # message["From"] = sender_email
    # message["To"] = receiver_email
    
    # try:

    #     with smtplib.SMTP(MAILTRAP_SERVER, MAILTRAP_PORT) as server:
    #         server.starttls()
    #         server.login(MAILTRAP_USERNAME, MAILTRAP_PASSWORD)
    #         server.sendmail(sender_email, receiver_email, message.as_string())
        
    # except Exception as e:
    #     print(f"{e}\n")
    #     return f"Email has not been sent. {e}"
    
    flash("Your pre-order was successful!", "success")
    return redirect(url_for('website.explore'))


def convert_size(size_number):
    """
    Convert numeric size to text representation.
    Args:       size_number (int): Numeric size from 1 to 6
    Returns:    str: Corresponding size in text (xs, s, m, l, xl, 2xl)
    Raises:     ValueError: If size_number is not between 1 and 6
    """
    size_map = {
        1: 'XS',
        2: 'S', 
        3: 'M',
        4: 'L',
        5: 'XL',
        6: '2XL'
    }
    
    if size_number not in size_map:
        raise ValueError(f"Invalid size number. Must be between 1 and 6. Received: {size_number}")
    
    return size_map[size_number]


#Wishlist------------------------------------------------------------------
from app import mysql
from flask import session, jsonify, flash

from MySQLdb.cursors import DictCursor  # Import DictCursor for dictionary-based row access

@website_bp.route('/wishlist', methods=['GET'])
@login_is_required
def wishlist():
    user_id = session.get("id")
    
    # Create cursor using DictCursor (force dictionary access if possible)
    cursor = mysql.connection.cursor(DictCursor)  # Ensure this line is using DictCursor

    # Execute the query to get the favorite products and their details
    cursor.execute("""
        WITH PictureSelection AS (
            SELECT 
                p.product_id,
                pic.picture_url,
                ROW_NUMBER() OVER (PARTITION BY p.product_id ORDER BY pic.picture_url) AS row_num
            FROM products p
            LEFT JOIN pictures pic ON p.product_id = pic.picture_id
        )
        SELECT 
            f.favorite_id AS 'Favorite ID',
            f.user_id AS 'User ID',
            p.product_id AS 'Product',
            p.product_name AS 'Name',
            p.description AS 'Description',
            col.college_name AS 'College',
            ps.picture_url AS 'Picture'
        FROM favorites f
        LEFT JOIN products p ON f.product_id = p.product_id
        LEFT JOIN user u ON p.seller_id = u.user_id
        LEFT JOIN organization org ON u.org_id = org.org_id
        LEFT JOIN college col ON org.college_id = col.college_id
        LEFT JOIN PictureSelection ps ON p.product_id = ps.product_id AND ps.row_num = 1
        WHERE f.user_id = %s  -- Replace ? with the specific user_id
        GROUP BY f.favorite_id, f.user_id, p.product_id, p.product_name, p.description, col.college_name, ps.picture_url;
    """, (user_id,))

    # Fetch all the favorite products for the user
    favorites = cursor.fetchall()

    # Print the first row to check if it's a dictionary or tuple
    print(favorites)  # For debugging

    cursor.close()
    return render_template('user/wishlist.html', favorites=favorites)


@website_bp.route('/favorite/submit', methods=['POST'])
@login_is_required
def toggle_favorite_details():
    # NEW CODE \/ \/ \/
    # NEW CODE \/ \/ \/
    # NEW CODE \/ \/ \/
    data = request.get_json()  # Parse the JSON body
    print(f"Received data: {data}")  # Log received data

    product_id = data.get('product_id')  # Extract product_id
    if not product_id:
        return jsonify({"error": "Order ID is required"}), 400
    
    if "id" not in session:
        return jsonify({"success": False, "message": "You must be logged in to toggle wishlist items."}), 401
    # NEW CODE /\ /\ /\
    # NEW CODE /\ /\ /\
    # NEW CODE /\ /\ /
    
    user_id = session.get("id")
    cursor = mysql.connection.cursor()

    try:
        # Check if the product is already in the user's favorites
        cursor.execute("SELECT * FROM favorites WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        favorite = cursor.fetchone()

        if favorite:
            # If already a favorite, remove it
            cursor.execute("DELETE FROM favorites WHERE user_id = %s AND product_id = %s", (user_id, product_id))
            mysql.connection.commit()
            favorite_status = False
        else:
            # If not a favorite, add it
            cursor.execute("INSERT INTO favorites (user_id, product_id) VALUES (%s, %s)", (user_id, product_id))
            mysql.connection.commit()
            favorite_status = True

        cursor.close()
        return jsonify({"success": True, "favorite_status": favorite_status})

    except Exception as e:
        cursor.close()
        print(f"Error toggling favorite: {e}")
        return jsonify({"success": False, "message": "An error occurred while toggling the favorite."}), 500