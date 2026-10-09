import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

#from MySQLdb.cursors import Cursor
#from app import mysql
#
import psycopg
from psycopg.rows import dict_row
from config import get_config


#
#
#
#@contextmanager
#def get_db_cursor(
#    cursorclass: type[Cursor] | None = None, commit: bool = False
#) -> Generator[Any, None, None]:
#    """Context manager for acquiring and safely releasing MySQL database cursors.
#
#    Args:
#        cursorclass: Optional cursor class (e.g. DictCursor). If None, standard tuple cursor is used.
#        commit: If True, commits the transaction on successful exit, and rolls back on exception.
#
#    Yields:
#        A database cursor object.
#    """
#    conn = mysql.connection
#    cursor = conn.cursor(cursorclass) if cursorclass else conn.cursor()
#    try:
#        yield cursor
#        if commit:
#            conn.commit()
#    except Exception:
#        if commit:
#            try:
#                conn.rollback()
#            except Exception:
#                pass
#        raise
#    finally:
#        cursor.close()


@contextmanager
def get_db_cursor(
    cursorclass: Any = None,
    commit: bool = False,
) -> Generator[Any, None, None]:
    """Acquire and safely release a PostgreSQL database cursor."""

    config_class = get_config()
    database_url = config_class.DATABASE_URL
    print(database_url)

    conn = psycopg.connect(
        database_url,
        sslmode="require",
    )

    cursor = None

    try:
        cursor = conn.cursor(row_factory=cursorclass)
        yield cursor

        if commit:
            conn.commit()

    except Exception:
        if commit:
            conn.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()
