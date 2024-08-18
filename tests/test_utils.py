import pytz
import pytest
import numpy as np
from datetime import datetime, timezone
import uuid
from fastapi import HTTPException
from app.utils.utils import process_data, transform_timestamp,\
    validate_request, is_uuid_valid
from app.models import DataRecord
import logging

def test_transform_timestamp():
    # Test case 1: Standard conversion from EST to UTC
    est_time = "2023-08-15T14:30:00-0400"  # 14:30 in US/Eastern
    expected_utc_time = datetime(2023, 8, 15, 18, 30, tzinfo=timezone.utc)  # 18:30 in UTC 
    assert transform_timestamp(est_time) == expected_utc_time

    # Test case 2: Different timezone conversion (e.g., PST to UTC)
    pst_time = "2023-08-15T14:30:00-0700"  # 14:30 in US/Pacific
    expected_utc_time = datetime(2023, 8, 15, 21, 30, tzinfo=timezone.utc)  # 21:30 in UTC
    assert transform_timestamp(pst_time, from_tz='US/Pacific') == expected_utc_time

    # Test case 3: Different time format
    est_time_alt_format = "2023-08-15 14:30:00"
    expected_utc_time_alt_format = datetime(2023, 8, 15, 18, 30, tzinfo=timezone.utc)
    assert transform_timestamp(est_time_alt_format, time_format='%Y-%m-%d %H:%M:%S') == expected_utc_time_alt_format

def test_transform_timestamp_invalid():
    # Test case 4: Invalid time format
    invalid_time = "2023-08-15 14:30:00-0400"
    with pytest.raises(ValueError):
        transform_timestamp(invalid_time, time_format='%Y-%m-%dT%H:%M:%S%z')

    # Test case 5: Non-existent timezone
    with pytest.raises(pytz.UnknownTimeZoneError):
        transform_timestamp("2023-08-15T14:30:00-0400", from_tz='Invalid/Timezone')

def test_process_data():
    # Test case 1: Basic functionality
    payload = {
        "time_stamp": "2023-08-15T14:30:00-0400",
        "data": [1, 2, 3, 4, 5]
    }
    expected_timestamp = datetime(2023, 8, 15, 18, 30, tzinfo=timezone.utc)  # 18:30 in UTC
    expected_mean = 3.0
    expected_std_dev = np.std([1, 2, 3, 4, 5])
    
    resposne = process_data(payload)
    
    assert type(resposne["request_id"]) == str
    assert resposne["timestamp"] == expected_timestamp
    assert resposne["mean"] == expected_mean
    assert resposne["std_dev"] == expected_std_dev

def test_process_data_invalid_timestamp():
    # Test case 3: Invalid timestamp format
    payload = {
        "time_stamp": "invalid-timestamp",
        "data": [1, 2, 3]
    }
    with pytest.raises(ValueError):
        process_data(payload)

def test_validate_request_valid():
    """
    Test that a valid request passes validation.
    """
    payload = {
        'time_stamp': '2023-08-15T14:30:00+0000',
        'data': [1, 2, 3, 4, 5]
    }
    # This should not raise an exception
    try:
        validate_request(payload)
    except HTTPException:
        pytest.fail("validate_request() raised HTTPException unexpectedly!")

def test_validate_request_invalid_timestamp():
    """
    Test that an invalid timestamp raises an HTTPException.
    """
    payload = {
        'time_stamp': '2023-08-15 14:30:00',  # Invalid format
        'data': [1, 2, 3, 4, 5]
    }
    with pytest.raises(HTTPException) as excinfo:
        validate_request(payload)
    assert excinfo.value.status_code == 400
    assert "Invalid timestamp format" in str(excinfo.value.detail)

def test_validate_request_empty_data():
    """
    Test that an empty data list raises an HTTPException.
    """
    payload = {
        'time_stamp': '2023-08-15T14:30:00+0000',
        'data': []  # Empty data list
    }
    with pytest.raises(HTTPException) as excinfo:
        validate_request(payload)
    assert excinfo.value.status_code == 400
    assert "Data field must be a non-empty list" in str(excinfo.value.detail)

def test_validate_request_non_numeric_data():
    """
    Test that a non-numeric data list raises an HTTPException.
    """
    payload = {
        'time_stamp': '2023-08-15T14:30:00+0000',
        'data': [1, 'two', 3, 4, 5]  # Non-numeric value in data list
    }
    with pytest.raises(HTTPException) as excinfo:
        validate_request(payload)
    assert excinfo.value.status_code == 400
    assert "All elements in the data list must be numbers" in str(excinfo.value.detail)

def test_validate_request_invalid_time_format():
    """
    Test that an invalid time zone in the timestamp raises an HTTPException.
    """
    payload = {
        'time_stamp': '2023-08-15 14:30:00+00:00',  # Invalid timezone format
        'data': [1, 2, 3, 4, 5]
    }
    with pytest.raises(HTTPException) as excinfo:
        validate_request(payload)
    assert excinfo.value.status_code == 400
    assert "Invalid timestamp format" in str(excinfo.value.detail)

def test_is_uuid_valid_valid_uuid_v4():
    """
    Test that a valid UUID version 4 returns True.
    """
    valid_uuid = str(uuid.uuid4())  # Generate a valid UUID v4
    assert is_uuid_valid(valid_uuid) is True

def test_is_uuid_valid_valid_uuid_v1():
    """
    Test that a valid UUID version 1 returns True.
    """
    valid_uuid = str(uuid.uuid1())  # Generate a valid UUID v1
    assert is_uuid_valid(valid_uuid, version=1) is True

def test_is_uuid_valid_invalid_uuid():
    """
    Test that an invalid UUID string returns False.
    """
    invalid_uuid = "1234-invalid-uuid"
    assert is_uuid_valid(invalid_uuid) is False

def test_is_uuid_valid_empty_string():
    """
    Test that an empty string returns False.
    """
    assert is_uuid_valid("") is False

def test_is_uuid_valid_none_input():
    """
    Test that passing None as input returns False.
    """
    assert is_uuid_valid(None) is False

def test_is_uuid_valid_invalid_format():
    """
    Test that an incorrectly formatted UUID string returns False.
    """
    invalid_uuid = "550e8400-e29b-41d4-a716-446655440000-1234"  # Extra characters
    assert is_uuid_valid(invalid_uuid) is False