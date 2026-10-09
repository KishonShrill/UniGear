"""Public website routes for browsing, explore, product details, preorder, and wishlist."""

import logging
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.forms import ProductForm
from app.models.favorite import Favorite
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.utils.decorators import login_is_required

logger = logging.getLogger(__name__)

website_bp = Blueprint("website", __name__)


@website_bp.route("/api/check-login", methods=["GET"])
def check_login():
    """Check whether the client is currently logged in."""
    return {"logged_in": "id" in session}


COLLEGES_CATALOG = [
    {
        "code": "cass",
        "abbr": "CASS",
        "name": "College of Arts and Social Sciences",
        "color": "#324831",
        "accent": "#4a6b49",
        "icon": "fas fa-feather-alt",
        "tagline": "Humanities, Social Sciences & Arts",
    },
    {
        "code": "ccs",
        "abbr": "CCS",
        "name": "College of Computer Studies",
        "color": "#598181",
        "accent": "#73a5a5",
        "icon": "fas fa-code",
        "tagline": "Computing, Software & Systems",
    },
    {
        "code": "cba",
        "abbr": "CBA",
        "name": "College of Business Administration",
        "color": "#9A9A71",
        "accent": "#b8b88a",
        "icon": "fas fa-chart-line",
        "tagline": "Accountancy, Management & Hospitality",
    },
    {
        "code": "chs",
        "abbr": "CHS",
        "name": "College of Health Sciences",
        "color": "#8B9EAF",
        "accent": "#a8c0d6",
        "icon": "fas fa-heartbeat",
        "tagline": "Nursing & Allied Health Sciences",
    },
    {
        "code": "ced",
        "abbr": "CED",
        "name": "College of Education",
        "color": "#414459",
        "accent": "#5e6382",
        "icon": "fas fa-graduation-cap",
        "tagline": "Teacher Education & Leadership",
    },
    {
        "code": "coe",
        "abbr": "COE",
        "name": "College of Engineering",
        "color": "#593838",
        "accent": "#7d5050",
        "icon": "fas fa-cogs",
        "tagline": "Civil, Mechanical, Electrical & Chemical",
    },
    {
        "code": "csm",
        "abbr": "CSM",
        "name": "College of Science and Mathematics",
        "color": "#934F50",
        "accent": "#ba6768",
        "icon": "fas fa-atom",
        "tagline": "Physics, Chemistry, Biology & Mathematics",
    },
]


# Landing Page Route
@website_bp.route("/")
def landing():
    """Render the application landing page with college directories and featured products."""
    featured_products = Product.get_featured_showcase(limit=4)
    return render_template(
        "landing.html",
        colleges=COLLEGES_CATALOG,
        featured_products=featured_products,
    )


@website_bp.route("/explore")
def explore():
    """Render the explore catalog organized by college."""
    result = Product.get_explore_catalog()

    # College Code mapping
    college_code_mapping = {
        "College of Arts and Social Sciences": "cass",
        "College of Computer Studies": "ccs",
        "College of Business Administration": "cba",
        "College of Health Sciences": "chs",
        "College of Education": "ced",
        "College of Engineering": "coe",
        "College of Science and Mathematics": "csm",
    }

    # Initialize merchandise data with all colleges
    merchandise_data = {
        college: {"college_code": code, "products": []}
        for college, code in college_code_mapping.items()
    }

    # Populate merchandise data with query results
    for row in result:
        college = row[2]
        if college in merchandise_data:
            merchandise_data[college]["products"].append(
                {
                    "product_id": row[0],
                    "product_name": row[1],
                    "picture_url": row[3] if row[3] else "/static/images/placeholder.jpg",
                }
            )

    # Define the order of colleges
    college_order = [
        "College of Arts and Social Sciences",
        "College of Computer Studies",
        "College of Business Administration",
        "College of Health Sciences",
        "College of Education",
        "College of Engineering",
        "College of Science and Mathematics",
    ]

    # Sort merchandise_data according to the defined order
    sorted_merchandise_data = {
        college: merchandise_data.get(college, {}) for college in college_order
    }

    college_colors = {
        "College of Arts and Social Sciences": "#324831",
        "College of Computer Studies": "#598181",
        "College of Business Administration": "#9A9A71",
        "College of Health Sciences": "#8B9EAF",
        "College of Education": "#414459",
        "College of Engineering": "#593838",
        "College of Science and Mathematics": "#934F50",
    }

    return render_template(
        "explore.html",
        merchandise_data=sorted_merchandise_data,
        college_colors=college_colors,
    )


@website_bp.route("/product/<int:product_id>", methods=["GET", "POST"])
def merch_details(product_id):
    """Render product details and handle favorite toggling."""
    user_id = session.get("id")

    product_details = Product.get_details_by_id(product_id)
    if not product_details:
        return "Product not found", 404

    product = product_details["product"]
    product_images = product_details["images"]
    product_sizes = product_details["sizes"]
    total_quantity = product_details["total_quantity"]

    is_favorite = Favorite.is_favorite(user_id, product_id) if user_id else False

    form = ProductForm()

    if request.method == "POST" and user_id:
        success, is_fav = Favorite.toggle(user_id, product_id)
        if is_fav:
            flash("Added to favorites.", "success")
        else:
            flash("Removed from favorites.", "info")
        return redirect(url_for("website.merch_details", product_id=product_id))

    return render_template(
        "crud_blueprint/product_details.html",
        product=product,
        images=product_images,
        sizes=product_sizes,
        form=form,
        total_quantity=total_quantity,
        is_favorite=is_favorite,
    )


@website_bp.route("/product/<int:product_id>/preorder", methods=["POST"])
@login_is_required
def preorder(product_id):
    """Place a preorder for a product and update inventory/goal counts."""
    user = User.get_by_email(session["email"])
    product = Product.get_by_id(product_id)

    size = request.form.get("selectedSizes")
    quantity = request.form.get("quantity")

    # Input validation
    try:
        quantity_check = int(quantity)

        if not size:
            flash("Please pick a size before pre-ordering.", "warning")
            return redirect(url_for("website.merch_details", product_id=product_id))
        if not 1 <= quantity_check <= 20:
            flash("Quantity should only be between 1 and 20.", "warning")
            return redirect(url_for("website.merch_details", product_id=product_id))
    except ValueError:
        flash("Quantity should only numbers", "danger")
        return redirect(url_for("website.merch_details", product_id=product_id))

    try:
        Order.preorderProduct(user.user_id, product.product_id, size, quantity, product.price)
        preorder_count, goal = product.countPreorder()

        if preorder_count >= goal:
            current_date = datetime.now()
            new_date = current_date + timedelta(days=8)
            formatted_date = new_date.strftime("%Y-%m-%d")

            product.goal_to_time(formatted_date)

    except Exception as e:
        logger.error("Error occurred during preorder: %s", e)
        flash(
            "Something went wrong while pre-ordering the product. Please order again later...",
            "danger",
        )
        return redirect(url_for("website.merch_details", product_id=product_id))

    flash("Your pre-order was successful!", "success")
    return redirect(url_for("website.explore"))


# Wishlist ------------------------------------------------------------------
@website_bp.route("/wishlist", methods=["GET"])
@login_is_required
def wishlist():
    """Render the user's favorited products wishlist."""
    user_id = session.get("id")
    favorites = Favorite.get_user_wishlist(user_id)
    return render_template("user/wishlist.html", favorites=favorites)


@website_bp.route("/favorite/submit", methods=["POST"])
@login_is_required
def toggle_favorite_details():
    """AJAX endpoint for toggling product favorite status."""
    data = request.get_json() or {}
    product_id = data.get("product_id")
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    user_id = session.get("id")
    if not user_id:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "You must be logged in to toggle wishlist items.",
                }
            ),
            401,
        )

    try:
        success, favorite_status = Favorite.toggle(user_id, product_id)
        return jsonify({"success": success, "favorite_status": favorite_status})
    except Exception as e:
        logger.error("Error toggling favorite: %s", e)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "An error occurred while toggling the favorite.",
                }
            ),
            500,
        )
