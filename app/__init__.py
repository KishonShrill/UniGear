import cloudinary
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
#from flask_mysqldb import MySQL

#mysql = MySQL(app)

from config import get_config



def create_app(test_config=None):
    """Application factory for UniGear Flask app."""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    config_class = get_config()
    app.config.from_object(config_class)

    if test_config is not None:
        if isinstance(test_config, dict):
            app.config.from_mapping(test_config)
        else:
            app.config.from_object(test_config)

    # Error Page Handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("./components/404.html"), 404

    @app.errorhandler(401)
    def not_logged_in(e):
        return render_template("./components/401.html"), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("./components/403.html"), 403

    # Initialize Cloudinary SDK
    cloudinary.config(
        cloud_name=app.config.get("CLOUD_NAME"),
        api_key=app.config.get("API_KEY"),
        api_secret=app.config.get("API_SECRET"),
        secure=True,
    )

    # Initialize Extensions
    #mysql.init_app(app)
    CSRFProtect(app)

    # Register Blueprints
    from app.cli import register_cli_commands
    from app.routes.auth import auth_bp
    from app.routes.colleges import colleges_bp
    from app.routes.seller import seller_bp
    from app.routes.user import user_bp
    from app.routes.website import website_bp

    register_cli_commands(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(website_bp)
    app.register_blueprint(colleges_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(user_bp)

    return app
