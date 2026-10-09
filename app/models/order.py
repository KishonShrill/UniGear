from app.utils.db import get_db_cursor


class Order(object):
    @staticmethod
    def preorderProduct(user_id, product_id, size, quantity, price):
        """Create an order record and increment product reserved size quantities atomically."""
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(
                    """
                    UPDATE product_sizes
                    SET product_quantity = product_quantity + %s
                    WHERE product_id = %s AND size_id = %s
                    """,
                    (quantity, product_id, size),
                )
                cursor.execute(
                    """
                    INSERT INTO ordered_by (user_id, product_id, size_id, quantity, total_cost, order_status)
                    VALUES (%s, %s, %s, %s, %s, 0)
                    """,
                    (user_id, product_id, size, quantity, price),
                )
                return cursor.lastrowid
        except Exception as e:
            print(f"Error in preorderProduct: {e}")
            return None

    @staticmethod
    def toggle_status(order_id):
        """Toggle an order's payment status between 0 (unpaid) and 1 (paid)."""
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(
                    """
                    SELECT order_status
                    FROM ordered_by
                    WHERE order_id = %s
                    """,
                    (order_id,),
                )
                row = cursor.fetchone()

                if not row:
                    return False, None

                current_status = row[0]
                new_status = 0 if current_status == 1 else 1

                cursor.execute(
                    """
                    UPDATE ordered_by
                    SET order_status = %s
                    WHERE order_id = %s
                    """,
                    (new_status, order_id),
                )
                return True, new_status
        except Exception as e:
            print(f"Error in toggle_status: {e}")
            return False, None

    @staticmethod
    def fetchReceipt(order_id):
        """Retrieve the proof of payment URL for a given order."""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT proof_of_payment
                    FROM ordered_by
                    WHERE order_id = %s
                    """,
                    (order_id,),
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Error in fetchReceipt: {e}")
            return None

    @staticmethod
    def deleteOrder(order_id):
        """Delete an order if it has not been marked as paid."""
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(
                    """
                    SELECT order_status
                    FROM ordered_by
                    WHERE order_id = %s
                    """,
                    (order_id,),
                )
                row = cursor.fetchone()

                if not row:
                    return False

                is_paid = row[0]
                if not is_paid:
                    cursor.execute(
                        """
                        DELETE FROM ordered_by
                        WHERE order_id = %s
                        """,
                        (order_id,),
                    )
                    return True
                return False
        except Exception as e:
            print(f"Error in deleteOrder: {e}")
            return False

    @staticmethod
    def deleteReceipt(picture):
        """Clear proof of payment URL from order records."""
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(
                    """
                    UPDATE ordered_by
                    SET proof_of_payment = NULL
                    WHERE proof_of_payment = %s
                    """,
                    (picture,),
                )
                return True
        except Exception as e:
            print(f"Error in deleteReceipt: {e}")
            return False

    @staticmethod
    def save_proof_of_payment(order_id, cloudinary_url):
        """Save uploaded proof of payment URL to the order record."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE ordered_by
                SET proof_of_payment = %s
                WHERE order_id = %s
                """,
                (cloudinary_url, order_id),
            )
            return True
