from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterable
import re

import pyodbc

from config.settings import build_connection_string


@contextmanager
def get_connection(database_override=None):
    connection = pyodbc.connect(
        build_connection_string(database_override=database_override),
        autocommit=False,
    )
    try:
        yield connection
    finally:
        connection.close()


def execute_sql_file(connection, sql_file: Path) -> None:
    sql = sql_file.read_text(encoding="utf-8")

    # Supports scripts pasted from SSMS without sending GO to pyodbc.
    batches = re.split(
        r"^\s*GO\s*;?\s*$",
        sql,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    cursor = connection.cursor()
    try:
        for batch in batches:
            batch = batch.strip()
            if batch:
                cursor.execute(batch)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def fetch_scalar(connection, sql: str, params: Iterable | None = None):
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params or [])
        row = cursor.fetchone()
        return None if row is None else row[0]
    finally:
        cursor.close()
