from datetime import datetime
import pytz
import numpy as np
from sqlalchemy.exc import SQLAlchemyError
import uuid

from datetime import datetime
from fastapi import HTTPException

def validate_request(payload):
    """
    Validates the incoming data submission request.
    
    Args:
        payload (dict): The data payload containing 'time_stamp' and 'data'.
    
    Raises:
        HTTPException: If the validation fails.
    """
    # Check if timestamp is in a valid format
    try:
        datetime.strptime(payload['time_stamp'], '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format. Expected format: YYYY-MM-DDTHH:MM:SS±hhmm")

    # Check if data is a non-empty list
    if not isinstance(payload['data'], list) or len(payload['data']) == 0:
        raise HTTPException(status_code=400, detail="Data field must be a non-empty list.")
    
    # Check if all elements in the data list are numbers
    if not all(isinstance(x, (int, float)) for x in payload['data']):
        raise HTTPException(status_code=400, detail="All elements in the data list must be numbers.")

def transform_timestamp(timestamp_str, from_tz='US/Eastern', to_tz='UTC', time_format='%Y-%m-%dT%H:%M:%S%z'):
    """
    Transforms a timestamp from one timezone to another.
    
    Args:
        timestamp_str (str): The original timestamp as a string.
        from_tz (str): The timezone of the original timestamp (default is 'US/Eastern').
        to_tz (str): The target timezone to convert to (default is 'UTC').
        time_format (str): The format in which the timestamp is given (default is '%Y-%m-%dT%H:%M:%S%z').
    
    Returns:
        str: The transformed timestamp as a string in the target timezone.
    """
    # Parse the original timestamp string into a datetime object
    from_zone = pytz.timezone(from_tz)
    to_zone = pytz.timezone(to_tz)
    
    timestamp = datetime.strptime(timestamp_str, time_format)
    if timestamp.tzinfo is None:
        timestamp = from_zone.localize(timestamp)
    # Convert the timestamp to the target timezone
    converted_timestamp = timestamp.astimezone(to_zone)
    
    # Return the converted timestamp
    return converted_timestamp

def process_data(payload):
    """
    Processes the input data payload by transforming the timestamp to UTC
    and calculating the mean and standard deviation of the data array.
    
    Args:
        payload (dict): The data payload containing a timestamp and a data array.
    
    Returns:
        dict: A dict containing the transformed UTC timestamp, mean, and standard deviation.
    """
    timestamp_utc = transform_timestamp(payload['time_stamp'])
    data = np.array(payload['data'])
    # Convert to explicit float datatypes so that data can be inserted in DB
    mean = float(data.mean())
    std_dev = float(data.std())
    
    return {'request_id': str(uuid.uuid4()), 'timestamp': timestamp_utc, 'mean': mean, 'std_dev': std_dev}

def insert_record(session, model, data):
    """
    Inserts a record into the specified table/model.
    
    Args:
        session (Session): SQLAlchemy session object.
        model (Base): SQLAlchemy ORM model representing the target table.
        data (dict): Dictionary containing column names as keys and values to insert.
    
    Returns:
        object: The inserted record object.
    """
    try:
        record = model(**data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting record: {e}")
        return None

def is_uuid_valid(uuid_to_test: str, version=4):
    """
    Validates whether uuid is valid or not
    
    Args:
        uuid_to_test (str): UUID string to validate.
        version (int): UUID version (1,2,3,4,5) Default value = 4
    
    Returns:
        Boolean: If valid true false otherwise
    """
    try:
        if uuid_to_test is None:
            return False
        # check for validity of Uuid
        uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return True