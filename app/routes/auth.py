from flask import Blueprint, render_template, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sign-in')
def sign_in():
  ...

@auth_bp.route('/sign-up')
def sign_up():
  ...