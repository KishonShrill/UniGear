from flask import Blueprint, render_template, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sign-in')
def sign_in():
  return render_template('sign_in.html')

@auth_bp.route('/sign-up')
def sign_up():
  ...