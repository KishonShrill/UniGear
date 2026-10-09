from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, session, abort
from app.models.product import Product
from app.models.user import User
from app.models.order import Order
from app.forms import LinkVerify
from app.utils.decorators import login_is_required
import math
import cloudinary.api
import cloudinary.uploader


user_bp = Blueprint('user', __name__)

@user_bp.route('/user/my-orders')
@login_is_required
def my_orders():
    form = LinkVerify()
    user = User.get_by_email(session['email'])

    total_items = Product.countOrdersWithEmail(user.user_email)
    items_per_page = 10
    total_pages = math.ceil(total_items / items_per_page) if total_items else 1

    current_page = int(request.args.get('page', 1))
    orders = Product.getOrdersWithEmail(user.user_email)
    return render_template('/user/my_orders.html', orders=orders, form=form, current_page=current_page, total_pages=total_pages)

@user_bp.route('/user/my-orders/delete', methods=['POST', 'GET'])
@login_is_required
def delete_order():
    if request.method == 'POST':
        try:
            data = request.get_json()
            order_id = data.get('order_id')
            if not order_id:
                return jsonify({"error": "Order ID is required"}), 400

            picture = Order.fetchReceipt(order_id)
            if picture:
                old_public_id = picture.split('/')[-1]
                old_public_id = '.'.join(old_public_id.split('.')[:-1])
                cloudinary.api.delete_resources(old_public_id, resource_type="image", type="upload")

            status = Order.deleteOrder(order_id)
            return jsonify({"success": status})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Something went wrong"}), 500
    if request.method == 'GET':
        return abort(404)

@user_bp.route('/user/receipt/delete', methods=['POST'])
@login_is_required
def delete_receipt():
    try:
        data = request.get_json()
        picture = data.get('picture')

        if picture:
            old_public_id = picture.split('/')[-1]
            old_public_id = '.'.join(old_public_id.split('.')[:-1])
            cloudinary.api.delete_resources(old_public_id, resource_type="image", type="upload")

        status = Order.deleteReceipt(picture)
        return jsonify({"success": status})
    except Exception as e:
        print(f"Receipt Del ERR: {e}")
        return jsonify({"error": str(e)}), 500

@user_bp.route('/user/profile', methods=['GET', 'POST'])
@login_is_required
def profile():
    user = User.get_by_email(session['email'])

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('user.profile'))

    if request.method == 'POST':
        try:
            user.user_name = request.form.get('username')
            user.user_email = request.form.get('email')
            user.user_contact = request.form.get('phone')
            user.user_address = request.form.get('address')
            user.user_role = request.form.get('role')
            user.org_id = request.form.get('org_id')
            user.save()

            flash("Profile updated successfully!", "success")
            return redirect(url_for('user.profile'))

        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for('user.profile'))

    if user and user.user_address:
        parts = user.user_address.split(", ")
        zipcode_street = parts[0] if len(parts) > 0 else ""
        barangay = parts[1] if len(parts) > 1 else ""
        city = parts[2] if len(parts) > 2 else ""
    else:
        zipcode_street, barangay, city = "", "", ""

    return render_template('user/user_profile.html', user=user, zipcode_street=zipcode_street, barangay=barangay, city=city)

@user_bp.route('/user/my-orders/upload', methods=['POST'])
@login_is_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        order_id = request.form.get('order_id')

        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not order_id:
            return jsonify({'error': 'No order ID provided'}), 400

        upload_result = cloudinary.uploader.upload(file)
        cloudinary_url = upload_result['secure_url']

        Order.save_proof_of_payment(order_id, cloudinary_url)

        return jsonify({
            'success': True,
            'url': cloudinary_url
        }), 200

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500
