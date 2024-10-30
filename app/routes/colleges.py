from flask import Blueprint, render_template

colleges_bp = Blueprint('colleges', __name__)

@colleges_bp.route('/college-cass')
def college_cass():
  ...

# Similar routes for college 2 to 8
