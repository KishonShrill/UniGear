from flask import Blueprint, render_template, jsonify, request
from app.models.organization import Organization
from app.models.product import Product

colleges_bp = Blueprint('colleges', __name__)

@colleges_bp.route('/college-<college_code>')
def college_page(college_code):
    try:
        return render_template(f'colleges/{college_code}.html')
    except Exception:
        return "Page not found", 404

@colleges_bp.route('/api/<college_code>/organizations')
def get_organizations(college_code):
    try:
        organizations = Organization.get_by_college_code(college_code)
        if organizations is None:
            return jsonify({"error": "Invalid college code"}), 400
        return jsonify(organizations)
    except Exception as e:
        print(f"Error in get_organizations: {e}")
        return jsonify({"error": "Failed to fetch organizations"}), 500

@colleges_bp.route('/api/organizations/products')
def get_organization_products():
    org_id = request.args.get('org_id')
    product_type = request.args.get('type')

    try:
        products = Product.get_by_organization(org_id, product_type)
        return jsonify(products)
    except Exception as e:
        print(f"Error in get_organization_products: {e}")
        return jsonify({"error": "Failed to fetch products"}), 500
