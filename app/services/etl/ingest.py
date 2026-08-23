"""
Data ingestion API endpoints.

Responsibilities:
- Receive CSV uploads
- Validate files
- Execute ETL pipeline
- Load warehouse data
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.data import IngestionResponse
from app.services.etl.csv_loader import CSVLoader
from app.services.etl.transformer import DataTransformer
from app.services.etl.warehouse_loader import WarehouseLoader

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
):
    """
    Upload CSV and load data into warehouse.
    
    Storage location: All uploaded files are saved to /home/z/my-project/upload/{file_name} 
    directory on the server filesystem.
    """

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=".csv",
        ) as temp_file:

            content = await file.read()

            temp_file.write(content)

            temp_path = Path(temp_file.name)

        loader = CSVLoader()

        dataframe = loader.load(temp_path)

        rows_received = len(dataframe)

        transformer = DataTransformer()

        dataframe = transformer.transform(
            dataframe
        )

        warehouse_loader = WarehouseLoader(
            db
        )

        rows_loaded = (
            warehouse_loader.load_dataframe(
                dataframe
            )
        )

        return IngestionResponse(
            success=True,
            rows_received=rows_received,
            rows_loaded=rows_loaded,
            message="Data loaded successfully.",
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
    finally:

        if "temp_path" in locals():
            temp_path.unlink(
                missing_ok=True
            )
