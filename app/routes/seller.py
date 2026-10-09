"""Seller routes for inventory, orders, product management, and exports."""

import logging
import math

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.forms import ProductForm
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.utils.decorators import seller_required
from app.utils.image_service import ImageService

logger = logging.getLogger(__name__)

seller_bp = Blueprint("seller", __name__)


@seller_bp.route("/seller/my-orders")
@seller_required
def my_orders():
    """Display paginated orders for the seller's organization."""
    total_items = Product.countOrders(session["org_id"])
    items_per_page = 10
    total_pages = math.ceil(total_items / items_per_page) if total_items else 1

    current_page = int(request.args.get("page", 1))
    orders = Product.getOrdersInPage(session["org_id"], current_page)
    return render_template(
        "/seller/my_orders.html",
        orders=orders,
        current_page=current_page,
        total_pages=total_pages,
    )


@seller_bp.route("/seller/my-orders/export")
@seller_required
def export_my_orders():
    """Export all orders for the seller's organization as a downloadable CSV."""
    orders = Product.getOrders(session["org_id"])

    def generate():
        header = [
            "Order",
            "Customer",
            "Total Cost",
            "Product",
            "Size",
            "Quantity",
            "Type",
            "Status",
            "Order Date",
        ]
        yield ",".join(header) + "\n"

        for order in orders:
            row = [
                str(order["Order"]),
                order["Customer"],
                f"{order['Total Cost']:.2f}",
                order["Product"],
                order["Size"],
                str(order["Quantity"]),
                "Time" if order["Type"] == 1 else "Order",
                "Paid" if order["Status"] == 1 else "Not Paid",
                order["Order Date"].strftime("%Y-%m-%d %H:%M:%S"),
            ]
            yield ",".join(row) + "\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=orders.csv"},
    )


@seller_bp.route("/seller/my-orders/delete", methods=["POST", "GET"])
@seller_required
def delete_order():
    """Delete an order for the seller's organization."""
    if request.method == "POST":
        try:
            data = request.get_json()
            order_id = data.get("order_id") if data else None
            if not order_id:
                return jsonify({"error": "Order ID is required"}), 400

            status = Order.deleteOrder(order_id)
            return jsonify({"success": status})
        except Exception as e:
            logger.error("Error deleting order: %s", e)
            return jsonify({"error": "Something went wrong"}), 500
    if request.method == "GET":
        return abort(404)


@seller_bp.route("/seller/my-products")
@seller_required
def my_products():
    """Display paginated list of products for seller's organization."""
    total_items = Product.countProducts(session["org_id"])
    items_per_page = 10
    total_pages = math.ceil(total_items / items_per_page) if total_items else 1

    current_page = int(request.args.get("page", 1))
    products = Product.getProducts(session["org_id"])
    return render_template(
        "/seller/my_products.html",
        products=products,
        current_page=current_page,
        total_pages=total_pages,
    )


@seller_bp.route("/seller/my-products/delete", methods=["POST", "GET"])
@seller_required
def delete_product():
    """Delete a product belonging to the seller's organization."""
    if request.method == "POST":
        try:
            data = request.get_json()
            product_id = data.get("product_id") if data else None
            if not product_id:
                return jsonify({"error": "Product ID is required"}), 400

            Product.delete(product_id)
            return jsonify({"success": True})
        except Exception as e:
            logger.error("Error deleting product: %s", e)
            return jsonify({"error": "Something went wrong"}), 500
    if request.method == "GET":
        return abort(404)


@seller_bp.route("/seller/profile", methods=["GET", "POST"])
@seller_required
def profile():
    """View and update seller profile details."""
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
            return redirect(url_for("seller.profile"))

        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for("seller.profile"))

    zipcode_street, barangay, city = user.parsed_address if user else ("", "", "")

    return render_template(
        "seller/seller_profile.html",
        user=user,
        zipcode_street=zipcode_street,
        barangay=barangay,
        city=city,
    )


@seller_bp.route("/product/new")
@seller_required
def product_new():
    """Render the product creation page."""
    form = ProductForm()
    return render_template("/crud_blueprint/product_page-create.html", form=form)


@seller_bp.route("/product/new/submit", methods=["POST", "GET"])
@seller_required
def product_new_submit():
    """Validate, create a new product, and upload associated image assets."""
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            price = request.form.get("price", "").strip()
            description = request.form.get("description", "").strip()
            hook = request.form.get("hook", "").strip()
            product_type = request.form.get("type", "").strip()
            preorder_type = request.form.get("preorder", "").strip()
            selected_sizes = request.form.get("selectedSizes", "").strip()
            picture_urls = request.files.getlist("picture_urls")
            date = request.form.get("preorderDate", "").strip() or None
            number_of_days = request.form.get("number_of_days", "").strip()

            sizes = [s.strip() for s in selected_sizes.split(",") if s.strip()]

            # Form validation checks
            if int(preorder_type) == 1:
                if not date:
                    flash("Select which date to release...", "warning")
                    return redirect(url_for("seller.product_new"))

                if int(number_of_days) <= 6:
                    flash("Please give a deadline of 1 week or more...", "warning")
                    return redirect(url_for("seller.product_new"))

            if len(name) == 0:
                flash("Enter a name for the product...", "warning")
                return redirect(url_for("seller.product_new"))

            if not price.isdigit() or price.startswith("0"):
                flash("Enter a valid price for the product. Must not start with 0.", "warning")
                return redirect(url_for("seller.product_new"))

            if int(price) > 10000:
                flash("Product should be affordable for students...", "warning")
                return redirect(url_for("seller.product_new"))

            if len(description) <= 10:
                flash("A minimum of 100 characters for description...", "warning")
                flash(f"Character Length: {len(description)}", "info")
                return redirect(url_for("seller.product_new"))

            if product_type == "":
                flash("Pick at least one size for product...", "warning")
                return redirect(url_for("seller.product_new"))

            valid_pictures = [p for p in picture_urls if getattr(p, "filename", None)]
            if not valid_pictures:
                flash("Upload at least one image", "warning")
                return redirect(url_for("seller.product_new"))

            # Save product record in the database
            product = Product(
                product_name=name,
                description=description,
                hook=hook,
                type=product_type,
                price=price,
                order_type=preorder_type,
                seller_id=session.get("id"),
                release_date=date,
            )
            product.save()

            for size in sizes:
                product.add_product_sizes(size)

            # Upload image files to Cloudinary and link to product
            for picture in valid_pictures:
                try:
                    cloudinary_url = ImageService.upload_image(picture)
                    if cloudinary_url:
                        product.init_product_pictures(cloudinary_url)
                except ValueError as ve:
                    flash(f"File size error: {ve}", "warning")
                    return redirect(url_for("seller.product_new"))
                except Exception as e:
                    logger.error("Cloudinary upload failed: %s", e)
                    flash(f"An error occurred during file upload: {str(e)}", "danger")
                    return redirect(url_for("seller.product_new"))

            flash("Product created successfully!", "success")
            return redirect(url_for("website.merch_details", product_id=product.product_id))

        except Exception as e:
            logger.error("Error creating product: %s", e)
            return jsonify(success=False, error=str(e)), 400

    if request.method == "GET":
        return abort(404)


@seller_bp.route("/product/edit/<int:product_id>", methods=["GET", "POST"])
@seller_required
def product_edit(product_id):
    """Render the product edit page populated with existing data."""
    product = Product.get_by_id(product_id)

    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("seller.my_products"))

    form = ProductForm(obj=product)
    product_pictures = product.get_product_pictures(product_id)
    product_sizes = product.get_product_sizes(product_id)
    formatted_sizes = ",".join(map(str, product_sizes))
    count, _ = product.countPreorder()

    return render_template(
        "crud_blueprint/product_page-edit.html",
        form=form,
        product=product,
        count=count,
        product_pictures=product_pictures,
        product_sizes=product_sizes,
        formatted_sizes=formatted_sizes,
    )


@seller_bp.route("/product/edit/<int:product_id>/submit", methods=["GET", "POST"])
@seller_required
def product_edit_submit(product_id):
    """Validate and update existing product, images, and sizes."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "").strip()
        description = request.form.get("description", "").strip()
        hook = request.form.get("hook", "").strip()
        product_type = request.form.get("type", "").strip()
        preorder_type = request.form.get("preorder", "").strip()
        selected_sizes = request.form.get("selectedSizes", "").strip()
        picture_urls = request.files.getlist("picture_urls")
        slides_data_str = request.form.get("slides_data", "")
        date = request.form.get("preorderDate", "").strip() or None
        number_of_days = request.form.get("number_of_days", "").strip()

        slides_data = [
            slide.strip()
            for slide in slides_data_str.split(",")
            if slide.strip().startswith("https://res.cloudinary.com")
        ]
        sizes = [s.strip() for s in selected_sizes.split(",") if s.strip()]

        # Validation
        if len(name) == 0:
            flash("Enter a name for the product...", "warning")
            return redirect(url_for("seller.product_edit", product_id=product_id))

        if preorder_type == "":
            flash("Please select an order type...", "warning")
            return redirect(url_for("seller.product_edit", product_id=product_id))

        if not price.isdigit() or price.startswith("0"):
            flash("Enter a valid price for the product. Must not start with 0.", "warning")
            return redirect(url_for("seller.product_edit", product_id=product_id))

        if float(price) > 10000:
            flash("Product should be affordable for students...", "warning")
            return redirect(url_for("seller.product_edit", product_id=product_id))

        if len(description) <= 10:
            flash("A minimum of 100 characters for description...", "warning")
            flash(f"Character Length: {len(description)}", "info")
            return redirect(url_for("seller.product_edit", product_id=product_id))

        if product_type == "":
            flash("Please select what kind of product you have...", "warning")
            return redirect(url_for("seller.product_edit", product_id=product_id))

        if int(preorder_type) == 1:
            if not date:
                flash("Select which date to release...", "warning")
                return redirect(url_for("seller.product_edit", product_id=product_id))

            if int(number_of_days) <= 6:
                flash("Please give a deadline of 1 week or more...", "warning")
                return redirect(url_for("seller.product_edit", product_id=product_id))

        # Handle image deletions for removed slides
        existing_pictures = Product.fetch_product_pictures(product_id=product_id)
        unmatched = [item for item in existing_pictures if item not in slides_data]

        for image in unmatched:
            Product.delete_product_pictures(image)
            ImageService.delete_image(image)

        # Handle new image uploads
        if picture_urls:
            for picture in picture_urls:
                if not getattr(picture, "filename", None):
                    continue

                try:
                    cloudinary_url = ImageService.upload_image(picture)
                    if cloudinary_url:
                        Product.add_product_pictures(product_id, cloudinary_url)
                except ValueError as ve:
                    flash(f"File size error: {ve}", "warning")
                    return redirect(url_for("seller.product_edit", product_id=product_id))
                except Exception as e:
                    logger.error("Cloudinary upload failed: %s", e)
                    flash(f"An error occurred during file upload: {str(e)}", "danger")
                    return redirect(url_for("seller.product_edit", product_id=product_id))

        # Update product record and sizes
        product = Product(
            product_name=name,
            description=description,
            hook=hook,
            type=product_type,
            price=price,
            order_type=preorder_type,
            seller_id=session.get("id"),
            release_date=date,
            product_id=product_id,
        )
        product.update()
        product.delete_product_sizes()

        for size in sizes:
            product.add_product_sizes(size)

        flash(f"Successfully edited product #{product_id}", "success")
        return redirect(url_for("website.merch_details", product_id=product_id))

    if request.method == "GET":
        return abort(404)


@seller_bp.route("/toggle_order_status", methods=["POST"])
@seller_required
def toggle_order_status():
    """Toggle payment status (0 = unpaid, 1 = paid) for a given order."""
    if request.method == "POST":
        try:
            data = request.get_json()
            order_id = data.get("order_id") if data else None
            if not order_id:
                return jsonify({"error": "Order ID is required"}), 400

            success, new_status = Order.toggle_status(order_id)

            if success:
                return jsonify({"success": True, "new_status": new_status}), 200
            else:
                return jsonify({"error": "Failed to update status"}), 500

        except Exception as e:
            logger.error("Error in toggle_order_status: %s", e)
            return jsonify({"error": "Something went wrong"}), 500
