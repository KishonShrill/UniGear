from app import mysql
from datetime import datetime
from flask import current_app

class Product(object):
    def __init__(self, product_name, description, hook=None, type=None, price=0.0, order_type=0, seller_id=None):
        self.product_id = None
        self.product_name = product_name
        self.description = description
        self.hook = hook
        self.type = type
        self.price = price
        self.order_type = bool(order_type)
        self.seller_id = seller_id

    def save(self):
        """Save a new product to the database."""
        query = """
        INSERT INTO products (product_name, description, hook, type, price, order_type, seller_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = mysql.connection.cursor()
        cursor.execute(query, (self.product_name, self.description, self.hook, self.type, self.price, self.order_type, self.seller_id))
        mysql.connection.commit()
        self.product_id = cursor.lastrowid
        cursor.close()



    def getID(self):
        return self.product_id

    def add_product_sizes(self, product_quantity, size_id):
        """Add sizes to the product."""
        query = """
        INSERT INTO product_sizes (product_id, product_quantity, size_id)
        VALUES (%s, %s, %s)
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query, (self.product_id, product_quantity, size_id))
        mysql.connection.commit()
        cursor.close()

    def add_product_pictures(self, picture_url):
        """Add sizes to the product."""
        query = """
        INSERT INTO pictures (picture_id, picture_url)
        VALUES (%s, %s)
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query, (self.product_id, picture_url))
        mysql.connection.commit()
        cursor.close()
         

    @staticmethod
    def get_by_name(product_name):
        """Retrieve a product by its name."""
        query = "SELECT * FROM products WHERE product_name = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (product_name,))
        product = cursor.fetchone()
        cursor.close()
        return product

    @staticmethod
    def update(product_id, product_name=None, description=None, hook=None, type=None, price=None, order_type=None):
        """Update product details."""
        query = """
        UPDATE products
        SET 
            product_name = COALESCE(%s, product_name),
            description = COALESCE(%s, description),
            hook = COALESCE(%s, hook),
            type = COALESCE(%s, type),
            price = COALESCE(%s, price),
            order_type = COALESCE(%s, order_type),
            updated_at = %s
        WHERE product_id = %s
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query, (product_name, description, hook, type, price, order_type, datetime.now(), product_id))
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def delete(product_id):
        """Delete a product by its ID."""
        query = "DELETE FROM products WHERE product_id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (product_id,))
        mysql.connection.commit()
        cursor.close()




    @staticmethod
    def get_by_id(product_id):
        """Retrieve a product by its ID."""
        try:
            with mysql.connection.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM products WHERE product_id = %s"
                cursor.execute(query, (product_id,))
                product = cursor.fetchone()

            if product is None:
                current_app.logger.warning(f"Product with ID {product_id} not found.")
                return None
            
            return product
        
        except Exception as e:
            current_app.logger.error(f"Error fetching product by ID {product_id}: {e}")
            return None

    @staticmethod
    def update_preorder_count(product_id, quantity):
        """Update the pre-order count for a product."""
        query = "UPDATE products SET preorder_count = preorder_count + %s WHERE product_id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (quantity, product_id))
        mysql.connection.commit()
        cursor.close()