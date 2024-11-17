from flask import Blueprint, render_template, jsonify, request, current_app
from MySQLdb import cursors
colleges_bp = Blueprint('colleges', __name__)

@colleges_bp.route('/college-<college_code>')
def college_page(college_code): 
    try:
        return render_template(f'colleges/{college_code}.html')
    except Exception:
        return "Page not found", 404

@colleges_bp.route('/api/<college_code>/organizations')
def get_organizations(college_code):
    from app import mysql
    cursor = None
    try:
        # Mapping college_code to college_id
        college_ids = {
            "cass": 1,
            "cba": 2,
            "ccs": 3,
            "ced": 4,
            "coe": 5,
            "chs": 6,
            "csm": 7
        }

        college_id = college_ids.get(college_code.lower())
        if not college_id:
            return jsonify({"error": "Invalid college code"}), 400

        connection = mysql.connection
        cursor = connection.cursor()
        query = """
            SELECT org_id, org_name 
            FROM organization 
            WHERE college_id = %s
            ORDER BY 
                CASE WHEN org_name LIKE '%%Executive Council%%' THEN 1 ELSE 2 END, 
                org_name ASC;
        """
        cursor.execute(query, (college_id,))
        organizations = cursor.fetchall()
        return jsonify([{"id": org[0], "name": org[1]} for org in organizations])
    except Exception as e:
        print(f"Error in get_organizations: {e}")
        return jsonify({"error": "Failed to fetch organizations"}), 500
    finally:
        if cursor:
            cursor.close()

@colleges_bp.route('/api/organizations/products')
def get_cass_organization_products():
    from app import mysql
    org_id = request.args.get('org_id')  # Get the org_id from the request
    product_type = request.args.get('type')  # Get the product type from the request (if any)

    query = """
    SELECT  p.product_id AS 'Product', 
            p.product_name AS 'Product Name', 
            p.description AS 'Description',
            pi.picture_url AS 'Picture',
            p.type AS 'Type'  -- Get the type of product
    FROM products p
    LEFT JOIN pictures pi ON p.product_id = pi.picture_id
    LEFT JOIN user u ON p.seller_id = u.user_id
    WHERE u.org_id = %s
    """
    
    # Only add the type condition if it's not 'all'
    if product_type and product_type != 'all':
        query += " AND p.type = %s"
        params = (org_id, product_type)
    else:
        params = (org_id,)  # Only the org_id parameter

    try:
        connection = mysql.connection
        cursor = connection.cursor(cursors.DictCursor)
        cursor.execute(query, params)  # Execute with the correct parameters
        products = cursor.fetchall()
        return jsonify([{
            "id": p['Product'], 
            "name": p['Product Name'], 
            "description": p['Description'], 
            "picture": p['Picture']
        } for p in products])
    except Exception as e:
        print(f"Error in get_<college>_organization_products: {e}")
        return jsonify({"error": "Failed to fetch products"}), 500
    finally:
        if cursor:
            cursor.close() 
