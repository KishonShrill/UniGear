import unittest
from unittest.mock import MagicMock, patch
from MySQLdb.cursors import DictCursor
from app.utils.db import get_db_cursor


class TestDbContextManager(unittest.TestCase):
    @patch("app.utils.db.mysql")
    def test_cursor_closes_on_success(self, mock_mysql):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_mysql.connection = mock_conn

        with get_db_cursor() as cursor:
            self.assertEqual(cursor, mock_cursor)
            cursor.execute("SELECT 1")

        mock_conn.cursor.assert_called_once_with()
        mock_cursor.execute.assert_called_once_with("SELECT 1")
        mock_cursor.close.assert_called_once()
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_not_called()

    @patch("app.utils.db.mysql")
    def test_cursor_commits_on_clean_exit_when_commit_true(self, mock_mysql):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_mysql.connection = mock_conn

        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE products SET price = 100")

        mock_cursor.close.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    @patch("app.utils.db.mysql")
    def test_cursor_rolls_back_and_closes_on_exception(self, mock_mysql):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_mysql.connection = mock_conn

        with self.assertRaises(RuntimeError):
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO user ...")
                raise RuntimeError("Simulated database error")

        mock_cursor.close.assert_called_once()
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()

    @patch("app.utils.db.mysql")
    def test_cursorclass_passed_correctly(self, mock_mysql):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_mysql.connection = mock_conn

        with get_db_cursor(cursorclass=DictCursor) as cursor:
            cursor.execute("SELECT * FROM products")

        mock_conn.cursor.assert_called_once_with(DictCursor)
        mock_cursor.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
