"""CSV ingestion: validate, load, and normalize sales CSV files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class CSVLoaderError(Exception):
    """Raised when CSV ingestion fails."""


class CSVLoader:
    """Load and validate a sales CSV into a normalized DataFrame."""

    REQUIRED_COLUMNS = {
        "customer_code",
        "customer_name",
        "product_code",
        "product_name",
        "region",
        "channel",
        "sale_date",
        "quantity",
        "amount",
    }

    def load(self, file_path: str | Path) -> pd.DataFrame:
        """Load a CSV file into a validated DataFrame.

        Raises:
            CSVLoaderError: If the file is missing, malformed, or incomplete.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise CSVLoaderError(f"CSV file not found: {file_path}")

        if file_path.suffix.lower() != ".csv":
            raise CSVLoaderError("Only CSV files are supported.")

        try:
            frame = pd.read_csv(file_path)
        except (OSError, ValueError, pd.errors.ParserError) as exc:
            raise CSVLoaderError(f"Failed to read CSV file: {exc}") from exc

        if frame.empty:
            raise CSVLoaderError("CSV file contains no rows.")

        frame.columns = [column.strip().lower() for column in frame.columns]
        self._validate_columns(frame)

        return frame

    def _validate_columns(self, frame: pd.DataFrame) -> None:
        """Raise if any required column is missing."""
        missing = self.REQUIRED_COLUMNS - set(frame.columns)

        if missing:
            raise CSVLoaderError(
                "Missing required columns: " + ", ".join(sorted(missing))
            )
