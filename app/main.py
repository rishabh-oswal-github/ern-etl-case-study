from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api import endpoints
from .database import engine, get_db_session
from .models import Base, DataRecord
from .schemas import DataPayload, IngestDataResponse, StatsResponse
from .utils.utils import process_data, insert_record

app = FastAPI()

# This makes sure that the Tables are created at runtime by the APP in the DB.
Base.metadata.create_all(bind=engine)

app.include_router(endpoints.router)

