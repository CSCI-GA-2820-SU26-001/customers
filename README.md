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
- `suspended` — a boolean flag that indicates whether the customer account is suspended. New customers default to `false`.

The service is built following **Test-Driven Development (TDD)**: tests are written first, then code is written to make those tests pass.

## Project Structure

```text
.gitignore               - files Git should ignore
.flaskenv                - environment variables for Flask (e.g., which app to run)
.gitattributes           - fixes line-ending issues between Mac/Windows
.devcontainer/           - config for VSCode Dev Containers (cloud dev environment)
dot-env-example          - copy to .env to set local environment variables
Dockerfile               - production image for the Customers service
Makefile                 - common commands for testing, linting, building, pushing, and deploying
Pipfile                  - Python package dependencies

k8s/                            - Kubernetes manifests for local deployment
├── deployment.yaml             - Customers service Deployment
├── service.yaml                - Customers service ClusterIP Service
├── ingress.yaml                - Ingress for external access
└── postgres/                   - PostgreSQL Kubernetes manifests
    ├── configmap.yaml          - PostgreSQL configuration
    ├── pvc.yaml                - persistent volume claim for database storage
    ├── secret.yaml             - PostgreSQL credentials and database URI
    ├── service.yaml            - PostgreSQL ClusterIP Service
    └── statefulset.yaml        - PostgreSQL StatefulSet

service/                        - the main application package
├── __init__.py                 - initializes the Flask app
├── config.py                   - app configuration (database URL, etc.)
├── models.py                   - Customer data model + database logic
├── routes.py                   - HTTP API endpoints for customers
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
- **`serialize()`** — converts a Customer object into a plain dictionary so it can be sent as JSON
- **`deserialize(data)`** — converts a dictionary from a JSON request into a Customer object, with validation
- **`Customer.all()`** — returns every customer in the database
- **`Customer.find(user_id)`** — looks up a single customer by their `user_id`
- **`Customer.find_by_first_name(first_name)`** — returns customers with a matching first name
- **`Customer.find_by_last_name(last_name)`** — returns customers with a matching last name
- **`Customer.find_by_name(first_name, last_name)`** — returns customers that match both first name and last name

`user_id`, `first_name`, `last_name`, and `address` are required and must be non-empty strings. If any required field is missing or blank, a `DataValidationError` is raised.

The `suspended` field is optional on create and defaults to `false`. If provided, `suspended` must be a boolean.

Character limits are enforced at the database level: `user_id`, `first_name`, and `last_name` are capped at 63 characters; `address` is capped at 256 characters.

## The API (`service/routes.py`)

All responses with a body are returned as JSON. DELETE returns `204 No Content` with an empty body. The `Content-Type` header must be `application/json` for any request that sends a body, such as POST and PUT.

| Method | URL | Description | Success Code |
| -------- | ----- | ------------- | -------------- |
| GET | `/` | Service info | `200 OK` |
| GET | `/health` | Health check for Kubernetes liveness/readiness probes | `200 OK` |
| POST | `/customers` | Create a new customer | `201 Created` |
| GET | `/customers` | List all customers | `200 OK` |
| GET | `/customers?first_name={first_name}` | Query customers by first name | `200 OK` |
| GET | `/customers?last_name={last_name}` | Query customers by last name | `200 OK` |
| GET | `/customers?first_name={first_name}&last_name={last_name}` | Query customers by first and last name | `200 OK` |
| GET | `/customers/{user_id}` | Read a single customer | `200 OK` |
| PUT | `/customers/{user_id}` | Update an existing customer | `200 OK` |
| PUT | `/customers/{user_id}/suspend` | Suspend an existing customer account | `200 OK` |
| DELETE | `/customers/{user_id}` | Delete a customer | `204 No Content` |

### Health check

**Health check — `GET /health`**

Request:

```bash
curl -i http://localhost:8080/health
```

Response (`200 OK`):

```json
{
  "status": "OK"
}
```

This endpoint is used by Kubernetes liveness and readiness probes.

### Create a customer

**Create a customer — `POST /customers`**

Request:

```bash
curl -i -X POST http://localhost:8080/customers \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user42","first_name":"John","last_name":"Doe","address":"123 Main Street"}'
```

Request body:

```json
{
  "user_id": "user42",
  "first_name": "John",
  "last_name": "Doe",
  "address": "123 Main Street"
}
```

Response (`201 Created`):

```json
{
  "address": "123 Main Street",
  "first_name": "John",
  "last_name": "Doe",
  "suspended": false,
  "user_id": "user42"
}
```

The response includes a `Location` header that points to the newly created customer resource:

```text
Location: /customers/user42
```

The `suspended` field may also be included in the request body. If it is omitted, it defaults to `false`.

### List and query customers

Query support extends the existing `GET /customers` List endpoint by applying optional query string filters. It is not a separate endpoint.

**List all customers — `GET /customers`**

Request:

```bash
curl -i http://localhost:8080/customers
```

Response (`200 OK`):

```json
[
  {
    "address": "123 Main Street",
    "first_name": "John",
    "last_name": "Doe",
    "suspended": false,
    "user_id": "user42"
  }
]
```

If no customers exist, the service returns an empty list:

```json
[]
```

**Query customers by first name**

Request:

```bash
curl -i "http://localhost:8080/customers?first_name=John"
```

Response (`200 OK`):

```json
[
  {
    "address": "123 Main Street",
    "first_name": "John",
    "last_name": "Doe",
    "suspended": false,
    "user_id": "user42"
  }
]
```

**Query customers by last name**

Request:

```bash
curl -i "http://localhost:8080/customers?last_name=Doe"
```

Response (`200 OK`):

```json
[
  {
    "address": "123 Main Street",
    "first_name": "John",
    "last_name": "Doe",
    "suspended": false,
    "user_id": "user42"
  }
]
```

**Query customers by first name and last name**

Request:

```bash
curl -i "http://localhost:8080/customers?first_name=John&last_name=Doe"
```

Response (`200 OK`):

```json
[
  {
    "address": "123 Main Street",
    "first_name": "John",
    "last_name": "Doe",
    "suspended": false,
    "user_id": "user42"
  }
]
```

If no customers match the query, the service returns an empty list:

```json
[]
```

### Read a customer

**Read a customer — `GET /customers/{user_id}`**

Request:

```bash
curl -i http://localhost:8080/customers/user42
```

Response (`200 OK`):

```json
{
  "address": "123 Main Street",
  "first_name": "John",
  "last_name": "Doe",
  "suspended": false,
  "user_id": "user42"
}
```

If the customer does not exist, the service returns `404 Not Found`.

### Update a customer

**Update a customer — `PUT /customers/{user_id}`**

Request:

```bash
curl -i -X PUT http://localhost:8080/customers/user42 \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Smith","address":"456 Elm Street"}'
```

Request body:

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "address": "456 Elm Street"
}
```

Response (`200 OK`):

```json
{
  "address": "456 Elm Street",
  "first_name": "John",
  "last_name": "Smith",
  "suspended": false,
  "user_id": "user42"
}
```

For updates, the service uses the `user_id` from the URL path. If a different `user_id` is provided in the request body, it is ignored.

### Suspend a customer

**Suspend a customer — `PUT /customers/{user_id}/suspend`**

This action marks an existing customer account as suspended. It does not delete the customer record.

Request:

```bash
curl -i -X PUT http://localhost:8080/customers/user42/suspend
```

Response (`200 OK`):

```json
{
  "address": "123 Main Street",
  "first_name": "John",
  "last_name": "Doe",
  "suspended": true,
  "user_id": "user42"
}
```

A suspended customer can still be retrieved with `GET /customers/{user_id}`. The response will include `"suspended": true`.

If the customer does not exist, the service returns `404 Not Found`.

### Delete a customer

**Delete a customer — `DELETE /customers/{user_id}`**

Request:

```bash
curl -i -X DELETE http://localhost:8080/customers/user42
```

Response:

```text
HTTP/1.1 204 No Content
```

DELETE is idempotent. Whether the customer exists or not, the response is always `204 No Content` with an empty body.

### Validation and error responses

For create requests, `user_id`, `first_name`, `last_name`, and `address` are required and must be non-empty strings. The `suspended` field is optional and defaults to `false`. If `suspended` is provided, it must be a boolean.

For update requests, `first_name`, `last_name`, and `address` are required in the request body, and the `user_id` is taken from the URL path.

All API error responses are returned as JSON with `status`, `error`, and `message` fields.

Common error codes used by this service:

| Status Code | Meaning |
| -------- | -------- |
| `400 Bad Request` | Missing or blank fields, invalid data, or invalid `suspended` value |
| `404 Not Found` | Customer not found |
| `405 Method Not Allowed` | Unsupported HTTP method on a route |
| `409 Conflict` | Duplicate `user_id` on create |
| `415 Unsupported Media Type` | Missing or wrong `Content-Type` header |
| `500 Internal Server Error` | Unexpected server error |

Example error response:

```json
{
  "error": "Bad Request",
  "message": "Invalid request data",
  "status": 400
}
```

## Local Kubernetes Deployment

The service can be deployed to a local K3D/K3S Kubernetes cluster using the Makefile commands from the Kubernetes lab.

### Build and deploy locally

Create a local Kubernetes cluster:

```bash
make cluster
```

Build the Customers service container image:

```bash
make build
```

Push the image to the local registry:

```bash
make push
```

Deploy PostgreSQL and the Customers service to Kubernetes:

```bash
make deploy
```

The deployment includes:

- PostgreSQL running as a Kubernetes StatefulSet
- PostgreSQL persistent storage through a PersistentVolumeClaim
- Customers service Deployment
- Customers service ClusterIP Service
- Ingress for external access
- `/health` liveness and readiness probes

After deployment, verify the pods are running:

```bash
kubectl get pods
```

Expected result:

```text
customers-...   1/1   Running
postgres-0      1/1   Running
```

Verify the service through the ingress:

```bash
curl -i http://localhost:8080/health
curl -i http://localhost:8080/customers
```

## Tests (`tests/`)

### `test_models.py`

Tests the Customer model directly against the database. Covers:

- Creating, finding, listing, updating, and deleting customers
- Querying customers by first name, last name, and first name plus last name
- Serializing and deserializing customer data
- Default and validation behavior for the `suspended` field
- Validation errors for missing or empty fields
- Database error handling using mocks to simulate DB failures

### `test_routes.py`

Tests the HTTP API endpoints. Covers route tests for:

- Create (`POST /customers`)
- Read (`GET /customers/{user_id}`)
- Update (`PUT /customers/{user_id}`)
- Delete (`DELETE /customers/{user_id}`)
- List (`GET /customers`)
- Query (`GET /customers?first_name=...` and `GET /customers?last_name=...`)
- Suspend (`PUT /customers/{user_id}/suspend`)
- Health (`GET /health`)
- Root URL (`GET /`)
- Error handling cases, including missing or blank fields, invalid `suspended` values, customer not found, wrong HTTP method, unsupported media type, and duplicate `user_id`

### `factories.py`

Uses the `factory-boy` library to generate realistic fake Customer objects for use in tests. This avoids the need to hand-craft test data.

## Setup

### Prerequisites

- Python 3.12
- PostgreSQL running locally or via Docker dev container
- Docker
- K3D / Kubernetes for local deployment

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

### Run the service locally

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

## Continuous Integration

This repository uses GitHub Actions for Continuous Integration.

The CI workflow runs on pull requests and pushes to `master`. It performs:

- flake8 checks
- pylint checks
- pytest unit tests
- coverage reporting
- Codecov upload

The CI badge and Codecov badge at the top of this README show the current build and coverage status.

## Tech Stack

| Tool | Purpose |
| ------ | --------- |
| Flask 3.1 | Web framework — handles HTTP requests |
| Flask-SQLAlchemy 3.1 | ORM — translates Python objects to database rows |
| PostgreSQL / psycopg | Database |
| pytest | Test runner |
| factory-boy | Fake data generation for tests |
| gunicorn | Production web server |
| pylint / flake8 | Code quality and formatting |
| Docker | Container image build and runtime |
| Kubernetes / K3D | Local container orchestration |
| GitHub Actions | Continuous Integration |
| Codecov | Coverage reporting |

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.