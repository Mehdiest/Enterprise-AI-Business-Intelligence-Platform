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

    FORBIDDEN_KEYWORDS = frozenset(
        {
            "ALTER",
            "ATTACH",
            "CALL",
            "COPY",
            "CREATE",
            "DELETE",
            "DROP",
            "EXEC",
            "EXECUTE",
            "GRANT",
            "INSERT",
            "MERGE",
            "REPLACE",
            "REVOKE",
            "TRUNCATE",
            "UPDATE",
            "VACUUM",
        }
    )

    def validate(self, sql: str) -> None:
        """
        Validate SQL query.

        Raises:
            ValueError: If the SQL is invalid or not read-only.
        """
        statements = [
            statement for statement in sqlparse.parse(sql) if str(statement).strip("; \n\t\r")
        ]

        if not statements:
            raise ValueError("Empty SQL query.")

        if len(statements) != 1:
            raise ValueError("Only one SQL statement is allowed.")

        statement = statements[0]

        statement_type = (statement.get_type() or "UNKNOWN").upper()

        if statement_type != self.ALLOWED_STATEMENT:
            raise ValueError(
                f"Only SELECT statements are allowed. Found: {statement_type}"
            )

        self._reject_write_keywords(statement)

    def _reject_write_keywords(self, statement) -> None:
        """Reject write keywords hidden inside an otherwise valid SELECT."""
        for token in statement.flatten():
            if not token.is_keyword:
                continue

            keyword = token.normalized.upper()

            if keyword in self.FORBIDDEN_KEYWORDS:
                raise ValueError(f"Read-only queries cannot contain: {keyword}")
