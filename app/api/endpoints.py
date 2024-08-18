import logging
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import engine, get_db_session
from app.models import Base, DataRecord
from app.schemas import DataPayload, IngestDataResponse, StatsResponse
from app.utils.utils import process_data, insert_record, is_uuid_valid, validate_request

router = APIRouter()

@router.post("/ingest/", response_model=IngestDataResponse)
def ingest_data(payload: DataPayload, db: Session = Depends(get_db_session)):
    """
    Ingests data, processes it, and stores the processed data in the database.

    This endpoint accepts a payload of data, validates the payload, processes it to calculate 
    statistical metrics, and then stores the processed data in the database. The function 
    returns a response containing a unique request ID that can be used to fetch the 
    statistics later.

    Args:
        payload (DataPayload): The input data payload containing the data to be processed.
        db (Session, optional): The database session used to interact with the PostgreSQL 
        database. Defaults to the session provided by the `get_db_session` dependency.

    Returns:
        IngestDataResponse: A response object containing the request ID and a success message.
    """
    validate_request(payload.model_dump())
    processed_data = process_data(payload=payload.model_dump())
    insert_record(session=db, model=DataRecord, data=processed_data)
    ingest_data_response = IngestDataResponse(
                request_id=processed_data["request_id"],
                message="Request submitted successfully. Please use request id to fetch stats"
            )
    return ingest_data_response

@router.get("/get_stats/{request_id}", response_model=StatsResponse)
def get_stats(request_id: str, db: Session = Depends(get_db_session)):
    """
    Endpoint to fetch statistics (mean and standard deviation) using a request ID.
    
    Args:
        request_id (str): The unique request ID.
    
    Returns:
        StatsResponse: The mean and standard deviation associated with the request ID.
    """
    if not is_uuid_valid(request_id):
        raise HTTPException(status_code=400,
                detail="400: Bad Request: Request ID not valid. Value should be of UUID type")
    record = db.query(DataRecord).filter(DataRecord.request_id == request_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Request ID not found")
    return StatsResponse(mean=record.mean, std_dev=record.std_dev)
