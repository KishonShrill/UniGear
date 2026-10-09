"""Product model managing product catalog, inventory sizes, and organization queries."""

import logging
from datetime import datetime

from MySQLdb.cursors import DictCursor

from app.utils.db import get_db_cursor

logger = logging.getLogger(__name__)


class Product:
    def __init__(
        self,
        product_name=None,
        description=None,
        hook=None,
        type=None,
        price=0.0,
        order_type=0,
        seller_id=None,
        product_id=None,
        release_date=None,
    ):
        self.product_id = product_id
        self.product_name = product_name
        self.description = description
        self.hook = hook
        self.type = type
        self.price = price
        self.order_type = order_type
        self.seller_id = seller_id
        self.release_date = release_date

    def save(self):
        """Save a new product to the database."""
        query = """
        INSERT INTO products (product_name, description, hook, type, price, order_type, seller_id, release_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    self.product_name,
                    self.description,
                    self.hook,
                    self.type,
                    self.price,
                    self.order_type,
                    self.seller_id,
                    self.release_date,
                ),
            )
            self.product_id = cursor.lastrowid

    def update(self):
        """Update an existing product in the database."""
        try:
            query = """
            UPDATE products
            SET
                product_name = %s,
                description = %s,
                hook = %s,
                type = %s,
                price = %s,
                order_type = %s,
                seller_id = %s,
                release_date = %s,
                updated_at = %s
            WHERE product_id = %s;
            """
            if self.release_date == "":
                self.release_date = None

            with get_db_cursor(commit=True) as cursor:
                cursor.execute(
                    query,
                    (
                        self.product_name,
                        self.description,
                        self.hook,
                        self.type,
                        self.price,
                        self.order_type,
                        self.seller_id,
                        self.release_date,
                        datetime.now(),
                        self.product_id,
                    ),
                )
        except AttributeError as e:
            logger.error("AttributeError during product update: %s", e)
        except Exception as e:
            logger.error("Error updating product %s: %s", self.product_id, e)

    def countPreorder(self):
        """Count preorders and fetch preorder goal."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT SUM(product_quantity) FROM product_sizes WHERE product_id = %s",
                (self.product_id,),
            )
            count_row = cursor.fetchone()
            count = count_row[0] if count_row and count_row[0] is not None else 0

            cursor.execute(
                "SELECT preorder_goal FROM products WHERE product_id = %s",
                (self.product_id,),
            )
            goal_row = cursor.fetchone()
            goal = goal_row[0] if goal_row and goal_row[0] is not None else 0

            return count, goal

    def getID(self):
        return self.product_id

    def clear_sizes(self, product_id):
        """Delete all sizes for a given product."""
        query = "DELETE FROM product_sizes WHERE product_id = %s"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (product_id,))

    def add_product_sizes(self, size_id):
        """Add size association to the product."""
        query = """
        INSERT INTO product_sizes (product_id, product_quantity, size_id)
        VALUES (%s, 0, %s)
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (self.product_id, size_id))

    def delete_product_sizes(self):
        """Delete all product sizes for this product."""
        query = "DELETE FROM product_sizes WHERE product_id = %s"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (self.product_id,))

    def init_product_pictures(self, picture_url):
        """Add initial picture URL for the product."""
        query = """
        INSERT INTO pictures (picture_id, picture_url)
        VALUES (%s, %s)
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (self.product_id, picture_url))

    def remove_product_picture(self, picture_id):
        """Remove pictures for the product."""
        query = "DELETE FROM pictures WHERE picture_id = %s"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (picture_id,))

    def goal_to_time(self, release_date):
        """Transition product order type to time-based preorder."""
        try:
            query = """
                UPDATE products
                SET
                    order_type = 1,
                    release_date = %s
                WHERE product_id = %s;
            """
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(query, (release_date, self.product_id))
        except Exception as e:
            logger.error(
                "Error transitioning product %s from goal to time: %s",
                self.product_id,
                e,
            )

    @staticmethod
    def add_product_pictures(product_id, picture_url):
        """Add picture to product."""
        query = """
        INSERT INTO pictures (picture_id, picture_url)
        VALUES (%s, %s)
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (product_id, picture_url))

    @staticmethod
    def fetch_product_pictures(product_id):
        """Fetch pictures for the product."""
        query_fetch = "SELECT picture_url FROM pictures WHERE picture_id = %s"
        with get_db_cursor() as cursor:
            cursor.execute(query_fetch, (product_id,))
            return {row[0] for row in cursor.fetchall()}

    @staticmethod
    def delete_product_pictures(product_url):
        """Delete pictures of the product by URL."""
        query_fetch = "DELETE FROM pictures WHERE picture_url = %s;"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query_fetch, (product_url,))

    def update_pictures(self, picture_urls):
        """Update pictures for the product."""
        with get_db_cursor(commit=True) as cursor:
            query_fetch = "SELECT picture_url FROM pictures WHERE picture_id = %s"
            cursor.execute(query_fetch, (self.product_id,))
            existing_pictures = {row[0] for row in cursor.fetchall()}

            for picture_url in picture_urls:
                if picture_url not in existing_pictures:
                    query_insert = """
                    INSERT INTO pictures (picture_id, picture_url)
                    VALUES (%s, %s)
                    """
                    cursor.execute(query_insert, (self.product_id, picture_url))

    @staticmethod
    def get_by_name(product_name):
        """Retrieve a product by its name."""
        query = "SELECT * FROM products WHERE product_name = %s"
        with get_db_cursor() as cursor:
            cursor.execute(query, (product_name,))
            return cursor.fetchone()

    @staticmethod
    def get_by_id(product_id):
        """Retrieve a product by its ID."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT product_id, product_name, description, hook, type, price, order_type, seller_id
                FROM products
                WHERE product_id = %s
                """,
                (product_id,),
            )
            result = cursor.fetchone()

            if result:
                return Product(
                    product_id=result[0],
                    product_name=result[1],
                    description=result[2],
                    hook=result[3],
                    type=result[4],
                    price=result[5],
                    order_type=result[6],
                    seller_id=result[7],
                )
            return None

    @staticmethod
    def delete(product_id):
        """Delete a product by its ID."""
        query = "DELETE FROM products WHERE product_id = %s"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (product_id,))

    @staticmethod
    def countProducts(org_id):
        """Count products for a seller organization."""
        try:
            query = """
            SELECT COUNT(*) AS row_count
            FROM products p
            LEFT JOIN user u ON p.seller_id = u.user_id
            WHERE u.org_id = %s;
            """
            with get_db_cursor() as cursor:
                cursor.execute(query, (org_id,))
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            return f"Order Count ERR: {e}"

    @staticmethod
    def getOrders(org_id):
        """Get recent orders for an organization."""
        try:
            query = """
            SELECT
                ob.order_id,
                u.user_name,
                ob.total_cost,
                p.product_name,
                s.size_name,
                ob.quantity,
                p.order_type,
                ob.order_status,
                ob.order_date,
                ob.proof_of_payment
            FROM ordered_by ob
            JOIN user u ON ob.user_id = u.user_id
            JOIN products p ON ob.product_id = p.product_id
            JOIN sizes s ON ob.size_id = s.size_id
            JOIN user seller ON p.seller_id = seller.user_id
            WHERE seller.org_id = %s
            ORDER BY ob.order_id DESC
            LIMIT 10;
            """
            with get_db_cursor() as cursor:
                cursor.execute(query, (org_id,))
                result = cursor.fetchall()
                orders = []
                for row in result:
                    order = {
                        "Order": row[0],
                        "Customer": row[1],
                        "Total Cost": row[2],
                        "Product": row[3],
                        "Size": row[4],
                        "Quantity": row[5],
                        "Type": row[6],
                        "Status": row[7],
                        "Order Date": row[8],
                        "Proof of Payment": row[9],
                    }
                    orders.append(order)
                return orders
        except Exception as e:
            logger.error("Error fetching orders for org %s: %s", org_id, e)
            return None

    @staticmethod
    def getOrdersInPage(org_id, page):
        """Get paginated orders for an organization."""
        try:
            offset = 10 * (page - 1)
            query = """
            SELECT
                ob.order_id,
                u.user_name,
                ob.total_cost,
                p.product_name,
                s.size_name,
                ob.quantity,
                p.order_type,
                ob.order_status,
                ob.order_date,
                ob.proof_of_payment
            FROM ordered_by ob
            JOIN user u ON ob.user_id = u.user_id
            JOIN products p ON ob.product_id = p.product_id
            JOIN sizes s ON ob.size_id = s.size_id
            JOIN user seller ON p.seller_id = seller.user_id
            WHERE seller.org_id = %s
            ORDER BY ob.order_id DESC
            LIMIT 10
            OFFSET %s;
            """
            with get_db_cursor() as cursor:
                cursor.execute(query, (org_id, offset))
                result = cursor.fetchall()
                orders = []
                for row in result:
                    order = {
                        "Order": row[0],
                        "Customer": row[1],
                        "Total Cost": row[2],
                        "Product": row[3],
                        "Size": row[4],
                        "Quantity": row[5],
                        "Type": row[6],
                        "Status": row[7],
                        "Order Date": row[8],
                        "Proof of Payment": row[9],
                    }
                    orders.append(order)
                return orders
        except Exception as e:
            logger.error("Error fetching paginated orders for org %s: %s", org_id, e)
            return None

    @staticmethod
    def countOrdersWithEmail(email):
        """Count total orders associated with a user's email."""
        try:
            query = """
            SELECT COUNT(*) as row_count
            FROM ordered_by ob
            JOIN user u ON ob.user_id = u.user_id
            JOIN products p ON ob.product_id = p.product_id
            JOIN sizes s ON ob.size_id = s.size_id
            WHERE user_email = %s;
            """
            with get_db_cursor() as cursor:
                cursor.execute(query, (email,))
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            logger.error("Error counting orders for email %s: %s", email, e)
            return None

    @staticmethod
    def getOrdersWithEmail(email):
        """Retrieve all orders placed by a user."""
        try:
            query = """
            SELECT
                ob.order_id,
                p.product_name,
                s.size_name,
                ob.quantity,
                ob.total_cost,
                p.order_type,
                ob.order_status,
                ob.order_date,
                p.product_id,
                ob.proof_of_payment
            FROM ordered_by ob
            JOIN user u ON ob.user_id = u.user_id
            JOIN products p ON ob.product_id = p.product_id
            JOIN sizes s ON ob.size_id = s.size_id
            WHERE user_email = %s
            ORDER BY ob.order_id ASC;
            """
            with get_db_cursor() as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchall()
                orders = []
                for row in result:
                    order = {
                        "Order": row[0],
                        "Product": row[1],
                        "Size": row[2],
                        "Quantity": row[3],
                        "Total Cost": row[4],
                        "Type": row[5],
                        "Status": row[6],
                        "Order Date": row[7],
                        "Product ID": row[8],
                        "Proof of Payment": row[9],
                    }
                    orders.append(order)
                return orders
        except Exception as e:
            logger.error("Error fetching orders for email %s: %s", email, e)
            return None

    @staticmethod
    def getProducts(org_id):
        """Retrieve all products for an organization."""
        try:
            query = """
            SELECT
                p.product_id,
                p.product_name,
                p.type,
                p.price,
                p.order_type,
                p.created_at,
                p.updated_at
            FROM products p
            LEFT JOIN user u ON p.seller_id = u.user_id
            WHERE u.org_id = %s
            ORDER BY p.product_id ASC;
            """
            with get_db_cursor() as cursor:
                cursor.execute(query, (org_id,))
                result = cursor.fetchall()
                if not result:
                    return []
                products = []
                for row in result:
                    product = {
                        "Product_id": row[0],
                        "Product_Name": row[1],
                        "Type": row[2],
                        "Price": row[3],
                        "Order-Type": row[4],
                        "Created At": row[5],
                        "Updated At": row[6],
                    }
                    products.append(product)
                return products
        except Exception as e:
            logger.error("Error fetching products for org %s: %s", org_id, e)
            return None

    @staticmethod
    def countOrders(org_id):
        """Count total orders for a seller organization."""
        try:
            query = """
            SELECT COUNT(*) AS row_count
            FROM ordered_by ob
            JOIN user u ON ob.user_id = u.user_id
            JOIN products p ON ob.product_id = p.product_id
            JOIN sizes s ON ob.size_id = s.size_id
            JOIN user seller ON p.seller_id = seller.user_id
            WHERE seller.org_id = %s;
            """
            with get_db_cursor() as cursor:
                cursor.execute(query, (org_id,))
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            logger.error("Error counting orders for org %s: %s", org_id, e)
            return 0

    @staticmethod
    def get_product_pictures(product_id):
        """Get all picture URLs for a given product ID."""
        query = "SELECT picture_url FROM pictures WHERE picture_id = %s"
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (product_id,))
                results = cursor.fetchall()
                return [row[0] for row in results]
        except Exception as e:
            logger.error("Error fetching product pictures for product %s: %s", product_id, e)
            return []

    @staticmethod
    def get_product_sizes(product_id):
        """Get all size IDs for a given product ID."""
        query = "SELECT size_id FROM product_sizes WHERE product_id = %s"
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (product_id,))
                results = cursor.fetchall()
                return [row[0] for row in results]
        except Exception as e:
            logger.error("Error fetching sizes for product %s: %s", product_id, e)
            return []

    @staticmethod
    def get_explore_catalog():
        """Retrieve product catalog grouped by college for the explore page."""
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
                p.product_id AS 'Product',
                p.product_name AS 'Name',
                col.college_name AS 'College',
                ps.picture_url AS 'Picture'
            FROM products p
            LEFT JOIN user u ON p.seller_id = u.user_id
            LEFT JOIN organization org ON u.org_id = org.org_id
            LEFT JOIN college col ON org.college_id = col.college_id
            LEFT JOIN PictureSelection ps ON p.product_id = ps.product_id AND ps.row_num = 1
            GROUP BY p.product_id, p.product_name, col.college_name, ps.picture_url;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_details_by_id(product_id):
        """Retrieve complete details for a product including images, sizes, and total stock."""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT product_id, product_name, description, hook, type, price, order_type, release_date
                FROM products
                WHERE product_id = %s
                """,
                (product_id,),
            )
            product_row = cursor.fetchone()
            if not product_row:
                return None

            product = {
                "product_id": product_row[0],
                "name": product_row[1],
                "description": product_row[2],
                "hook": product_row[3],
                "type": product_row[4],
                "price": product_row[5],
                "order_type": product_row[6],
                "release_date": product_row[7],
            }

            cursor.execute("SELECT picture_url FROM pictures WHERE picture_id = %s", (product_id,))
            images = [img[0] for img in cursor.fetchall()]

            cursor.execute(
                "SELECT size_id, product_quantity FROM product_sizes WHERE product_id = %s",
                (product_id,),
            )
            sizes = cursor.fetchall()

            cursor.execute(
                "SELECT SUM(product_quantity) FROM product_sizes WHERE product_id = %s",
                (product_id,),
            )
            sum_row = cursor.fetchone()
            total_quantity = sum_row[0] if sum_row and sum_row[0] is not None else 0

            return {
                "product": product,
                "images": images,
                "sizes": sizes,
                "total_quantity": total_quantity,
            }

    @staticmethod
    def get_by_organization(org_id, product_type=None):
        """Retrieve products belonging to an organization, with optional type filtering."""
        query = """
            SELECT
                p.product_id AS 'Product',
                p.product_name AS 'Product Name',
                p.description AS 'Description',
                MIN(pi.picture_url) AS 'Picture',
                p.type AS 'Type'
            FROM products p
            LEFT JOIN pictures pi ON p.product_id = pi.picture_id
            LEFT JOIN user u ON p.seller_id = u.user_id
            WHERE u.org_id = %s
        """
        params = [org_id]
        if product_type and product_type != "all":
            query += " AND p.type = %s"
            params.append(product_type)

        query += " GROUP BY p.product_id, p.product_name, p.description, p.type;"

        with get_db_cursor(cursorclass=DictCursor) as cursor:
            cursor.execute(query, params)
            products = cursor.fetchall()
            return [
                {
                    "id": p["Product"],
                    "name": p["Product Name"],
                    "description": p["Description"],
                    "picture": p["Picture"],
                }
                for p in products
            ]
