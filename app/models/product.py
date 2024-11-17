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
    def getOrders():
        try:
            # Create a connection object
            cursor = mysql.connection.cursor()

            # Define the SQL query
            query = """
            SELECT 
                ob.order_id,
                u.user_name,
                ob.total_cost,
                p.product_name,
                s.size_name,
                ob.quantity,
                p.order_type,
                ob.purchase_date
            FROM ordered_by ob
            JOIN user u ON ob.user_id = u.user_id
            JOIN products p ON ob.product_id = p.product_id
            JOIN sizes s ON ob.size_id = s.size_id;
            """

            # Execute the query
            cursor.execute(query)

            # Fetch all results
            result = cursor.fetchall()

            # Process the results into a list of dictionaries
            orders = []
            for row in result:
                order = {
                    'Order': row[0],
                    'Customer': row[1],
                    'Total Cost': row[2],
                    'Product': row[3],
                    'Size': row[4],
                    'Quantity': row[5],
                    'Status': row[6],
                    'Purchase Date': row[7]
                }
                orders.append(order)

            # Close the cursor and connection
            cursor.close()

            return orders  # Return the orders list

        except Exception as e:
            print(f"Error occurred: {e}")
            return None