import unittest
from unittest.mock import MagicMock, patch

from app.models.favorite import Favorite
from app.models.order import Order
from app.models.organization import Organization
from app.models.product import Product
from app.models.user import User


class TestUserModel(unittest.TestCase):
    @patch("app.models.user.get_db_cursor")
    def test_user_save_insert(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 42
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        user = User(
            user_name="testuser",
            user_email="test@example.com",
            user_password="hashedpassword",
            user_contact="09123456789",
            user_address="Street, Barangay, City",
            user_role="user",
            org_id=None,
        )
        user.save()

        self.assertEqual(user.user_id, 42)
        mock_get_cursor.assert_called_once_with(commit=True)
        self.assertTrue(mock_cursor.execute.called)

    @patch("app.models.user.get_db_cursor")
    def test_user_save_update(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        user = User(
            user_id=1,
            user_name="updateduser",
            user_email="updated@example.com",
            user_password="newhash",
            user_contact="09999999999",
            user_address="New Address",
            user_role="seller",
            org_id="ORG123",
        )
        user.save()

        mock_get_cursor.assert_called_once_with(commit=True)
        self.assertTrue(mock_cursor.execute.called)

    @patch("app.models.user.get_db_cursor")
    def test_get_by_email(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            1,
            "john_doe",
            "john@example.com",
            "pbkdf2:sha256:...",
            "09123456789",
            "Address",
            "user",
            None,
        )
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        user = User.get_by_email("john@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.user_name, "john_doe")
        self.assertEqual(user.user_email, "john@example.com")
        self.assertEqual(user.user_role, "user")

    @patch("app.models.user.get_db_cursor")
    def test_create_from_website(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 10
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        user = User.create_from_website(
            name="Alice",
            email="alice@example.com",
            password="securepassword",
            contact="09111111111",
            address="Campus Dorm",
        )
        self.assertEqual(user.user_id, 10)
        self.assertEqual(user.user_name, "Alice")
        self.assertEqual(user.user_role, "user")


class TestOrderModel(unittest.TestCase):
    @patch("app.models.order.get_db_cursor")
    def test_preorder_product_atomic(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 101
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        order_id = Order.preorderProduct(user_id=1, product_id=5, size=2, quantity=3, price=450.00)
        self.assertEqual(order_id, 101)
        mock_get_cursor.assert_called_once_with(commit=True)
        self.assertEqual(mock_cursor.execute.call_count, 2)

    @patch("app.models.order.get_db_cursor")
    def test_toggle_status(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)  # current unpaid
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        success, new_status = Order.toggle_status(order_id=101)
        self.assertTrue(success)
        self.assertEqual(new_status, 1)

    @patch("app.models.order.get_db_cursor")
    def test_delete_unpaid_order(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)  # unpaid
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = Order.deleteOrder(order_id=101)
        self.assertTrue(result)
        self.assertEqual(mock_cursor.execute.call_count, 2)

    @patch("app.models.order.get_db_cursor")
    def test_delete_paid_order_blocked(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)  # paid
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = Order.deleteOrder(order_id=101)
        self.assertFalse(result)
        self.assertEqual(mock_cursor.execute.call_count, 1)

    @patch("app.models.order.get_db_cursor")
    def test_save_proof_of_payment(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = Order.save_proof_of_payment(101, "https://cloudinary.com/receipt.jpg")
        self.assertTrue(result)
        mock_get_cursor.assert_called_once_with(commit=True)


class TestProductModel(unittest.TestCase):
    @patch("app.models.product.get_db_cursor")
    def test_product_save(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 7
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        p = Product(
            product_name="College Lanyard",
            description="Official college lanyard with metal hook",
            hook="Best lanyard",
            type="lanyard",
            price=150.00,
            order_type=0,
            seller_id=1,
            release_date=None,
        )
        p.save()
        self.assertEqual(p.product_id, 7)
        mock_get_cursor.assert_called_once_with(commit=True)

    @patch("app.models.product.get_db_cursor")
    def test_count_preorder(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(25,), (50,)]
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        p = Product(product_id=7)
        count, goal = p.countPreorder()
        self.assertEqual(count, 25)
        self.assertEqual(goal, 50)

    @patch("app.models.product.get_db_cursor")
    def test_get_details_by_id(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            (
                7,
                "College Shirt",
                "Description",
                "Hook",
                "shirt",
                350.00,
                1,
                "2026-12-01",
            ),  # product
            (100,),  # sum of quantities
        ]
        mock_cursor.fetchall.side_effect = [
            [("https://img.com/pic1.jpg",), ("https://img.com/pic2.jpg",)],  # images
            [(1, 20), (2, 40), (3, 40)],  # sizes
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        details = Product.get_details_by_id(7)
        self.assertIsNotNone(details)
        self.assertEqual(details["product"]["name"], "College Shirt")
        self.assertEqual(len(details["images"]), 2)
        self.assertEqual(len(details["sizes"]), 3)
        self.assertEqual(details["total_quantity"], 100)


class TestOrganizationModel(unittest.TestCase):
    @patch("app.models.organization.get_db_cursor")
    def test_get_by_college_code(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("CCS_EC", "CCS Executive Council"),
            ("SITE", "Society of Information Technology Enthusiasts"),
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        orgs = Organization.get_by_college_code("ccs")
        self.assertIsNotNone(orgs)
        self.assertEqual(len(orgs), 2)
        self.assertEqual(orgs[0]["name"], "CCS Executive Council")

    def test_invalid_college_code_returns_none(self):
        orgs = Organization.get_by_college_code("invalid_code")
        self.assertIsNone(orgs)


class TestFavoriteModel(unittest.TestCase):
    @patch("app.models.favorite.get_db_cursor")
    def test_is_favorite_true(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = Favorite.is_favorite(user_id=1, product_id=5)
        self.assertTrue(result)

    @patch("app.models.favorite.get_db_cursor")
    def test_toggle_favorite_add(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # Not favorited yet
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        success, is_fav = Favorite.toggle(user_id=1, product_id=5)
        self.assertTrue(success)
        self.assertTrue(is_fav)

    @patch("app.models.favorite.get_db_cursor")
    def test_toggle_favorite_remove(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)  # Already favorited
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        success, is_fav = Favorite.toggle(user_id=1, product_id=5)
        self.assertTrue(success)
        self.assertFalse(is_fav)


if __name__ == "__main__":
    unittest.main()
