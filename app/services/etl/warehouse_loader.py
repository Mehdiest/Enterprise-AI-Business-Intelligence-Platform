"""Asynchronous warehouse batch loader."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import (
    DimChannel,
    DimCustomer,
    DimDate,
    DimProduct,
    DimRegion,
    FactSales,
)

logger = logging.getLogger(__name__)


class WarehouseLoader:
    """Load warehouse dimensions and facts in batches."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def load_dataframe(self, dataframe: Any) -> int:
        """Load transformed rows into warehouse tables."""
        if dataframe.empty:
            return 0

        rows = dataframe.to_dict(orient="records")
        try:
            dimension_ids = await self._load_dimensions(rows)
            fact_mappings = self._fact_mappings(rows, dimension_ids)
            await self._insert_mappings(FactSales, fact_mappings)
            await self.db.commit()
            return len(fact_mappings)
        except Exception:
            await self.db.rollback()
            logger.exception("Warehouse batch load failed | rows=%s", len(rows))
            raise

    async def _load_dimensions(self, rows: list[dict]) -> dict[str, dict]:
        return {
            "customers": await self._dimension_map(
                DimCustomer, "customer_code", self._customer_mappings(rows)
            ),
            "products": await self._dimension_map(
                DimProduct, "product_code", self._product_mappings(rows)
            ),
            "regions": await self._dimension_map(
                DimRegion, "region_name", self._region_mappings(rows)
            ),
            "channels": await self._dimension_map(
                DimChannel, "channel_name", self._channel_mappings(rows)
            ),
            "dates": await self._dimension_map(
                DimDate, "full_date", self._date_mappings(rows)
            ),
        }

    async def _dimension_map(
        self, model: Any, key: str, mappings: Iterable[dict]
    ) -> dict:
        unique_mappings = {mapping[key]: mapping for mapping in mappings}
        if not unique_mappings:
            return {}

        column = getattr(model, key)
        values = list(unique_mappings)
        database_ids = await self._existing_ids(model, column, key, values)
        missing_mappings = [
            mapping
            for value, mapping in unique_mappings.items()
            if value not in database_ids
        ]
        if missing_mappings:
            await self._insert_mappings(model, missing_mappings)
            database_ids.update(
                await self._existing_ids(
                    model, column, key, [mapping[key] for mapping in missing_mappings]
                )
            )
        return database_ids

    async def _existing_ids(
        self, model: Any, column: Any, key: str, values: list
    ) -> dict:
        query_result = await self.db.execute(select(model).where(column.in_(values)))
        records = query_result.scalars().all()
        return {getattr(record, key): record.id for record in records}

    async def _insert_mappings(self, model: Any, mappings: list[dict]) -> None:
        await self.db.run_sync(
            lambda session: session.bulk_insert_mappings(model, mappings)
        )

    @staticmethod
    def _customer_mappings(rows: list[dict]) -> Iterable[dict]:
        return (
            {
                "customer_code": str(row["customer_code"]),
                "customer_name": str(row["customer_name"]),
            }
            for row in rows
        )

    @staticmethod
    def _product_mappings(rows: list[dict]) -> Iterable[dict]:
        return (
            {
                "product_code": str(row["product_code"]),
                "product_name": str(row["product_name"]),
            }
            for row in rows
        )

    @staticmethod
    def _region_mappings(rows: list[dict]) -> Iterable[dict]:
        return ({"region_name": str(row["region"])} for row in rows)

    @staticmethod
    def _channel_mappings(rows: list[dict]) -> Iterable[dict]:
        return ({"channel_name": str(row["channel"])} for row in rows)

    @classmethod
    def _date_mappings(cls, rows: list[dict]) -> Iterable[dict]:
        return ({"full_date": cls._as_date(row["sale_date"])} for row in rows)

    @classmethod
    def _fact_mappings(
        cls, rows: list[dict], dimension_ids: dict[str, dict]
    ) -> list[dict]:
        return [cls._fact_mapping(row, dimension_ids) for row in rows]

    @classmethod
    def _fact_mapping(cls, row: dict, dimension_ids: dict[str, dict]) -> dict:
        return {
            "customer_id": dimension_ids["customers"][str(row["customer_code"])],
            "product_id": dimension_ids["products"][str(row["product_code"])],
            "region_id": dimension_ids["regions"][str(row["region"])],
            "channel_id": dimension_ids["channels"][str(row["channel"])],
            "date_id": dimension_ids["dates"][cls._as_date(row["sale_date"])],
            "quantity": int(row["quantity"]),
            "amount": float(row["amount"]),
        }

    @staticmethod
    def _as_date(value: Any) -> date:
        return value.date() if hasattr(value, "date") else value
