from flask import Blueprint, render_template, redirect, url_for, flash, session, abort, request, current_app
from google.oauth2 import id_token
from google.auth.transport import requests
from app.models.user import User
from app.forms import LinkVerify, SignUpForm
from app.utils.decorators import login_is_required, seller_required


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/sign-in')
def sign_in():
    form = LinkVerify()
    return render_template('sign_in.html', form=form)


# The route to render the sign-up page
@auth_bp.route('/sign-up')
def sign_up():
    form = SignUpForm()
    return render_template('sign_up.html', form=form)


@auth_bp.route('/sign-up2', methods=['GET', 'POST'])
def sign_up2():
    form = SignUpForm()
    if request.method == 'POST':
        # Check if password confirmation match
        if form.password.data != form.repassword.data:
            flash("Password confirmation don't match", "warning")
            return redirect(url_for('auth.sign_up'))

        # Handle form submission
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        return render_template('sign_up2.html', username=username, email=email, password=password, form=form)
    if request.method == 'GET':
        return redirect(url_for('auth.sign_up'))


@auth_bp.route('/sign-up/submit', methods=['GET', 'POST'])
def submit_sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        city = request.form.get('city')
        barangay = request.form.get('barangay')
        street = request.form.get('address')
        contact = request.form.get('contact')

        # Combine the address
        address = f"{street}, {barangay}, {city}"

        # Check if user exists or create new one
        user = User.get_by_email(email)

        if not user:
            try:
                user = User.create_from_website(username, email, password, contact, address)
            except Exception:
                flash("The contact number is already used...", "warning")
                return redirect(url_for('auth.sign_up'))

        flash("Account created successfully...", "success")
        return redirect(url_for('auth.sign_in'))

    if request.method == "GET":
        abort(404)


@auth_bp.route('/auth/callback', methods=['POST'])
def callback():
    form = LinkVerify()
    if request.method == 'POST':
        # Simulated authentication / standard form login
        get_email = request.form.get("email")
        get_password = request.form.get("password")

        # Check if user exists
        user = User.get_by_email(get_email)
        if not user:
            flash("User does not exist", "warning")
            return render_template('sign_in.html', form=form)

        # Check if password matches database hash
        is_login = user.verify_password(get_password)
        if not is_login:
            flash("Password does not match", "warning")
            return render_template('sign_in.html', form=form)

        # Store user info in session
        session['id'] = user.user_id
        session['name'] = user.user_name
        session['email'] = user.user_email
        session['role'] = user.user_role
        session['org_id'] = user.org_id

        flash(f"Welcome {user.user_name}", "success")
        return redirect(url_for('website.explore'))

    if request.method == 'GET':
        return redirect(url_for('website.landing'))


@auth_bp.route('/auth/google_callback')
def google_callback():
    form = LinkVerify()
    token = request.args.get("credential")

    if not token:
        flash("Token is not being received properly.", "warning")
        return redirect(url_for('auth.sign_in', form=form))

    try:
        # Verify the token against configured Google Client ID
        client_id = current_app.config.get(
            "GOOGLE_CLIENT_ID",
            "888454362739-8khch6t2lesrhrevs4s22h739a9ek8gh.apps.googleusercontent.com",
        )
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=client_id,
            clock_skew_in_seconds=1000,
        )

        # Store user info in session
        session['name'] = idinfo.get('name')
        session['email'] = idinfo.get('email')
        session['picture'] = idinfo.get('picture')

        # Check if user exists or create new one
        user = User.get_by_email(idinfo.get('email'))
        if not user:
            user = User.create_from_website(idinfo.get('name'), idinfo.get('email'))

        session['id'] = user.user_id
        session['role'] = user.user_role
        session['org_id'] = user.org_id

        flash(f"Welcome {idinfo.get('name')}", "success")
        return redirect(url_for('website.explore'))
    except ValueError:
        return "Invalid token", 400
    except Exception:
        return "An error occurred during authentication. Please try again.", 500


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("User has logged out...", "success")
    return redirect(url_for('website.explore'))
