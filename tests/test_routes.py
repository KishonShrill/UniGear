import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from config import TestingConfig


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

    def test_landing_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    @patch("app.models.product.Product.get_explore_catalog")
    def test_explore_page(self, mock_get_explore):
        mock_get_explore.return_value = [
            (1, "CCS Hoodie", "College of Computer Studies", "https://img.com/ccs.jpg")
        ]
        response = self.client.get("/explore")
        self.assertEqual(response.status_code, 200)

    @patch("app.models.organization.Organization.get_by_college_code")
    def test_get_organizations_api(self, mock_get_orgs):
        mock_get_orgs.return_value = [{"id": "SITE", "name": "SITE Organization"}]
        response = self.client.get("/api/ccs/organizations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"id": "SITE", "name": "SITE Organization"}])

    def test_get_organizations_invalid_college_api(self):
        response = self.client.get("/api/invalid_college/organizations")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    @patch("app.models.product.Product.get_by_organization")
    def test_get_organization_products_api(self, mock_get_products):
        mock_get_products.return_value = [
            {"id": 1, "name": "Shirt", "description": "Desc", "picture": "pic.jpg"}
        ]
        response = self.client.get("/api/organizations/products?org_id=SITE&type=all")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_protected_user_routes_require_login(self):
        # Accessing protected user route without session should redirect to login / return 401
        response = self.client.get("/user/my-orders")
        self.assertEqual(response.status_code, 401)

    def test_protected_seller_routes_require_seller_role(self):
        # Accessing protected seller route without session should return 401
        response = self.client.get("/seller/my-products")
        self.assertEqual(response.status_code, 401)

    @patch("app.models.favorite.Favorite.toggle")
    def test_toggle_favorite_api_logged_in(self, mock_toggle):
        mock_toggle.return_value = (True, True)
        with self.client.session_transaction() as sess:
            sess["id"] = 1
            sess["email"] = "user@example.com"
            sess["role"] = "user"

        response = self.client.post("/favorite/submit", json={"product_id": 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"success": True, "favorite_status": True})

    @patch("app.models.order.Order.toggle_status")
    def test_seller_toggle_order_status(self, mock_toggle_status):
        mock_toggle_status.return_value = (True, 1)
        with self.client.session_transaction() as sess:
            sess["id"] = 1
            sess["email"] = "seller@example.com"
            sess["role"] = "seller"
            sess["org_id"] = "SITE"

        response = self.client.post("/toggle_order_status", json={"order_id": 10})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"success": True, "new_status": 1})


if __name__ == "__main__":
    unittest.main()
