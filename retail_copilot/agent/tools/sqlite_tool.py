import sqlite3
from typing import Any, Dict, List, Tuple


class SQLiteTool:
    """
    Lightweight helper for interacting with the local Northwind SQLite database.

    - Opens a single connection (kept open during agent runtime)
    - Provides safe SQL execution with error handling
    - Exposes schema information through PRAGMA queries
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # return dict-like rows

    def execute(self, sql: str) -> Tuple[List[str], List[Dict[str, Any]], str]:
        """
        Execute a SQL query and return:
            - column names
            - list of rows (as dicts)
            - error message ('' if OK)

        We don't raise errors—LangGraph's repair loop will handle failures.
        """
        try:
            cursor = self.conn.execute(sql)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = [dict(row) for row in cursor.fetchall()]
            return columns, rows, ""
        except Exception as exc:
            return [], [], str(exc)

    def get_schema(self) -> Dict[str, List[str]]:
        """
        Return a simple schema dictionary:
            { table_name: [column1, column2, ...], ... }
        """
        schema = {}
        tables = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        for t in tables:
            table_name = t[0]
            cols = self.conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            schema[table_name] = [c[1] for c in cols]

        return schema

    def close(self):
        """Close the database connection."""
        self.conn.close()
