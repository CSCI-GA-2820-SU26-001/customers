# NYU DevOps - Customers Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI](https://github.com/CSCI-GA-2820-SU26-001/customers/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU26-001/customers/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU26-001/customers/branch/master/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-SU26-001/customers)

A RESTful microservice for managing customer data, built with Flask and PostgreSQL as part of the NYU DevOps course.

## Overview

This service manages **Customer** records in a PostgreSQL database. Each customer has:

- `user_id` — a unique string identifier (e.g., `"user42"`)
- `first_name` — the customer's first name
- `last_name` — the customer's last name
- `address` — the customer's street address

The service is built following **Test-Driven Development (TDD)**: tests are written first, then code is written to make those tests pass.

## Project Structure

```text
.gitignore               - files Git should ignore
.flaskenv                - environment variables for Flask (e.g., which app to run)
.gitattributes           - fixes line-ending issues between Mac/Windows
.devcontainer/           - config for VSCode Dev Containers (cloud dev environment)
dot-env-example          - copy to .env to set local environment variables
Pipfile                  - Python package dependencies

service/                        - the main application package
├── __init__.py                 - initializes the Flask app
├── config.py                   - app configuration (database URL, etc.)
├── models.py                   - Customer data model + database logic
├── routes.py                   - HTTP API endpoints (full CRUD for customers)
└── common/
    ├── cli_commands.py         - Flask CLI command to recreate database tables
    ├── error_handlers.py       - handles HTTP errors (404, 400, etc.)
    ├── log_handlers.py         - sets up logging
    └── status.py               - HTTP status code constants (200, 201, 404, etc.)

tests/                          - all test cases
├── __init__.py                 - makes tests a Python package
├── factories.py                - generates fake Customer objects for testing
├── test_cli_commands.py        - tests for CLI commands
├── test_models.py              - tests for the Customer model (database logic)
└── test_routes.py              - tests for the HTTP API endpoints
```

## The Customer Model (`service/models.py`)

This file defines how a Customer is stored in and retrieved from the database. Key things it can do:

- **`create()`** — saves a new customer to the database
- **`update()`** — saves changes to an existing customer
- **`delete()`** — removes a customer from the database
- **`serialize()`** — converts a Customer object into a plain dictionary (so it can be sent as JSON)
- **`deserialize(data)`** — converts a dictionary (from a JSON request) into a Customer object, with validation
- **`Customer.all()`** — returns every customer in the database
- **`Customer.find(user_id)`** — looks up a single customer by their `user_id`

All fields (`user_id`, `first_name`, `last_name`, `address`) are required and must be non-empty strings. If any field is missing or blank, a `DataValidationError` is raised. Character limits are enforced at the database level: `user_id`, `first_name`, and `last_name` are capped at 63 characters; `address` is capped at 256 characters.

## The API (`service/routes.py`)

All responses with a body are returned as JSON. DELETE returns 204 No Content with an empty body. The `Content-Type` header must be `application/json` for any request that sends a body (POST, PUT).

| Method | URL | Description | Success Code |
| -------- | ----- | ------------- | -------------- |
| GET | `/` | Service info (name, message, status, links) | `200 OK` |
| POST | `/customers` | Create a new customer | `201 Created` |
| GET | `/customers` | List all customers | `200 OK` |
| GET | `/customers/{user_id}` | Read a single customer | `200 OK` |
| PUT | `/customers/{user_id}` | Update an existing customer | `200 OK` |
| DELETE | `/customers/{user_id}` | Delete a customer | `204 No Content` |

### Request / Response format

**Create a customer — `POST /customers`**

Request body:

```json
{
  "user_id": "user42",
  "first_name": "Jane",
  "last_name": "Doe",
  "address": "123 Main Street"
}
```

Response (`201 Created`):

```json
{
  "user_id": "user42",
  "first_name": "Jane",
  "last_name": "Doe",
  "address": "123 Main Street"
}
```

**Update a customer — `PUT /customers/{user_id}`**

Request body (`first_name`, `last_name`, and `address` are required; the `user_id` comes from the URL):

```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "address": "456 Elm Street"
}
```

Response (`200 OK`):

```json
{
  "user_id": "user42",
  "first_name": "Jane",
  "last_name": "Smith",
  "address": "456 Elm Street"
}
```

For updates, the service uses the `user_id` from the URL path. If a different `user_id` is provided in the request body, it is ignored.

For create requests, `user_id`, `first_name`, `last_name`, and `address` are required and must be non-empty strings. For update requests, `first_name`, `last_name`, and `address` are required in the request body, and the `user_id` is taken from the URL path.

All API error responses are returned as JSON with `status`, `error`, and `message` fields. Error codes used by this service: `400 Bad Request` (missing or blank fields), `404 Not Found` (customer not found), `405 Method Not Allowed` (unsupported HTTP method on a route), `409 Conflict` (duplicate `user_id` on create), `415 Unsupported Media Type` (missing or wrong `Content-Type` header), and `500 Internal Server Error` (unexpected server error).

DELETE is idempotent — whether the customer exists or not, the response is always `204 No Content` with an empty body.

## Tests (`tests/`)

### `test_models.py`

Tests the Customer model directly against the database. Covers:

- Creating, finding, listing, updating, and deleting customers
- Serializing and deserializing customer data
- Validation errors for missing or empty fields
- Database error handling (using mocks to simulate DB failures)

### `test_routes.py`

Tests the HTTP API endpoints. Covers route tests for Create (`POST /customers`), Read (`GET /customers/{user_id}`), Update (`PUT /customers/{user_id}`), Delete (`DELETE /customers/{user_id}`), List (`GET /customers`), root URL (`GET /`), and error handling cases (missing/blank fields, customer not found, wrong HTTP method, unsupported media type, duplicate `user_id`).

### `factories.py`

Uses the `factory-boy` library to generate realistic fake Customer objects for use in tests — no need to hand-craft test data.

## Setup

### Prerequisites

- Python 3.12
- PostgreSQL running locally (or via Docker dev container)

### Install dependencies

```bash
pip install pipenv
pipenv install --dev
```

### Configure environment

```bash
cp dot-env-example .env
# Edit .env with your database credentials
```

### Run the service

```bash
honcho start
```

The service will be available at `http://localhost:8080/`.

### Run the tests

```bash
make test
```

This runs `pytest` with coverage reporting. The target is **95% coverage** minimum. You can also run pytest directly:

```bash
pipenv run pytest --cov=service
```

### Lint the code

```bash
make lint
```

This runs `pylint` and `flake8` to enforce PEP8 style. Fix any warnings before opening a Pull Request.

## Tech Stack

| Tool | Purpose |
| ------ | --------- |
| Flask 3.1 | Web framework — handles HTTP requests |
| Flask-SQLAlchemy 3.1 | ORM — translates Python objects to database rows |
| PostgreSQL (psycopg 3.3) | Database |
| pytest 9.0 | Test runner |
| factory-boy 3.3 | Fake data generation for tests |
| gunicorn | Production web server |
| pylint / flake8 / black | Code quality and formatting |

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
