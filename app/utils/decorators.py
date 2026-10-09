from functools import wraps

from flask import abort, flash, session


def login_is_required(f):
    """Decorator to require user authentication on protected routes."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "id" not in session:
            return abort(401)
        return f(*args, **kwargs)

    return decorated_function


def seller_required(f):
    """Decorator to require seller role authorization on protected routes."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "id" not in session:
            flash("You must be logged in to access this page.", "warning")
            return abort(401)

        user_role = session.get("role")
        if not user_role or user_role.lower() != "seller":
            flash("Access denied. Only sellers can access this page.", "danger")
            return abort(403)

        return f(*args, **kwargs)

    return decorated_function
