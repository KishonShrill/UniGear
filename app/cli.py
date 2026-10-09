"""CLI commands for UniGear application, including database migrations."""

import click
from flask import Flask
from flask.cli import AppGroup

from app.utils.migrator import DatabaseMigrator

db_cli = AppGroup("db", help="Database schema migration commands.")


@db_cli.command("migrate")
def migrate_command():
    """Apply all pending database migrations."""
    migrator = DatabaseMigrator()
    click.echo("Checking and running pending migrations...")
    try:
        applied = migrator.migrate()
        if applied:
            click.echo(f"Successfully applied {len(applied)} migration(s): {', '.join(applied)}")
        else:
            click.echo("Database schema is already up to date. No pending migrations.")
    except Exception as e:
        click.echo(f"Error executing migrations: {e}", err=True)


@db_cli.command("status")
def status_command():
    """Display the current status of all migrations."""
    migrator = DatabaseMigrator()
    try:
        statuses = migrator.status()
        if not statuses:
            click.echo("No migration files found in migrations directory.")
            return

        click.echo("=" * 75)
        click.echo(f"{'Version':<10} {'Name':<35} {'Status':<12} {'Applied At'}")
        click.echo("=" * 75)
        for s in statuses:
            status_label = "Applied" if s["applied"] else "Pending"
            applied_at = str(s["applied_at"]) if s["applied_at"] else "-"
            click.echo(f"{s['version']:<10} {s['name']:<35} {status_label:<12} {applied_at}")
        click.echo("=" * 75)
    except Exception as e:
        click.echo(f"Error fetching migration status: {e}", err=True)


@db_cli.command("create")
@click.argument("name")
def create_command(name: str):
    """Create a new migration SQL template file."""
    migrator = DatabaseMigrator()
    try:
        file_path = migrator.create_migration(name)
        click.echo(f"Created new migration file: {file_path}")
    except Exception as e:
        click.echo(f"Error creating migration: {e}", err=True)


def register_cli_commands(app: Flask) -> None:
    """Register custom CLI commands with the Flask application."""
    app.cli.add_command(db_cli)
