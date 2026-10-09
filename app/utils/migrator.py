"""Database migration utility for managing versioned SQL schema migrations."""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import MySQLdb
from MySQLdb.cursors import DictCursor

from config import get_config

logger = logging.getLogger(__name__)

DEFAULT_MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "migrations"


@dataclass
class Migration:
    """Represents a migration file."""

    version: str
    name: str
    filepath: Path


class DatabaseMigrator:
    """Handles discovery, tracking, and execution of raw SQL schema migrations."""

    def __init__(
        self,
        db_config: dict[str, Any] | None = None,
        migrations_dir: Path | str | None = None,
    ):
        if db_config is None:
            active_config = get_config()
            self.db_config = {
                "host": getattr(active_config, "MYSQL_HOST", "localhost"),
                "user": getattr(active_config, "MYSQL_USER", "root"),
                "passwd": getattr(active_config, "MYSQL_PASSWORD", ""),
                "db": getattr(active_config, "MYSQL_DB", "college_marketplace"),
                "unix_socket": getattr(active_config, "MYSQL_UNIX_SOCKET", None),
            }
            # Remove None values
            self.db_config = {k: v for k, v in self.db_config.items() if v is not None}
        else:
            self.db_config = db_config

        self.migrations_dir = Path(migrations_dir or DEFAULT_MIGRATIONS_DIR)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> MySQLdb.Connection:
        """Create a direct MySQLdb connection from config."""
        return MySQLdb.connect(**self.db_config)

    def ensure_migrations_table(self, cursor: Any) -> None:
        """Ensure the schema_migrations tracking table exists."""
        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(query)

    def get_applied_migrations(self, cursor: Any) -> dict[str, dict[str, Any]]:
        """Retrieve all previously applied migrations from schema_migrations."""
        self.ensure_migrations_table(cursor)
        query = "SELECT version, name, applied_at FROM schema_migrations ORDER BY version ASC;"
        cursor.execute(query)
        rows = cursor.fetchall()
        applied = {}
        for row in rows:
            if isinstance(row, dict):
                version = str(row["version"])
                applied[version] = {
                    "name": row["name"],
                    "applied_at": row["applied_at"],
                }
            else:
                version = str(row[0])
                applied[version] = {
                    "name": row[1],
                    "applied_at": row[2],
                }
        return applied

    def get_available_migrations(self) -> list[Migration]:
        """Discover and sort all .sql migration files in the migrations directory."""
        if not self.migrations_dir.exists():
            return []

        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        migrations = []
        for file in migration_files:
            filename = file.stem
            # Pattern: 001_initial_schema or 20261009120000_name
            parts = filename.split("_", 1)
            version = parts[0]
            name = parts[1] if len(parts) > 1 else filename
            migrations.append(Migration(version=version, name=name, filepath=file))

        return migrations

    def get_pending_migrations(self, cursor: Any | None = None) -> list[Migration]:
        """Return list of available migrations that have not yet been applied."""
        if cursor is not None:
            applied = self.get_applied_migrations(cursor)
        else:
            conn = self.get_connection()
            try:
                with conn.cursor() as cur:
                    applied = self.get_applied_migrations(cur)
            finally:
                conn.close()

        available = self.get_available_migrations()
        return [m for m in available if m.version not in applied]

    @staticmethod
    def parse_sql_statements(sql_content: str) -> list[str]:
        """Split raw SQL file content into individual executable statements.

        Strips single-line and multi-line comments while preserving statement integrity.
        """
        # Remove multi-line comments /* ... */
        cleaned = re.sub(r"/\*.*?\*/", "", sql_content, flags=re.DOTALL)

        # Remove single-line comments (-- or #)
        lines = []
        for line in cleaned.splitlines():
            stripped = line.strip()
            if stripped.startswith("--") or stripped.startswith("#"):
                continue
            # Remove trailing -- comments if not inside quotes
            line_no_comment = re.sub(r"--.*$", "", line)
            lines.append(line_no_comment)

        cleaned_sql = "\n".join(lines)

        # Split by semicolon
        raw_statements = cleaned_sql.split(";")
        statements = []
        for stmt in raw_statements:
            trimmed = stmt.strip()
            if trimmed:
                statements.append(trimmed)

        return statements

    def apply_migration(self, migration: Migration, conn: Any | None = None) -> None:
        """Execute a single migration file within a database transaction."""
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True

        try:
            sql_content = migration.filepath.read_text(encoding="utf-8")
            statements = self.parse_sql_statements(sql_content)

            with conn.cursor() as cursor:
                self.ensure_migrations_table(cursor)

                for stmt in statements:
                    cursor.execute(stmt)

                # Record migration record
                record_query = """
                INSERT INTO schema_migrations (version, name, applied_at)
                VALUES (%s, %s, %s);
                """
                cursor.execute(record_query, (migration.version, migration.name, datetime.now()))

            conn.commit()
            logger.info("Successfully applied migration %s (%s)", migration.version, migration.name)
        except Exception as e:
            conn.rollback()
            logger.error(
                "Failed to apply migration %s (%s): %s", migration.version, migration.name, e
            )
            raise
        finally:
            if should_close:
                conn.close()

    def migrate(self) -> list[str]:
        """Apply all pending migrations in sequential order.

        Returns:
            list[str]: Versions of newly applied migrations.
        """
        conn = self.get_connection()
        applied_versions = []
        try:
            with conn.cursor() as cursor:
                pending = self.get_pending_migrations(cursor)

            for migration in pending:
                self.apply_migration(migration, conn=conn)
                applied_versions.append(migration.version)

            return applied_versions
        finally:
            conn.close()

    def status(self) -> list[dict[str, Any]]:
        """Retrieve full status of all available migrations."""
        conn = self.get_connection()
        try:
            with conn.cursor(DictCursor) as cursor:
                applied = self.get_applied_migrations(cursor)

            available = self.get_available_migrations()
            result = []

            for m in available:
                is_applied = m.version in applied
                applied_info = applied.get(m.version, {})
                result.append(
                    {
                        "version": m.version,
                        "name": m.name,
                        "applied": is_applied,
                        "applied_at": applied_info.get("applied_at"),
                        "filepath": str(m.filepath),
                    }
                )

            return result
        finally:
            conn.close()

    def create_migration(self, name: str) -> Path:
        """Create a new migration file template in the migrations directory.

        Args:
            name: Human-readable name for the migration (e.g. 'add_discount_to_products').

        Returns:
            Path to the created migration file.
        """
        # Normalize name
        slug = re.sub(r"[^\w\-_]", "_", name).strip("_").lower()

        # Find next sequential number
        available = self.get_available_migrations()
        numeric_versions = []
        for m in available:
            if m.version.isdigit():
                numeric_versions.append(int(m.version))

        next_num = max(numeric_versions, default=0) + 1
        version_str = f"{next_num:03d}"

        filename = f"{version_str}_{slug}.sql"
        file_path = self.migrations_dir / filename

        template = f"""-- Migration: {version_str}_{slug}
-- Created at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

-- Write your schema changes (DDL / DML) below:

"""
        file_path.write_text(template, encoding="utf-8")
        logger.info("Created new migration file: %s", file_path)
        return file_path
