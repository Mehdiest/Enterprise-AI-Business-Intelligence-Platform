"""CSV ingestion API endpoints."""

from __future__ import annotations

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies.rbac import require_admin
from app.schemas.data import IngestionResponse
from app.services.etl.csv_loader import CSVLoader, CSVLoaderError
from app.services.etl.transformer import DataTransformer
from app.services.etl.warehouse_loader import WarehouseLoader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Data Ingestion"])


@router.post("/csv", response_model=IngestionResponse)
async def ingest_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
) -> IngestionResponse:
    """Ingest an uploaded sales CSV."""
    _validate_csv(file)
    temp_path: Path | None = None
    try:
        temp_path = await _save_upload(file)
        received_rows, loaded_rows = await _load_csv(temp_path, db)
        logger.info("CSV ingested | user=%s | rows=%s", current_user.email, loaded_rows)
        return _ingestion_response(received_rows, loaded_rows)
    except CSVLoaderError as exc:
        logger.warning("Invalid CSV | user=%s | error=%s", current_user.email, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception:
        logger.exception("CSV ingestion failed | user=%s", current_user.email)
        raise HTTPException(status_code=500, detail="Internal server error.") from None
    finally:
        _delete_temp_file(temp_path)


def _validate_csv(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")


async def _save_upload(file: UploadFile) -> Path:
    max_bytes = settings.max_upload_mb * 1024 * 1024
    with NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        await _write_chunks(file, temp_file, max_bytes)
        return Path(temp_file.name)


async def _write_chunks(file: UploadFile, temp_file, max_bytes: int) -> None:
    byte_count = 0
    while chunk := await file.read(65_536):
        byte_count += len(chunk)
        if byte_count > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds {settings.max_upload_mb} MB limit.",
            )
        temp_file.write(chunk)


async def _load_csv(temp_path: Path, db: AsyncSession) -> tuple[int, int]:
    dataframe = CSVLoader().load(temp_path)
    received_rows = len(dataframe)
    transformed_data = DataTransformer().transform(dataframe)
    loaded_rows = await WarehouseLoader(db).load_dataframe(transformed_data)
    return received_rows, loaded_rows


def _ingestion_response(received_rows: int, loaded_rows: int) -> IngestionResponse:
    return IngestionResponse(
        success=True,
        rows_received=received_rows,
        rows_loaded=loaded_rows,
        message="Data loaded successfully.",
    )


def _delete_temp_file(temp_path: Path | None) -> None:
    if temp_path and temp_path.exists():
        temp_path.unlink(missing_ok=True)
