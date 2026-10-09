import os
from datetime import timedelta
from dotenv import load_dotenv

# Automatically load .env file if present
load_dotenv()


def _get_bool_env(key: str, default: bool = False) -> bool:
    """Parse boolean values from environment variables safely."""
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "t", "yes", "y")


def _get_int_env(key: str, default: int | None = None) -> int | None:
    """Parse integer values from environment variables safely."""
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return int(val.strip())
    except (ValueError, TypeError):
        return default


class Config:
    """Base configuration shared across all environments."""

    # Flask Core
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret-key-change-in-prod")
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB max file upload
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    # MySQL Database Config (Flask-MySQLdb)
    MYSQL_USER = os.getenv("DB_USERNAME", "root")
    MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "")
    MYSQL_DB = os.getenv("DB_NAME", "college_marketplace")
    MYSQL_HOST = os.getenv("DB_HOST", "localhost")
    MYSQL_UNIX_SOCKET = os.getenv("DB_UNIX_SOCKET") or None

    # Cloudinary Credentials
    CLOUD_NAME = os.getenv("CLOUD_NAME", "")
    API_KEY = os.getenv("API_KEY", "")
    API_SECRET = os.getenv("API_SECRET", "")

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv(
        "GOOGLE_CLIENT_ID",
        "888454362739-8khch6t2lesrhrevs4s22h739a9ek8gh.apps.googleusercontent.com",
    )

    # Email / Mailtrap Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
    MAIL_PORT = _get_int_env("MAIL_PORT", 2525)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_USE_TLS = _get_bool_env("MAIL_USE_TLS", True)
    MAIL_USE_SSL = _get_bool_env("MAIL_USE_SSL", False)


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration with secure cookie policies."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(env_name: str | None = None) -> type[Config]:
    """Retrieve configuration class based on environment name or FLASK_ENV."""
    if env_name is None:
        env_name = os.getenv("FLASK_ENV", os.getenv("ENV", "development")).lower()
    return CONFIG_MAP.get(env_name, DevelopmentConfig)


# ==============================================================================
# Backwards-compatible module-level constants for existing imports
# ==============================================================================
_active_config = get_config()

DB_NAME = _active_config.MYSQL_DB
DB_USERNAME = _active_config.MYSQL_USER
DB_PASSWORD = _active_config.MYSQL_PASSWORD
DB_HOST = _active_config.MYSQL_HOST
DB_UNIX_SOCKET = _active_config.MYSQL_UNIX_SOCKET

CLOUD_NAME = _active_config.CLOUD_NAME
API_KEY = _active_config.API_KEY
API_SECRET = _active_config.API_SECRET

MAILTRAP_SERVER = _active_config.MAIL_SERVER
MAILTRAP_PORT = _active_config.MAIL_PORT
MAILTRAP_USERNAME = _active_config.MAIL_USERNAME
MAILTRAP_PASSWORD = _active_config.MAIL_PASSWORD
MAILTRAP_USE_TLS = _active_config.MAIL_USE_TLS
MAILTRAP_USE_SSL = _active_config.MAIL_USE_SSL

SECRET_KEY = _active_config.SECRET_KEY
