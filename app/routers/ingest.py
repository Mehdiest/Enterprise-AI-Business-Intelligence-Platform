"""
Data ingestion API endpoints.

Responsibilities
----------------
- Receive CSV uploads
- Validate uploaded files
- Execute ETL pipeline
- Load warehouse
"""

from __future__ import annotations

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.data import IngestionResponse

from app.services.etl.csv_loader import (
    CSVLoader,
    CSVLoaderError,
)
from app.services.etl.transformer import DataTransformer
from app.services.etl.warehouse_loader import WarehouseLoader

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ingest",
    tags=["Data Ingestion"],
)


@router.post(
    "/csv",
    response_model=IngestionResponse,
)
async def ingest_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload CSV and execute ETL pipeline.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    temp_path: Path | None = None
    max_bytes = settings.max_upload_mb * 1024 * 1024

    try:

        with NamedTemporaryFile(
            delete=False,
            suffix=".csv",
        ) as temp_file:

            size = 0
            while chunk := await file.read(65_536):
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds {settings.max_upload_mb} MB limit.",
                    )
                temp_file.write(chunk)
            temp_path = Path(temp_file.name)

        loader = CSVLoader()

        dataframe = loader.load(
            temp_path,
        )

        rows_received = len(dataframe)

        transformer = DataTransformer()

        dataframe = transformer.transform(
            dataframe,
        )

        warehouse_loader = WarehouseLoader(
            db,
        )

        rows_loaded = warehouse_loader.load_dataframe(
            dataframe,
        )

        logger.info(
            "CSV ingested successfully | user=%s | rows=%s",
            current_user.email,
            rows_loaded,
        )

        return IngestionResponse(
            success=True,
            rows_received=rows_received,
            rows_loaded=rows_loaded,
            message="Data loaded successfully.",
        )

    except CSVLoaderError as exc:

        logger.warning(
            "Invalid CSV uploaded by user=%s : %s",
            current_user.email,
            str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "CSV ingestion failed for user=%s",
            current_user.email,
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        )

    finally:

        if temp_path and temp_path.exists():
            temp_path.unlink(
                missing_ok=True,
            )