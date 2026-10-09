"""Unit tests for the DatabaseMigrator and migration CLI commands."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app import create_app
from app.utils.migrator import DatabaseMigrator, Migration
from config import TestingConfig


class TestDatabaseMigrator(unittest.TestCase):
    """Tests for DatabaseMigrator parsing, discovery, execution, and scaffolding."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.migrations_dir = Path(self.temp_dir.name)
        self.migrator = DatabaseMigrator(
            db_config={"host": "localhost", "user": "test", "passwd": "pw", "db": "testdb"},
            migrations_dir=self.migrations_dir,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_sql_statements_single_and_multi(self):
        sql = """
        -- Create table
        CREATE TABLE test (
            id INT PRIMARY KEY,
            name VARCHAR(50)
        );

        /* Multi-line
           comment */
        INSERT INTO test (id, name) VALUES (1, 'Hello');
        """
        statements = DatabaseMigrator.parse_sql_statements(sql)
        self.assertEqual(len(statements), 2)
        self.assertTrue(statements[0].startswith("CREATE TABLE test"))
        self.assertTrue(statements[1].startswith("INSERT INTO test"))

    def test_parse_sql_statements_handles_hash_and_trailing_comments(self):
        sql = """
        # Line comment with hash
        SELECT 1; -- inline comment
        SELECT 2;
        """
        statements = DatabaseMigrator.parse_sql_statements(sql)
        self.assertEqual(len(statements), 2)
        self.assertEqual(statements[0], "SELECT 1")
        self.assertEqual(statements[1], "SELECT 2")

    def test_get_available_migrations_sorting(self):
        # Create dummy migration files
        (self.migrations_dir / "002_add_field.sql").write_text("SELECT 2;", encoding="utf-8")
        (self.migrations_dir / "001_initial.sql").write_text("SELECT 1;", encoding="utf-8")
        (self.migrations_dir / "003_seed_data.sql").write_text("SELECT 3;", encoding="utf-8")

        migrations = self.migrator.get_available_migrations()
        self.assertEqual(len(migrations), 3)
        self.assertEqual([m.version for m in migrations], ["001", "002", "003"])
        self.assertEqual([m.name for m in migrations], ["initial", "add_field", "seed_data"])

    def test_get_pending_migrations(self):
        (self.migrations_dir / "001_init.sql").write_text("SELECT 1;", encoding="utf-8")
        (self.migrations_dir / "002_more.sql").write_text("SELECT 2;", encoding="utf-8")

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"version": "001", "name": "init", "applied_at": "2026-10-09 10:00:00"}
        ]

        pending = self.migrator.get_pending_migrations(cursor=mock_cursor)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].version, "002")

    def test_create_migration_auto_numbering(self):
        (self.migrations_dir / "001_init.sql").write_text("SELECT 1;", encoding="utf-8")
        (self.migrations_dir / "002_add_stuff.sql").write_text("SELECT 2;", encoding="utf-8")

        created_path = self.migrator.create_migration("add new column to users")
        self.assertTrue(created_path.exists())
        self.assertEqual(created_path.name, "003_add_new_column_to_users.sql")

        content = created_path.read_text(encoding="utf-8")
        self.assertIn("-- Migration: 003_add_new_column_to_users", content)

    @patch.object(DatabaseMigrator, "get_connection")
    def test_apply_migration_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        file_path = self.migrations_dir / "001_test.sql"
        file_path.write_text("CREATE TABLE t (id INT); INSERT INTO t VALUES (1);", encoding="utf-8")
        migration = Migration(version="001", name="test", filepath=file_path)

        self.migrator.apply_migration(migration, conn=mock_conn)

        self.assertEqual(mock_cursor.execute.call_count, 4)  # ensure table + 2 stmts + record stmt
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    @patch.object(DatabaseMigrator, "get_connection")
    def test_apply_migration_failure_rolls_back(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = [None, RuntimeError("SQL syntax error")]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        file_path = self.migrations_dir / "001_fail.sql"
        file_path.write_text("BAD SQL STATEMENT;", encoding="utf-8")
        migration = Migration(version="001", name="fail", filepath=file_path)

        with self.assertRaises(RuntimeError):
            self.migrator.apply_migration(migration, conn=mock_conn)

        mock_conn.rollback.assert_called_once()


class TestMigrationCLI(unittest.TestCase):
    """Tests for Flask CLI migration commands."""

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.runner = self.app.test_cli_runner()

    @patch("app.cli.DatabaseMigrator.status")
    def test_cli_db_status_output(self, mock_status):
        mock_status.return_value = [
            {
                "version": "001",
                "name": "core_tables",
                "applied": True,
                "applied_at": "2026-10-09 12:00:00",
                "filepath": "/path/001.sql",
            },
            {
                "version": "002",
                "name": "favorites",
                "applied": False,
                "applied_at": None,
                "filepath": "/path/002.sql",
            },
        ]
        result = self.runner.invoke(args=["db", "status"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("core_tables", result.output)
        self.assertIn("Applied", result.output)
        self.assertIn("favorites", result.output)
        self.assertIn("Pending", result.output)

    @patch("app.cli.DatabaseMigrator.migrate")
    def test_cli_db_migrate(self, mock_migrate):
        mock_migrate.return_value = ["001", "002"]
        result = self.runner.invoke(args=["db", "migrate"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Successfully applied 2 migration(s): 001, 002", result.output)

    @patch("app.cli.DatabaseMigrator.create_migration")
    def test_cli_db_create(self, mock_create):
        mock_create.return_value = Path("/migrations/006_add_coupons.sql")
        result = self.runner.invoke(args=["db", "create", "add_coupons"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Created new migration file: /migrations/006_add_coupons.sql", result.output)


if __name__ == "__main__":
    unittest.main()
