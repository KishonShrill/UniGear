from app import mysql

class Order(object):
  
  @staticmethod
  def preorderProduct(userID, productID, size, quantity, price):
    try:
      cursor = mysql.connection.cursor()
      cursor.execute(
        """
          UPDATE product_sizes
          SET product_quantity = product_quantity + %s 
          WHERE product_id = %s and size_id = %s
        """,
        (quantity, productID, size)
      )
      cursor.execute(
        """
          INSERT INTO ordered_by (user_id, product_id, size_id, quantity, total_cost, order_status) VALUES 
          (%s, %s, %s, %s, %s, 0);
        """,
        (userID, productID, size, quantity, price)
      )
      mysql.connection.commit()
      order_id = cursor.lastrowid
      cursor.close()
      return order_id
    except Exception as e:
      return None
    

  def toggle_status(order_id):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
               """
               SELECT order_status 
               FROM ordered_by 
               WHERE order_id = %s
               """,
                (order_id,))
            current_status = cursor.fetchone()

            if not current_status:
                cursor.close()
                return False, None  # If the order doesn't exist, return False

            current_status = current_status[0]

            # Toggle status: If it's 1 (paid), set it to 0 (unpaid), and vice versa
            new_status = 0 if current_status == 1 else 1

            cursor.execute(
                """
                UPDATE ordered_by 
                SET order_status = %s 
                WHERE order_id = %s
                """, (new_status, order_id)
            )

            # Commit the transaction
            mysql.connection.commit()
            cursor.close()

            return True, new_status  # Return success and the new status

        except Exception as e:
            print(f"Error: {e}")
            return False, None  # Return failure if any exception occurs