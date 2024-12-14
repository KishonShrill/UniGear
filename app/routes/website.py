from flask import Blueprint, render_template, flash, redirect, url_for, request, session, abort
from app.models.product import Product
from app.models.user import User
from app.forms import ProductForm


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
    if "id" in session:
        return {"logged_in": True}
    else:
        return {"logged_in": False}


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
            col.college_name AS 'College', 
            ps.picture_url AS 'Picture'
        FROM products p
        LEFT JOIN user u ON p.seller_id = u.user_id
        LEFT JOIN organization org ON u.org_id = org.org_id
        LEFT JOIN college col ON org.college_id = col.college_id
        LEFT JOIN PictureSelection ps ON p.product_id = ps.product_id AND ps.row_num = 1
        GROUP BY p.product_id, col.college_name, ps.picture_url;
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
        college = row[1]
        if college in merchandise_data:
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

@website_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def merch_details(product_id):
    from app import mysql

    user_id = session.get("id")  # Get logged-in user's ID from session
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
    
    from app import mysql

    size = request.form.get('selectedSizes')
    quantity = request.form.get("quantity")

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
        cursor = mysql.connection.cursor()
        cursor.execute(
            """
              UPDATE product_sizes
              SET product_quantity = product_quantity + %s 
              WHERE product_id = %s and size_id = %s
            """,
            (quantity, product_id, size)
        )
        cursor.execute(
            """
              INSERT INTO ordered_by (user_id, product_id, size_id, quantity, total_cost, order_status) VALUES 
              (%s, %s, %s, %s, %s, 0);
            """,
            (user.user_id, product_id, size, quantity, product.price)
        )
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
      print(f"Error occurred: {e}")
      flash("Something went wrong while pre-ordering the product. Please order again later...", "danger")
      return redirect(url_for('website.merch_details', product_id=product_id))

    flash("Your pre-order was successful!", "success")
    return redirect(url_for('website.explore'))




#Wishlist------------------------------------------------------------------
@website_bp.route('/favorite/<int:product_id>', methods=['POST'])
@login_is_required
def toggle_favorite(product_id):
    from app import mysql
    
    user_id = session.get("id")  
    cursor = mysql.connection.cursor()
    # Check if the product is already a favorite
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
        cursor.close()
        return {"status": "removed"}
    else:
        # Add favorite
        cursor.execute(
            "INSERT INTO favorites (user_id, product_id) VALUES (%s, %s)",
            (user_id, product_id)
        )
        mysql.connection.commit()
        cursor.close()
        return {"status": "added"}