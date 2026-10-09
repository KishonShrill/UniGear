from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from MySQLdb.cursors import Cursor

from app import mysql


@contextmanager
def get_db_cursor(
    cursorclass: type[Cursor] | None = None, commit: bool = False
) -> Generator[Any, None, None]:
    """Context manager for acquiring and safely releasing MySQL database cursors.

    Args:
        cursorclass: Optional cursor class (e.g. DictCursor). If None, standard tuple cursor is used.
        commit: If True, commits the transaction on successful exit, and rolls back on exception.

    Yields:
        A database cursor object.
    """
    conn = mysql.connection
    cursor = conn.cursor(cursorclass) if cursorclass else conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        if commit:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        cursor.close()
