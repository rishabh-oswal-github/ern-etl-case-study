# ern-etl-case-study

# ETL Case Study with FastAPI

This repository contains the code for an ETL (Extract, Transform, Load) case study implemented using FastAPI. The application is designed to process datasets, calculate statistical metrics such as mean and standard deviation, and store the results in a PostgreSQL database. It also provides an API to retrieve these statistics using a unique request ID.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [CI Pipeline](#ci-pipeline)
- [Contributing](#contributing)

## Features

- Calculate and store statistical metrics (mean and standard deviation).
- Retrieve statistics by request ID via an API endpoint.
- Validate UUID format for request IDs.
- Implemented using FastAPI for high performance and scalability.
- Dockerized for easy setup and deployment.
- Includes comprehensive unit tests using pytest.
- CI/CD pipeline for automated testing and deployment.

## Technologies Used

- **FastAPI** - A modern web framework for building APIs with Python 3.7+.
- **PostgreSQL** - An advanced, open-source relational database system.
- **Docker** - A platform for containerizing applications.
- **Pytest** - A testing framework for Python.
- **GitHub Actions** - CI/CD pipeline for automated testing and deployment.

## Requirements

- Github Account [Sign Up here](https://github.com)
- Git [How to Install](https://git-scm.com/downloads)
- Docker & Docker Compose ([How to Install](https://docs.docker.com/compose/install/))

## Installation

1. Clone the repository on your machine:

```bash
   git clone https://github.com/rishabh-oswal-github/ern-etl-case-study
   cd cern-etl-case-study
```

2. Build and run the Docker container:

```bash
   docker compose up --build
```

3. The API will be available at http://localhost:8000

4. The API Docs will be avialable at http://localhost:8000/docs OR http://localhost:8000/redoc

5. To run the unittests execute the below command
```bash
   docker compose run app pytest
```

### API Endpoints

1: Ingest and Submit Data
- Endpoint: /ingest
- Method: POST
- Description: Submit a dataset and receive a request ID.

Sample Request:

```json
{
    "time_stamp": "2024-08-15T14:30:00+0000",
    "data": [1, 2, 3, 4, 5]
}
```

Successfull Response:

```json
{
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

2: Retrieve Statistics

- Endpoint: /get_stats/{request_id}
- Method: GET
- Description: Retrieve the mean and standard deviation associated with a request ID.

Sample Request

```json
{
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Successfull Response:

```json
{
    "mean": 2,
    "std_dev": 4
}
```

### CI Pipeline

- The CI pipelines runs everytime a pull request to main is created or code is pushed to main branch.
- The CI pipeline tests if Postgres DB is functioning and available
- The CI pipeline also tests the unittest code written for the API in the /tests directory in this repo.

### Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (git checkout -b feature/your-feature-name).
3. Commit your changes (git commit -m 'Add some feature').
4. Push to the branch (git push origin feature/your-feature-name).
5. Create a new Pull Request.