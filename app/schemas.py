from pydantic import BaseModel, Field

class DataPayload(BaseModel):
    time_stamp: str = Field(..., json_schema_extra={"examples": ["2019-05-01T06:00:00-04:00"]})
    data: list[float] = Field(..., json_schema_extra={"examples": [[1.01, 2.11, 3.11, 4.11, 5.11]]})

# Response model for returning stats
class IngestDataResponse(BaseModel):
    request_id: str
    message: str

# Response model for returning stats
class StatsResponse(BaseModel):
    mean: float
    std_dev: float