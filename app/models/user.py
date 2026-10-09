"""User model representing application users and sellers."""
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.db import get_db_cursor
from app.utils.helpers import split_address


class User(object):
    """User domain model for authentication and profile management."""

    def __init__(
        self,
        user_id=None,
        user_name=None,
        user_email=None,
        user_password=None,
        user_contact=None,
        user_address=None,
        user_role=None,
        org_id=None,
    ):
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password
        self.user_contact = user_contact
        self.user_address = user_address
        self.user_role = user_role
        self.org_id = org_id

    @property
    def parsed_address(self):
        """Return (street, barangay, city) tuple parsed from user_address."""
        return split_address(self.user_address)

    def save(self):
        """Save the current user instance to the database."""
        with get_db_cursor(commit=True) as cursor:
            if self.user_id:
                cursor.execute(
                    """
                    UPDATE user
                    SET user_name = %s, user_email = %s, user_password = %s, user_contact = %s, user_address = %s, user_role = %s, org_id = %s
                    WHERE user_id = %s
                    """,
                    (
                        self.user_name,
                        self.user_email,
                        self.user_password,
                        self.user_contact,
                        self.user_address,
                        self.user_role,
                        self.org_id,
                        self.user_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO user (user_name, user_email, user_password, user_contact, user_address, user_role, org_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        self.user_name,
                        self.user_email,
                        self.user_password,
                        self.user_contact,
                        self.user_address,
                        self.user_role,
                        self.org_id,
                    ),
                )
                self.user_id = cursor.lastrowid

    def verify_password(self, password):
        """Verify password against stored password hash."""
        if not self.user_password:
            return False
        return check_password_hash(self.user_password, password)

    @staticmethod
    def get_by_email(email):
        """Retrieve a user from the database using their email."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, user_name, user_email, user_password, user_contact, user_address, user_role, org_id
                FROM user
                WHERE user_email = %s
                """,
                (email,),
            )
            result = cursor.fetchone()

            if result:
                return User(
                    user_id=result[0],
                    user_name=result[1],
                    user_email=result[2],
                    user_password=result[3],
                    user_contact=result[4],
                    user_address=result[5],
                    user_role=result[6],
                    org_id=result[7],
                )
            return None

    @classmethod
    def get_by_id(cls, user_id):
        """Retrieve a user by their user ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, user_name, user_email, user_password, user_contact, user_address, user_role, org_id
                FROM user
                WHERE user_id = %s
                """,
                (user_id,),
            )
            result = cursor.fetchone()

            if result:
                return cls(*result)
            return None

    @classmethod
    def create_from_google(cls, google_name, google_email, google_contact=None, google_address=None):
        """Create a new user from Google OAuth data."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO user (user_name, user_email, user_role, user_contact, user_address)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (google_name, google_email, "seller", google_contact, google_address),
            )
            user_id = cursor.lastrowid

        return cls(user_id=user_id, user_name=google_name, user_email=google_email, user_role="seller")

    @classmethod
    def create_from_website(cls, name, email, password=None, contact=None, address=None):
        """Create a new standard user from website registration."""
        generated_password = None
        if password:
            generated_password = generate_password_hash(password)

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO user (user_name, user_email, user_password, user_contact, user_address, user_role)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, email, generated_password, contact, address, "user"),
            )
            user_id = cursor.lastrowid

        return cls(user_id=user_id, user_name=name, user_email=email, user_role="user")
