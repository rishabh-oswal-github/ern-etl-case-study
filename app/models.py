from sqlalchemy import Column, Float, Time
from sqlalchemy.types import Uuid
from .database import Base

class DataRecord(Base):
    __tablename__ = "data_records"

    request_id = Column(Uuid, primary_key=True, index=True)
    timestamp = Column(Time, index=True)
    mean = Column(Float)
    std_dev = Column(Float)
    # Recommeded by FastAPI and PyDantic
    class Config:
        orm_mode = True