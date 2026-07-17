"""
Enterprise SQL Validator.
"""

from __future__ import annotations

import sqlparse


class SQLValidator:
    """
    Validate SQL queries before execution.

    Only read-only SELECT statements are allowed.
    """

    ALLOWED_STATEMENT = "SELECT"

    def validate(self, sql: str) -> None:
        """
        Validate SQL query.

        Raises:
            ValueError: If the SQL is invalid or not read-only.
        """
        statements = sqlparse.parse(sql)

        if not statements:
            raise ValueError("Empty SQL query.")

        if len(statements) != 1:
            raise ValueError("Only one SQL statement is allowed.")

        statement = statements[0]

        statement_type = statement.get_type().upper()

        if statement_type != self.ALLOWED_STATEMENT:
            raise ValueError(
                f"Only SELECT statements are allowed. Found: {statement_type}"
            )