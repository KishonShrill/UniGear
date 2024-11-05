from flask import Blueprint, render_template
from app.forms import *

website_bp = Blueprint('website', __name__)

@website_bp.route('/')
def landing():
  return render_template('landing.html')


@website_bp.route('/explore')
def explore():
  ...


@website_bp.route('/product/new')
def product_new():
  form = ProductForm()
  return render_template('/crud_blueprint/product_page-create.html', form=form)