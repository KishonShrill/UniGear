#from MySQLdb.cursors import DictCursor
from psycopg.rows import dict_row

from app.utils.db import get_db_cursor


class Favorite:
    def __init__(self, favorite_id=None, user_id=None, product_id=None):
        self.favorite_id = favorite_id
        self.user_id = user_id
        self.product_id = product_id

    @staticmethod
    def get_user_wishlist(user_id):
        """Retrieve full wishlist items with product and college details for a user."""
        query = """
            WITH PictureSelection AS (
                SELECT
                    p.product_id,
                    pic.picture_url,
                    ROW_NUMBER() OVER (PARTITION BY p.product_id ORDER BY pic.picture_url) AS row_num
                FROM products p
                LEFT JOIN pictures pic ON p.product_id = pic.picture_id
            )
            SELECT
                f.favorite_id AS 'Favorite ID',
                f.user_id AS 'User ID',
                p.product_id AS 'Product',
                p.product_name AS 'Name',
                p.description AS 'Description',
                col.college_name AS 'College',
                ps.picture_url AS 'Picture'
            FROM favorites f
            LEFT JOIN products p ON f.product_id = p.product_id
            LEFT JOIN user u ON p.seller_id = u.user_id
            LEFT JOIN organization org ON u.org_id = org.org_id
            LEFT JOIN college col ON org.college_id = col.college_id
            LEFT JOIN PictureSelection ps ON p.product_id = ps.product_id AND ps.row_num = 1
            WHERE f.user_id = %s
            GROUP BY f.favorite_id, f.user_id, p.product_id, p.product_name, p.description, col.college_name, ps.picture_url;
        """
        with get_db_cursor(cursorclass=dict_row) as cursor:
            cursor.execute(query, (user_id,))
            return cursor.fetchall()

    @staticmethod
    def is_favorite(user_id, product_id):
        """Check if a specific product is marked as favorite by the user."""
        if not user_id or not product_id:
            return False
        query = "SELECT 1 FROM favorites WHERE user_id = %s AND product_id = %s LIMIT 1"
        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id, product_id))
            return cursor.fetchone() is not None

    @staticmethod
    def toggle(user_id, product_id):
        """Toggle favorite status for a user and product atomically.

        Returns:
            tuple: (success: bool, is_now_favorite: bool)
        """
        if not user_id or not product_id:
            return False, False

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "SELECT favorite_id FROM favorites WHERE user_id = %s AND product_id = %s",
                (user_id, product_id),
            )
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    "DELETE FROM favorites WHERE user_id = %s AND product_id = %s",
                    (user_id, product_id),
                )
                return True, False
            else:
                cursor.execute(
                    "INSERT INTO favorites (user_id, product_id) VALUES (%s, %s)",
                    (user_id, product_id),
                )
                return True, True
