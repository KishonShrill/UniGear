import cloudinary
from flask import Flask
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY
from config import CLOUD_NAME, API_KEY, API_SECRET
from datetime import timedelta

mysql = MySQL()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        MYSQL_USER=DB_USERNAME,
        MYSQL_PASSWORD=DB_PASSWORD,
        MYSQL_DB=DB_NAME,
        MYSQL_HOST=DB_HOST,
        #BOOTSTRAP_SERVE_LOCAL=BOOTSTRAP_SERVE_LOCAL
    )

    # Set the max upload size to 25MB (in bytes)
    app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB

    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET,
        secure=True
    )

    mysql.init_app(app)
    CSRFProtect(app)
    app.permanent_session_lifetime = timedelta(days=1)  # Session lasts 1 day

    # Gather Routes
    from app.routes.auth import auth_bp
    from app.routes.website import website_bp
    from app.routes.user import seller_bp
    from app.routes.colleges import colleges_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(website_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(colleges_bp)

    return app