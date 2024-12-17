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
    

  @staticmethod
  def deletePreorder(orderId):
    cursor = mysql.connection.cursor()
    cursor.execute(
      """
        DELETE FROM ordered_by
        WHERE order_id = %s
      """,
      (orderId,)
    )
    mysql.connection.commit()
    cursor.close()
