from flask import Blueprint, render_template, jsonify, request, current_app
from MySQLdb import cursors
colleges_bp = Blueprint('colleges', __name__)

@colleges_bp.route('/college-cass')
def college_cass():
    return render_template('colleges/cass.html')

@colleges_bp.route('/college-ccs')
def college_ccs():
    return render_template('colleges/ccs.html')

@colleges_bp.route('/college-cba')
def college_cba():
    return render_template('colleges/cba.html')

@colleges_bp.route('/college-chs')
def college_chs():
    return render_template('colleges/chs.html')

@colleges_bp.route('/college-ced')
def college_ced():
    return render_template('colleges/ced.html')

@colleges_bp.route('/college-coe')
def college_coe():
    return render_template('colleges/coe.html')

@colleges_bp.route('/college-csm')
def college_csm():
    return render_template('colleges/csm.html')

#CASS

@colleges_bp.route('/api/cass/organizations')
def get_cass_organizations():
    from app import mysql
    cursor = None
    try:
        connection = mysql.connection
        cursor = connection.cursor()
        query = """
            SELECT org_id, org_name 
            FROM organization 
            WHERE college_id = 1
            ORDER BY 
                CASE WHEN org_name LIKE '%Executive Council%' THEN 1 ELSE 2 END, 
                org_name ASC;
        """
        cursor.execute(query)
        organizations = cursor.fetchall()
        return jsonify([{"id": org[0], "name": org[1]} for org in organizations])
    except Exception as e:
        print(f"Error in get_cass_organizations: {e}")
        return jsonify({"error": "Failed to fetch organizations"}), 500
    finally:
        if cursor:
            cursor.close()

@colleges_bp.route('/api/cba/organizations')
def get_cba_organizations():
    from app import mysql
    cursor = None
    try:
        connection = mysql.connection
        cursor = connection.cursor()
        query = """
            SELECT org_id, org_name 
            FROM organization 
            WHERE college_id = 2
            ORDER BY 
                CASE WHEN org_name LIKE '%Executive Council%' THEN 1 ELSE 2 END, 
                org_name ASC;
        """
        cursor.execute(query)
        organizations = cursor.fetchall()
        return jsonify([{"id": org[0], "name": org[1]} for org in organizations])
    except Exception as e:
        print(f"Error in get_ccs_organizations: {e}")
        return jsonify({"error": "Failed to fetch organizations"}), 500
    finally:
        if cursor:
            cursor.close()

#CCS
@colleges_bp.route('/api/ccs/organizations')
def get_ccs_organizations():
    from app import mysql
    cursor = None
    try:
        connection = mysql.connection
        cursor = connection.cursor()
        query = """
            SELECT org_id, org_name 
            FROM organization 
            WHERE college_id = 3
            ORDER BY 
                CASE WHEN org_name LIKE '%Executive Council%' THEN 1 ELSE 2 END, 
                org_name ASC;
        """
        cursor.execute(query)
        organizations = cursor.fetchall()
        return jsonify([{"id": org[0], "name": org[1]} for org in organizations])
    except Exception as e:
        print(f"Error in get_ccs_organizations: {e}")
        return jsonify({"error": "Failed to fetch organizations"}), 500
    finally:
        if cursor:
            cursor.close()

#CED
@colleges_bp.route('/api/ced/organizations')
def get_ced_organizations():
    from app import mysql
    cursor = None
    try:
        connection = mysql.connection
        cursor = connection.cursor()
        query = """
            SELECT org_id, org_name 
            FROM organization 
            WHERE college_id = 4
            ORDER BY 
                CASE WHEN org_name LIKE '%Executive Council%' THEN 1 ELSE 2 END, 
                org_name ASC;
        """
        cursor.execute(query)
        organizations = cursor.fetchall()
        return jsonify([{"id": org[0], "name": org[1]} for org in organizations])
    except Exception as e:
        print(f"Error in get_ccs_organizations: {e}")
        return jsonify({"error": "Failed to fetch organizations"}), 500
    finally:
        if cursor:
            cursor.close()

#CHS
@colleges_bp.route('/api/chs/organizations')
def get_chs_organizations():
    from app import mysql
    cursor = None
    try:
        connection = mysql.connection
        cursor = connection.cursor()
        query = """
            SELECT org_id, org_name 
            FROM organization 
            WHERE college_id = 6
            ORDER BY 
                CASE WHEN org_name LIKE '%Executive Council%' THEN 1 ELSE 2 END, 
                org_name ASC;
        """
        cursor.execute(query)
        organizations = cursor.fetchall()
        return jsonify([{"id": org[0], "name": org[1]} for org in organizations])
    except Exception as e:
        print(f"Error in get_ccs_organizations: {e}")
        return jsonify({"error": "Failed to fetch organizations"}), 500
    finally:
        if cursor:
            cursor.close()

#COE
@colleges_bp.route('/api/coe/organizations')
def get_coe_organizations():
    from app import mysql
    cursor = None
    try:
        connection = mysql.connection
        cursor = connection.cursor()
        query = """
            SELECT org_id, org_name 
            FROM organization 
            WHERE college_id = 5
            ORDER BY 
                CASE WHEN org_name LIKE '%Executive Council%' THEN 1 ELSE 2 END, 
                org_name ASC;
        """
        cursor.execute(query)
        organizations = cursor.fetchall()
        return jsonify([{"id": org[0], "name": org[1]} for org in organizations])
    except Exception as e:
        print(f"Error in get_ccs_organizations: {e}")
        return jsonify({"error": "Failed to fetch organizations"}), 500
    finally:
        if cursor:
            cursor.close()

#CSM
@colleges_bp.route('/api/csm/organizations')
def get_csm_organizations():
    from app import mysql
    cursor = None
    try:
        connection = mysql.connection
        cursor = connection.cursor()
        query = """
            SELECT org_id, org_name 
            FROM organization 
            WHERE college_id = 7
            ORDER BY 
                CASE WHEN org_name LIKE '%Executive Council%' THEN 1 ELSE 2 END, 
                org_name ASC;
        """
        cursor.execute(query)
        organizations = cursor.fetchall()
        return jsonify([{"id": org[0], "name": org[1]} for org in organizations])
    except Exception as e:
        print(f"Error in get_ccs_organizations: {e}")
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

#CCS
