from app import mysql
from werkzeug.security import generate_password_hash, check_password_hash

class User(object):
    def __init__(self, user_id=None, user_name=None, user_email=None, user_password=None, user_contact=None, user_address=None, user_role=None, org_id=None):
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password
        self.user_contact = user_contact
        self.user_address = user_address
        self.user_role = user_role
        self.org_id = org_id

    @classmethod
    def get_by_email(cls, email):
        """Retrieve a user by their email address."""
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE user_email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return cls(*result)  # Return an instance of the User class
        return None

    @classmethod
    def get_by_id(cls, user_id):
        """Retrieve a user by their user ID."""
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return cls(*result)  # Return an instance of the User class
        return None

    @classmethod
    def create_from_google(cls, google_name, google_email, google_contact=None, google_address=None):
        """Create a new user from Google OAuth data."""
        # Create the user in the database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO user (user_name, user_email, user_role, user_contact, user_address)
            VALUES (%s, %s, %s, %s, %s)
        """, (google_name, google_email, "seller", google_contact, google_address))

        mysql.connection.commit()
        user_id = cursor.lastrowid  # Get the user_id of the newly inserted user
        cursor.close()

        return cls(user_id=user_id, user_name=google_name, user_email=google_email)
    
    @classmethod
    def create_from_google(cls, name, email, password, contact, address):
        """Create a new user from Google OAuth data."""
        generated_password = generate_password_hash(password)
        
        # Create the user in the database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO user (user_name, user_email, user_password, user_contact, user_address, user_role)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, generated_password, contact, address, "user"))

        mysql.connection.commit()
        user_id = cursor.lastrowid  # Get the user_id of the newly inserted user
        cursor.close()

        return cls(user_id=user_id, user_name=name, user_email=email)

    def save(self):
        """Save the current user instance to the database."""
        cursor = mysql.connection.cursor()

        if self.user_id:
            cursor.execute("""
                UPDATE user
                SET user_name = %s, user_email = %s, user_password = %s, user_contact = %s, user_address = %s
                WHERE user_id = %s
            """, (self.user_name, self.user_email, self.user_password, self.user_contact, self.user_address, self.user_id))
        else:
            cursor.execute("""
                INSERT INTO user (user_name, user_email, user_password, user_contact, user_address)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.user_name, self.user_email, self.user_password, self.user_contact, self.user_address))

        mysql.connection.commit()
        cursor.close()

    def verify_password(self, password):
        """Verify if the provided password matches the stored hash."""
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT *
                FROM user
                WHERE user_email = %s
            """, ())
            database_password = cursor.fetchone()
            return check_password_hash(database_password, password)
        except Exception as e:
            print(f"Password does not match: {e}")
            return 0