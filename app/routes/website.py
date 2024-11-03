from flask import Blueprint, render_template

website_bp = Blueprint('website', __name__)

@website_bp.route('/')
def landing():
  return render_template('landing.html')


@website_bp.route('/explore')
def explore():
  ...