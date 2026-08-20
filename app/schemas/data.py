"""
Data schemas used by ingestion and ETL pipelines.

These schemas validate incoming metadata and API responses
before data is transformed and loaded into the warehouse.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SalesRecord(BaseModel):
    """
    Canonical sales record used across ETL pipelines.
    """

    customer_code: str = Field(..., min_length=1, max_length=100)
    customer_name: str = Field(..., min_length=1, max_length=255)

    product_code: str = Field(..., min_length=1, max_length=100)
    product_name: str = Field(..., min_length=1, max_length=255)

    region: str = Field(..., min_length=1, max_length=255)
    channel: str = Field(..., min_length=1, max_length=255)

    sale_date: datetime

    quantity: int = Field(..., gt=0)

    amount: Decimal = Field(..., gt=0)

    model_config = ConfigDict(from_attributes=True)


class IngestionResponse(BaseModel):
    """
    Standard response returned by ingestion endpoints.
    """

    success: bool
    rows_received: int
    rows_loaded: int
    message: str


class FileUploadResponse(BaseModel):
    """
    Upload metadata returned after processing a file.
    """

    filename: str
    rows_detected: int
    processed_at: datetime


class ETLHealthResponse(BaseModel):
    """
    Health check response for ETL services.
    """

    status: str
    timestamp: datetime
    version: str | None = None