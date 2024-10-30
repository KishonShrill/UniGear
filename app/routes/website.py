from flask import Blueprint, render_template

website_bp = Blueprint('website', __name__)

@website_bp.route('/')
def landing():
  return "<h1>Hello, World!</h1>"


@website_bp.route('/explore')
def explore():
  ...