from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.main import app
from app.models import DataRecord
from app.database import get_db_session

client = TestClient(app)

def test_ingest_data():
    payload = {
        "time_stamp": "2019-05-01T06:00:00-04:00",
        "data": [1.0, 2.0, 3.0, 4.0]
    }
    response = client.post("/ingest/", json=payload)
    assert response.status_code == 200
    assert type(response.json()["request_id"]) == str
    assert response.json()["message"] == "Request submitted successfully. Please use request id to fetch stats"

# Mock database session fixture
@pytest.fixture
def db_session():
    session = MagicMock(spec=Session)
    yield session

# Mock data record fixture
@pytest.fixture
def mock_data_record():
    return DataRecord(request_id="550e8400-e29b-41d4-a716-446655440000", mean=10.0, std_dev=2.0)

# Dependency override to use the mock database session
@pytest.fixture(autouse=True)
def override_get_db_session(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session
    yield
    app.dependency_overrides.clear()

def test_get_stats_valid_request_id(db_session, mock_data_record):
    """
    Test that a valid request ID returns the correct mean and standard deviation.
    """
    # Mock the query result to return the mock data record
    db_session.query().filter().first.return_value = mock_data_record

    # Call the API endpoint with a valid request ID
    response = client.get(f"/get_stats/{mock_data_record.request_id}")
    
    # Assert the response status and data
    assert response.status_code == 200
    assert response.json() == {"mean": 10.0, "std_dev": 2.0}

def test_get_stats_invalid_request_id_format(db_session):
    """
    Test that an invalid request ID format raises a 400 error.
    """
    invalid_uuid = "1234-invalid-uuid"

    response = client.get(f"/get_stats/{invalid_uuid}")
    
    assert response.status_code == 400
    assert "Request ID not valid" in response.json()["detail"]

def test_get_stats_request_id_not_found(db_session):
    """
    Test that a non-existent request ID returns a 404 error.
    """
    # Mock the query result to return None (i.e., request ID not found)
    db_session.query().filter().first.return_value = None

    valid_uuid = "550e8400-e29b-41d4-a716-446655440000"

    response = client.get(f"/get_stats/{valid_uuid}")
    
    assert response.status_code == 404
    assert "Request ID not found" in response.json()["detail"]
