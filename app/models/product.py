from app import mysql
from datetime import datetime
from flask import current_app
from datetime import datetime

class Product(object):
    def __init__(self, product_name, description, hook=None, type=None, price=0.0, order_type=0, seller_id=None, product_id=None, release_date=None):
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
        
        cursor = mysql.connection.cursor()
        cursor.execute(query, (self.product_name, self.description, self.hook, self.type, self.price, self.order_type, self.seller_id, self.release_date))
        mysql.connection.commit()
        self.product_id = cursor.lastrowid
        cursor.close()
        
    def update(self):
        """Save a new product to the database."""
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
            
            if self.release_date == '':
                self.release_date = None
            
            cursor = mysql.connection.cursor()
            cursor.execute(query, (self.product_name, 
                                   self.description, 
                                   self.hook, 
                                   self.type, 
                                   self.price, 
                                   self.order_type, 
                                   self.seller_id, 
                                   self.release_date, 
                                   datetime.now(),
                                   self.product_id))
            mysql.connection.commit()
            cursor.close()
        except AttributeError as e:
            print(f"AttributeError: {str(e)}")
        except Exception as e:
            print(f"Something went wrong when updating product_id...\n{e}")

    def countPreorder(self):
        cursor = mysql.connection.cursor()
        print(f"Product ID: {self.product_id}")
        
        cursor.execute("SELECT SUM(product_quantity) FROM product_sizes WHERE product_id = %s", (self.product_id,))
        mysql.connection.commit()
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT preorder_goal FROM products WHERE product_id = %s", (self.product_id,))
        mysql.connection.commit()
        goal = cursor.fetchone()[0]
        
        cursor.close()
        return count, goal

    def getID(self):
        return self.product_id

    def clear_sizes(self, product_id):
        """Deleting the sizes that the product had"""
        query = """
        DELETE FROM product_sizes
        WHERE product_id = %s
        """

        cursor = mysql.connection.cursor()  # Ensure cursor is properly initialized
        cursor.execute(query, (product_id,))  # Wrap product_id in a tuple
        mysql.connection.commit()
        cursor.close()

    def add_product_sizes(self, size_id):
        """Add sizes to the product."""
        query = """
        INSERT INTO product_sizes (product_id, product_quantity, size_id)
        VALUES (%s, 0, %s)
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query, (self.product_id, size_id))
        mysql.connection.commit()
        cursor.close()
        
    def delete_product_sizes(self):
        """Delete all product sizes that match the product_id and size_id."""
        query = """
        DELETE FROM product_sizes
        WHERE product_id = %s
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query, (self.product_id))
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
        
    def remove_product_picture(self, picture_id):
        """remove pictures"""
        query = """
        DELETE FROM pictures
        WHERE picture_id = %s
        """
        cursor = mysql.connection.cursor()  # Ensure cursor is properly initialized
        cursor.execute(query, (picture_id,))  # Wrap product_id in a tuple
        mysql.connection.commit()
        cursor.close()

    def update_details(self, product_name=None, description=None, hook=None, type=None, price=None, order_type=None):
        """Update product details."""
        Product.update(
            product_id=self.product_id,
            product_name=product_name,
            description=description,
            hook=hook,
            type=type,
            price=price,
            order_type=order_type
        )
        
    def goal_to_time(self, release_date):
        try:
            query = """
                UPDATE products
                SET 
                    order_type = 1,
                    release_date = %s
                WHERE product_id = %s;
            """
            
            cursor = mysql.connection.cursor()
            cursor.execute(query, (release_date, self.product_id))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Something went wrong with transitioning from goal to time:\n{e}")



    @staticmethod
    def add_product_pictures(product_id, picture_url):
        """Add sizes to the product."""
        query = """
        INSERT INTO pictures (picture_id, picture_url)
        VALUES (%s, %s)
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query, (product_id, picture_url))
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def fetch_product_pictures(product_id):
        """Fetch pictures for the product."""
        cursor = mysql.connection.cursor()
        
        query_fetch = "SELECT picture_url FROM pictures WHERE picture_id = %s"
        cursor.execute(query_fetch, (product_id,))
        fetched_pictures = {row[0] for row in cursor.fetchall()}
        mysql.connection.commit()
        cursor.close()
        
        return fetched_pictures
    
    @staticmethod
    def delete_product_pictures(product_url):
        """Delete pictures of the product."""
        cursor = mysql.connection.cursor()

        query_fetch = "DELETE FROM pictures WHERE picture_url = %s;"
        cursor.execute(query_fetch, (product_url,))
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def update_pictures(self, picture_urls):
        """Update pictures for the product."""
        cursor = mysql.connection.cursor()

        # Fetch existing pictures for the product
        query_fetch = "SELECT picture_url FROM pictures WHERE picture_id = %s"
        cursor.execute(query_fetch, (self.product_id,))
        existing_pictures = {row[0] for row in cursor.fetchall()}

        # Add new pictures or ignore duplicates
        for picture_url in picture_urls:
            if picture_url not in existing_pictures:
                query_insert = """
                INSERT INTO pictures (picture_id, picture_url)
                VALUES (%s, %s)
                """
                cursor.execute(query_insert, (self.product_id, picture_url))

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
    def get_by_id(product_id):
        """Retrieve a product by its name."""
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT product_id, product_name, description, hook, type, price, order_type, seller_id
            FROM products
            WHERE product_id = %s
        """, (product_id,))  # Note the comma to make it a tuple
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            # Unpack and return a User object
            return Product(
                product_id = result[0],
                product_name = result[1],
                description = result[2],
                hook = result[3],
                type = result[4],
                price = result[5],
                order_type = result[6],
                seller_id = result[7]
            )
        return None  # If no match, return None

    from datetime import datetime

    # @staticmethod
    # def update(product_id, product_name=None, description=None, hook=None, type=None, price=None, order_type=None):
    #     """Update product details."""
    #     try:
    #         query = """
    #         UPDATE products
    #         SET 
    #             product_name = COALESCE(%s, product_name),
    #             description = COALESCE(%s, description),
    #             hook = COALESCE(%s, hook),
    #             type = COALESCE(%s, type),
    #             price = COALESCE(%s, price),
    #             order_type = COALESCE(%s, order_type),
    #             updated_at = %s
    #         WHERE product_id = %s
    #         """
    #         cursor = mysql.connection.cursor()
    #         cursor.execute(query, (product_name, description, hook, type, price, order_type, datetime.now(), product_id))
    #         mysql.connection.commit()
    #         cursor.close()
    #         print("Product updated successfully!")
    #     except AttributeError as e:
    #         print(f"AttributeError: {str(e)}")
    #     except Exception as e:
    #         print(f"Error updating product: {str(e)}")


    @staticmethod
    def delete(product_id):
        """Delete a product by its ID."""
        query = "DELETE FROM products WHERE product_id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (product_id,))
        mysql.connection.commit()
        cursor.close()
        
    @staticmethod
    def countProducts(org_id):
        try:
            cursor = mysql.connection.cursor()
            query = """
            SELECT COUNT(*) AS row_count
            FROM products p
            LEFT JOIN user u ON p.seller_id = u.user_id
            WHERE u.org_id = %s;
            """
            cursor.execute(query, (org_id,))
            
            row_count = cursor.fetchone()[0]
            return row_count
        except Exception as e:
            return f"Order Count ERR: {e}"
        
    @staticmethod
    def getOrders(org_id):
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

            # Execute the query
            cursor.execute(query, (org_id,))

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
                    'Type': row[6],
                    'Status': row[7],
                    'Order Date': row[8],
                    'Proof of Payment': row[9]
                }
                orders.append(order)

            # Close the cursor and connection
            cursor.close()

            return orders  # Return the orders list

        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        
    @staticmethod
    def getOrdersInPage(org_id, page):
        try:
            # Create a connection object
            cursor = mysql.connection.cursor()
            
            offset = 10 * (page - 1)
            print(f"Offset: {offset}")

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

            # Execute the query
            cursor.execute(query, (org_id, offset))

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
                    'Type': row[6],
                    'Status': row[7],
                    'Order Date': row[8],
                    'Proof of Payment': row[9]
                }
                orders.append(order)

            # Close the cursor and connection
            cursor.close()

            return orders  # Return the orders list

        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        
    @staticmethod
    def countOrdersWithEmail(email):
        try:
            # Create a connection object
            cursor = mysql.connection.cursor()

            # Define the SQL query
            query = """
            SELECT COUNT(*) as row_count
            FROM ordered_by ob
            JOIN user u ON ob.user_id = u.user_id
            JOIN products p ON ob.product_id = p.product_id
            JOIN sizes s ON ob.size_id = s.size_id
            WHERE user_email = %s;
            """

            # Execute the query
            cursor.execute(query, (email,))

            # Fetch all results
            count = cursor.fetchone()[0]

            # Close the cursor and connection
            cursor.close()

            return count  # Return the count of orders
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        
    @staticmethod
    def getOrdersWithEmail(email):
        try:
            # Create a connection object
            cursor = mysql.connection.cursor()

            # Define the SQL query
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

            # Execute the query
            cursor.execute(query, (email,))

            # Fetch all results
            result = cursor.fetchall()

            # Process the results into a list of dictionaries
            orders = []
            for row in result:
                order = {
                    'Order': row[0],
                    'Product': row[1],
                    'Size': row[2],
                    'Quantity': row[3],
                    'Total Cost': row[4],
                    'Type': row[5],
                    'Status': row[6],
                    'Order Date': row[7],
                    'Product ID': row[8],
                    'Proof of Payment': row[9],
                }
                orders.append(order)
            print(orders)
            # Close the cursor and connection
            cursor.close()

            return orders  # Return the orders list
    
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

    @staticmethod
    def getProducts(org_id):
        try:

            print(f"org_id passed: {org_id}")
            cursor = mysql.connection.cursor()

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
            print(f"Executing query: {query} with org_id: {org_id}")
            cursor.execute(query, (org_id,))
            result = cursor.fetchall()
            print(f"Query result: {result}")
            if not result:
                return []
            products = []
            for row in result:
                product = {
                    'Product_id': row[0],
                    'Product_Name': row[1],
                    'Type': row[2],
                    'Price': row[3],
                    'Order-Type': row[4],
                    'Created At': row[5],
                    'Updated At': row[6],
                }
                products.append(product)
            cursor.close()
            return products  

        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        
    @staticmethod
    def countOrders(org_id):
        try:
            cursor = mysql.connection.cursor()

            query = """
            SELECT COUNT(*) AS row_count
            FROM ordered_by ob
            JOIN user u ON ob.user_id = u.user_id
            JOIN products p ON ob.product_id = p.product_id
            JOIN sizes s ON ob.size_id = s.size_id
            JOIN user seller ON p.seller_id = seller.user_id
            WHERE seller.org_id = %s;
            """
            print(f"Executing query: {query} with org_id: {org_id}")
            cursor.execute(query, (org_id,))
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Products Count ERR: {e}")
        
    @staticmethod
    def get_product_pictures(product_id):
        """Get all picture URLs for a given product ID."""
        query = "SELECT picture_url FROM pictures WHERE picture_id = %s"
        cursor = mysql.connection.cursor()  # Get the database cursor
        
        try:
            # Execute the query with the product ID
            cursor.execute(query, (product_id,))
            
            # Fetch all the results
            results = cursor.fetchall()
            
            # Extract picture URLs from the results
            picture_urls = [row[0] for row in results]  # Assuming fetchall() returns a list of tuples
            
            return picture_urls
        except Exception as e:
            print(f"Error fetching product pictures: {e}")
            return []
        finally:
            # Ensure the cursor is closed after the operation
            cursor.close()

    @staticmethod
    def get_product_sizes(product_id):
        """Get all size IDs for a given product ID."""
        query = "SELECT size_id FROM product_sizes WHERE product_id = %s"
        cursor = mysql.connection.cursor()  # Get the database cursor
        
        try:
            # Execute the query with the product ID
            cursor.execute(query, (product_id,))
            
            # Fetch all the results
            results = cursor.fetchall()
            
            # Extract size IDs from the results
            sizes = [row[0] for row in results]  # Assuming fetchall() returns a list of tuples
            
            return sizes
        except Exception as e:
            print(f"Error fetching sizes: {e}")
            return []
        finally:
            # Ensure the cursor is closed after the operation
            cursor.close()