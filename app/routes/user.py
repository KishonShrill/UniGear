"""User routes for orders, profile, and proof-of-payment management."""

import logging
import math

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.forms import LinkVerify
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.utils.decorators import login_is_required
from app.utils.image_service import ImageService

logger = logging.getLogger(__name__)

user_bp = Blueprint("user", __name__)


@user_bp.route("/user/my-orders")
@login_is_required
def my_orders():
    """Display paginated list of current user's orders."""
    form = LinkVerify()
    user = User.get_by_email(session["email"])

    total_items = Product.countOrdersWithEmail(user.user_email)
    items_per_page = 10
    total_pages = math.ceil(total_items / items_per_page) if total_items else 1

    current_page = int(request.args.get("page", 1))
    orders = Product.getOrdersWithEmail(user.user_email)
    return render_template(
        "/user/my_orders.html",
        orders=orders,
        form=form,
        current_page=current_page,
        total_pages=total_pages,
    )


@user_bp.route("/user/my-orders/delete", methods=["POST", "GET"])
@login_is_required
def delete_order():
    """Cancel / delete an unpaid order and remove associated receipt image."""
    if request.method == "POST":
        try:
            data = request.get_json()
            order_id = data.get("order_id")
            if not order_id:
                return jsonify({"error": "Order ID is required"}), 400

            picture = Order.fetchReceipt(order_id)
            if picture:
                ImageService.delete_image(picture)

            status = Order.deleteOrder(order_id)
            return jsonify({"success": status})
        except Exception as e:
            logger.error("Error deleting order: %s", e)
            return jsonify({"error": "Something went wrong"}), 500
    if request.method == "GET":
        return abort(404)


@user_bp.route("/user/receipt/delete", methods=["POST"])
@login_is_required
def delete_receipt():
    """Delete a proof of payment receipt image."""
    try:
        data = request.get_json()
        picture = data.get("picture")

        if picture:
            ImageService.delete_image(picture)

        status = Order.deleteReceipt(picture)
        return jsonify({"success": status})
    except Exception as e:
        logger.error("Receipt deletion error: %s", e)
        return jsonify({"error": str(e)}), 500


@user_bp.route("/user/profile", methods=["GET", "POST"])
@login_is_required
def profile():
    """View and update user profile information."""
    user = User.get_by_email(session["email"])

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("user.profile"))

    if request.method == "POST":
        try:
            user.user_name = request.form.get("username")
            user.user_email = request.form.get("email")
            user.user_contact = request.form.get("phone")
            user.user_address = request.form.get("address")
            user.user_role = request.form.get("role")
            user.org_id = request.form.get("org_id")
            user.save()

            flash("Profile updated successfully!", "success")
            return redirect(url_for("user.profile"))

        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for("user.profile"))

    zipcode_street, barangay, city = user.parsed_address if user else ("", "", "")

    return render_template(
        "user/user_profile.html",
        user=user,
        zipcode_street=zipcode_street,
        barangay=barangay,
        city=city,
    )


@user_bp.route("/user/my-orders/upload", methods=["POST"])
@login_is_required
def upload_file():
    """Upload proof of payment receipt image to Cloudinary and link to order."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        order_id = request.form.get("order_id")

        if not file or file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not order_id:
            return jsonify({"error": "No order ID provided"}), 400

        cloudinary_url = ImageService.upload_image(file)
        if not cloudinary_url:
            return jsonify({"error": "Failed to upload image"}), 500

        Order.save_proof_of_payment(order_id, cloudinary_url)

        return jsonify({"success": True, "url": cloudinary_url}), 200

    except ValueError as e:
        logger.warning("Upload validation failed: %s", e)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("Upload error: %s", e)
        return jsonify({"error": str(e)}), 500
