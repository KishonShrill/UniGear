from flask import Blueprint, jsonify, render_template, current_app

website_bp = Blueprint('website', __name__)

@website_bp.route('/')
def landing():
    return render_template('landing.html')

@website_bp.route('/explore')
def explore():
    from app import mysql
    cursor = mysql.connection.cursor()

    query = """
        SELECT p.product_id AS 'Product', 
               col.college_name AS 'College', 
               pic.picture_url AS 'Picture'
        FROM products p
        LEFT JOIN user u ON p.seller_id = u.user_id
        LEFT JOIN organization org ON u.org_id = org.org_id
        LEFT JOIN college col ON org.college_id = col.college_id
        LEFT JOIN pictures pic ON p.product_id = pic.picture_id
    """
    cursor.execute(query)
    result = cursor.fetchall()

    merchandise_data = {}
    for row in result:
        college = row[1]
        if college not in merchandise_data:
            merchandise_data[college] = []

        merchandise_data[college].append({
            'product_id': row[0],
            'picture_url': row[2] if row[2] else '/static/images/placeholder.jpg'
        })

    # Define the order of colleges
    college_order = [
        'College of Arts and Sciences',
        'College of Computer Studies',
        'College of Business Administration',
        'College of Health Sciences',
        'College of Education',
        'College of Engineering',
        'College of Science and Mathematics'
    ]

    # Sort merchandise_data according to the defined order
    sorted_merchandise_data = {college: merchandise_data.get(college, []) for college in college_order}

    college_colors = {
        'College of Arts and Sciences': '#324831',
        'College of Computer Studies': '#598181',
        'College of Business Administration': '#9A9A71',
        'College of Health Sciences': '#8B9EAF',
        'College of Education': '#414459',
        'College of Engineering': '#593838',
        'College of Science and Mathematics': '#934F50'
    }

    return render_template('explore.html', merchandise_data=sorted_merchandise_data, college_colors=college_colors)
from flask import Blueprint, jsonify, render_template, current_app

website_bp = Blueprint('website', __name__)

@website_bp.route('/')
def landing():
    return render_template('landing.html')

@website_bp.route('/explore')
def explore():
    from app import mysql
    cursor = mysql.connection.cursor()

    query = """
        SELECT p.product_id AS 'Product', 
               col.college_name AS 'College', 
               pic.picture_url AS 'Picture'
        FROM products p
        LEFT JOIN user u ON p.seller_id = u.user_id
        LEFT JOIN organization org ON u.org_id = org.org_id
        LEFT JOIN college col ON org.college_id = col.college_id
        LEFT JOIN pictures pic ON p.product_id = pic.picture_id
    """
    cursor.execute(query)
    result = cursor.fetchall()

    merchandise_data = {}
    for row in result:
        college = row[1]
        if college not in merchandise_data:
            merchandise_data[college] = []

        merchandise_data[college].append({
            'product_id': row[0],
            'picture_url': row[2] if row[2] else '/static/images/placeholder.jpg'
        })

    # Define the order of colleges
    college_order = [
        'College of Arts and Sciences',
        'College of Computer Studies',
        'College of Business Administration',
        'College of Health Sciences',
        'College of Education',
        'College of Engineering',
        'College of Science and Mathematics'
    ]

    # Sort merchandise_data according to the defined order
    sorted_merchandise_data = {college: merchandise_data.get(college, []) for college in college_order}

    college_colors = {
        'College of Arts and Sciences': '#324831',
        'College of Computer Studies': '#598181',
        'College of Business Administration': '#9A9A71',
        'College of Health Sciences': '#8B9EAF',
        'College of Education': '#414459',
        'College of Engineering': '#593838',
        'College of Science and Mathematics': '#934F50'
    }

    return render_template('explore.html', merchandise_data=sorted_merchandise_data, college_colors=college_colors)
