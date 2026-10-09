from flask import Blueprint, render_template, flash, redirect, url_for, request, session, abort, jsonify
from datetime import datetime, timedelta
from config import MAILTRAP_SERVER, MAILTRAP_PORT, MAILTRAP_USERNAME, MAILTRAP_PASSWORD
from app.models.product import Product
from app.models.user import User
from app.models.order import Order
from app.models.favorite import Favorite
from app.forms import ProductForm
from app.utils.decorators import login_is_required

import smtplib
from email.mime.text import MIMEText


website_bp = Blueprint('website', __name__)

@website_bp.route('/api/check-login', methods=['GET'])
def check_login():
    return {"logged_in": "id" in session}


# Landing Page Route
@website_bp.route('/')
def landing():
    return render_template('landing.html')

@website_bp.route('/explore')
def explore():
    result = Product.get_explore_catalog()

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
    user_id = session.get("id")

    product_details = Product.get_details_by_id(product_id)
    if not product_details:
        flash("Product not found.", "danger")
        return redirect(url_for('website.explore'))

    product = product_details["product"]
    product_images = product_details["images"]
    product_sizes = product_details["sizes"]
    total_quantity = product_details["total_quantity"]

    is_favorite = Favorite.is_favorite(user_id, product_id) if user_id else False

    form = ProductForm()

    if request.method == 'POST' and user_id:
        success, is_fav = Favorite.toggle(user_id, product_id)
        if is_fav:
            flash("Added to favorites.", "success")
        else:
            flash("Removed from favorites.", "info")
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

    # Input validation
    try:
        quantityCheck = int(quantity)

        if not size:
            flash("Please pick a size before pre-ordering.", "warning")
            return redirect(url_for('website.merch_details', product_id=product_id))
        if not 1 <= quantityCheck <= 20:
            flash("Quantity should only be between 0 and 20.", "warning")
            return redirect(url_for('website.merch_details', product_id=product_id))
    except ValueError:
        flash("Quantity should only numbers", "danger")
        return redirect(url_for('website.merch_details', product_id=product_id))

    try:
        order_number = Order.preorderProduct(user.user_id, product.product_id, size, quantity, product.price)
        preorder_count, goal = product.countPreorder()

        if preorder_count >= goal:
            current_date = datetime.now()
            new_date = current_date + timedelta(days=8)
            formatted_date = new_date.strftime('%Y-%m-%d')

            product.goal_to_time(formatted_date)

    except Exception as e:
        print(f"Error occurred: {e}")
        flash("Something went wrong while pre-ordering the product. Please order again later...", "danger")
        return redirect(url_for('website.merch_details', product_id=product_id))

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


# Wishlist ------------------------------------------------------------------
@website_bp.route('/wishlist', methods=['GET'])
@login_is_required
def wishlist():
    user_id = session.get("id")
    favorites = Favorite.get_user_wishlist(user_id)
    return render_template('user/wishlist.html', favorites=favorites)


@website_bp.route('/favorite/submit', methods=['POST'])
@login_is_required
def toggle_favorite_details():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    user_id = session.get("id")
    if not user_id:
        return jsonify({"success": False, "message": "You must be logged in to toggle wishlist items."}), 401

    try:
        success, favorite_status = Favorite.toggle(user_id, product_id)
        return jsonify({"success": success, "favorite_status": favorite_status})
    except Exception as e:
        print(f"Error toggling favorite: {e}")
        return jsonify({"success": False, "message": "An error occurred while toggling the favorite."}), 500
