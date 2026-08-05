# NYU DevOps - Customers Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI](https://github.com/CSCI-GA-2820-SU26-001/customers/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU26-001/customers/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU26-001/customers/branch/master/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-SU26-001/customers)

A production-style Customers microservice built for NYU CSCI-GA.2820 DevOps and Agile Methodologies. The project includes a Flask-RESTX API, an administrative web UI, PostgreSQL persistence, automated unit and browser-based BDD tests, local Kubernetes deployment, GitHub Actions CI, and a six-stage Tekton CD pipeline on Red Hat OpenShift.

## Overview

The service manages Customer records with the following fields:

- `user_id` — unique customer identifier
- `first_name` — customer first name
- `last_name` — customer last name
- `address` — customer street address
- `suspended` — whether the account is suspended; defaults to `false`

The completed application provides:

- A browser-based administrative UI at `/`
- A Flask-RESTX REST API under `/api`
- Swagger/OpenAPI documentation at `/apidocs/`
- PostgreSQL persistence
- Query support by first name, last name, or both
- A stateful Suspend action
- Unit testing with pytest and coverage
- Browser-based BDD testing with Behave, Selenium, and headless Chrome
- GitHub Actions continuous integration
- A six-stage Tekton continuous delivery pipeline on OpenShift
- Automatic pipeline triggering on pushes to `master`

The service is built following **Test-Driven Development (TDD)**: tests are written first, then implementation is added to make the tests pass.

## Project Structure

```text
.gitignore                           - files Git should ignore
.flaskenv                            - Flask environment configuration
.gitattributes                       - repository line-ending configuration
.devcontainer/                       - VS Code Dev Container configuration
dot-env-example                      - example local environment variables

.github/
└── workflows/
    └── ci.yml                      - GitHub Actions CI workflow

.tekton/
├── pipeline.yaml                   - six-stage Tekton CD pipeline
├── tasks.yaml                      - custom Tekton Task definitions
├── workspace.yaml                  - shared pipeline PVC
└── events/
    ├── eventlistener.yaml          - receives GitHub webhook events
    ├── route-eventlistener.yaml    - public OpenShift Route for the listener
    ├── triggerbinding.yaml         - extracts repository URL and revision
    └── triggertemplate.yaml        - creates a PipelineRun

features/                            - Behave BDD test suite
├── customers.feature               - Gherkin scenarios
├── environment.py                  - Behave environment and browser setup
└── steps/
    └── web_steps.py                - shared browser interaction steps

k8s/                                - Kubernetes and OpenShift manifests
├── deployment.yaml                 - Customers Deployment
├── service.yaml                    - Customers Service
├── ingress.yaml                    - local Kubernetes ingress
├── route.yaml                      - OpenShift application Route
└── postgres/                       - PostgreSQL manifests

service/
├── __init__.py                     - Flask application initialization
├── config.py                       - application configuration
├── models.py                       - Customer model and database logic
├── routes.py                       - Flask-RESTX API routes
├── static/                         - administrative UI assets
└── common/
    ├── cli_commands.py              - Flask CLI commands
    ├── log_handlers.py              - application logging
    └── status.py                    - HTTP status constants

tests/
├── __init__.py                     - makes tests a Python package
├── factories.py                    - factory-boy test data
├── test_cli_commands.py            - CLI command tests
├── test_log_handlers.py            - logging handler tests
├── test_models.py                  - model tests
└── test_routes.py                  - API and route tests

Dockerfile                          - production container image
Makefile                            - test, lint, build, push, and deploy commands
Pipfile / Pipfile.lock              - Python dependencies
README.md                           - project documentation
```

The Kubernetes manifests are stored in the `./k8s/` path. Here, `./k8s/` and `k8s/` refer to the same project directory.

## Customer Model

The Customer model supports:

Key model methods include `create()`, `update()`, `delete()`, `serialize()`, `deserialize()`, `all()`, `find()`, `find_by_first_name()`, `find_by_last_name()`, and `find_by_name()`.

- Create, read, update, and delete operations
- Listing all customers
- Querying by first name
- Querying by last name
- Querying by first and last name together
- Serializing database objects to dictionaries
- Deserializing and validating request data
- Suspending a customer account

`user_id`, `first_name`, `last_name`, and `address` are required and must be non-empty strings. The `suspended` field is optional when creating a customer, defaults to `false`, and must be a boolean when provided.

Character limits are enforced at the database level:

- `user_id`: 63 characters
- `first_name`: 63 characters
- `last_name`: 63 characters
- `address`: 256 characters

## Administrative Web UI

The root URL `/` serves an administrative interface for managing customers. The UI supports:

- List
- Create
- Read
- Update
- Delete
- Query
- Suspend

The BDD suite tests the UI from the outside through the browser. It does not connect directly to the application internals or database.

## REST API

All REST resources use the `/api` prefix. Responses with a body are JSON. Requests with a body must use `Content-Type: application/json`.

| Method | URL | Description | Success |
|---|---|---|---|
| GET | `/` | Customer Administration UI | `200 OK` |
| GET | `/health` | Kubernetes health check | `200 OK` |
| GET | `/apidocs/` | Swagger/OpenAPI documentation | `200 OK` |
| POST | `/api/customers` | Create a customer | `201 Created` |
| GET | `/api/customers` | List all customers | `200 OK` |
| GET | `/api/customers?first_name={first_name}` | Query by first name | `200 OK` |
| GET | `/api/customers?last_name={last_name}` | Query by last name | `200 OK` |
| GET | `/api/customers?first_name={first_name}&last_name={last_name}` | Query by full name | `200 OK` |
| GET | `/api/customers/{user_id}` | Read a customer | `200 OK` |
| PUT | `/api/customers/{user_id}` | Update a customer | `200 OK` |
| PUT | `/api/customers/{user_id}/suspend` | Suspend a customer | `200 OK` |
| DELETE | `/api/customers/{user_id}` | Delete a customer | `204 No Content` |

### Health Check

```bash
curl -i http://localhost:8080/health
```

Expected response:

```json
{
  "status": "OK"
}
```

### Create a Customer

```bash
curl -i -X POST http://localhost:8080/api/customers \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user42",
    "first_name": "John",
    "last_name": "Doe",
    "address": "123 Main Street"
  }'
```

A successful response returns `201 Created`. The `Location` header points to:

```text
/api/customers/user42
```

### List Customers

```bash
curl -i http://localhost:8080/api/customers
```

If no customers exist, the API returns:

```json
[]
```

### Query Customers

By first name:

```bash
curl -i "http://localhost:8080/api/customers?first_name=John"
```

By last name:

```bash
curl -i "http://localhost:8080/api/customers?last_name=Doe"
```

By first and last name:

```bash
curl -i "http://localhost:8080/api/customers?first_name=John&last_name=Doe"
```

### Read a Customer

```bash
curl -i http://localhost:8080/api/customers/user42
```

A missing customer returns `404 Not Found`.

### Update a Customer

```bash
curl -i -X PUT http://localhost:8080/api/customers/user42 \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "address": "456 Elm Street"
  }'
```

The `user_id` is taken from the URL path.

### Suspend a Customer

```bash
curl -i -X PUT http://localhost:8080/api/customers/user42/suspend
```

A successful response includes `"suspended": true`. The customer remains available through the Read endpoint.

### Delete a Customer

```bash
curl -i -X DELETE http://localhost:8080/api/customers/user42
```

DELETE returns `204 No Content`. The operation is idempotent: deleting a missing customer also returns `204 No Content`.

### Error Responses

API errors are returned as JSON and include `status`, `error`, and `message`.

| Status | Meaning |
|---|---|
| `400 Bad Request` | Missing, blank, or invalid data |
| `404 Not Found` | Customer not found |
| `405 Method Not Allowed` | Unsupported method |
| `409 Conflict` | Duplicate `user_id` |
| `415 Unsupported Media Type` | Missing or incorrect content type |
| `500 Internal Server Error` | Unexpected server error |

Example:

```json
{
  "status": 400,
  "error": "Bad Request",
  "message": "Invalid request data"
}
```

## Swagger Documentation

The service uses Flask-RESTX annotations and Swagger data models to document request and response payloads.

Interactive Swagger/OpenAPI documentation is available locally at:

```text
http://localhost:8080/apidocs/
```

In the final OpenShift deployment:

```text
https://customers-nyu-customers-dev.apps.rm2.thpm.p1.openshiftapps.com/apidocs/
```

## Local Development

### Prerequisites

- Python 3.12
- PostgreSQL
- Docker
- Pipenv
- K3D/K3S and Kubernetes CLI tools for local deployment
- OpenShift CLI (`oc`) for remote deployment

### Install Dependencies

```bash
pip install pipenv
pipenv install --dev
```

### Configure the Environment

```bash
cp dot-env-example .env
```

Update `.env` with the required local database settings.

### Run the Service

```bash
honcho start
```

The service is available at `http://localhost:8080/`.

## Testing and Code Quality

### Unit Tests

```bash
make test
```

The project maintains at least 95% test coverage. The latest verified pipeline run completed 64 unit tests with 100% coverage.

The unit-test suite includes:

- `tests/test_models.py` — model CRUD, query, serialization, validation, and database error handling
- `tests/test_routes.py` — `/api/customers` CRUD, List, Query, Suspend, health, UI root, and HTTP error responses
- `tests/test_cli_commands.py` — Flask CLI command behavior
- `tests/test_log_handlers.py` — application logging handler behavior
- `tests/factories.py` — factory-boy data generation for test fixtures

### Linting

```bash
make lint
```

This runs pylint and flake8. The latest verified result was `10.00/10`.

### Behavior-Driven Development

The Gherkin scenarios are stored in `.feature` files under the `features/` directory. Their accompanying Selenium step definitions are stored under `features/steps/`.

Run the browser-based BDD suite locally with:

```bash
behave --no-capture
```

The suite covers:

- Create
- Read
- Update
- Delete
- List
- Query
- Suspend

Latest verified result:

```text
1 feature passed
16 scenarios passed
124 steps passed
```

The Tekton BDD Task runs the same suite against the deployed OpenShift Route using Selenium and headless Chrome. The BDD Task receives the Route through the `BASE_URL` parameter and runs only after deployment succeeds.

## Local Kubernetes Deployment

The Kubernetes manifests are stored in `./k8s/`.

Create the local Kubernetes cluster, build and push the image, and deploy the application:

```bash
make cluster
make build
make push
make deploy
```

Verify the deployment:

```bash
kubectl get pods
kubectl get services
kubectl get ingress
kubectl get statefulsets
kubectl get pvc
```

Test the service:

```bash
curl -i http://localhost:8080/health
curl -i http://localhost:8080/api/customers
```

The local deployment includes:

- PostgreSQL as a StatefulSet
- PostgreSQL persistent storage
- Customers Deployment
- Customers ClusterIP Service
- Ingress for external access
- Liveness and readiness probes using `/health`

## OpenShift Deployment

The final team deployment runs in the `nyu-customers-dev` OpenShift project.

Application Route:

```text
https://customers-nyu-customers-dev.apps.rm2.thpm.p1.openshiftapps.com
```

Available endpoints:

- Admin UI: `/`
- Health: `/health`
- REST API: `/api/customers`
- Swagger: `/apidocs/`

PostgreSQL is deployed manually to the OpenShift project before the CD pipeline runs:

```bash
oc apply -f ./k8s/postgres/
```

Apply the application manifests and Route:

```bash
oc apply -f ./k8s/
```

Deploy the Tekton Pipeline, Tasks, and shared workspace:

```bash
oc apply -f .tekton/
```

Deploy the EventListener resources:

```bash
oc apply -f .tekton/events/
```

## Continuous Integration

GitHub Actions runs on pull requests and pushes to `master`. The workflow performs:

- flake8
- pylint
- pytest
- coverage reporting
- Codecov upload

Pull requests should not be merged while tests fail or coverage decreases. The CI and Codecov badges at the top of this README show the current build and coverage status.

## Continuous Delivery Pipeline

The Tekton pipeline contains six stages:

1. `clone` — clones the GitHub repository
2. `lint` — runs pylint and flake8
3. `test` — runs unit tests and coverage
4. `build` — builds and pushes the application image
5. `deploy` — deploys the image to OpenShift
6. `bdd` — runs Selenium/Behave tests against the deployment

The `lint` and `test` Tasks run in parallel. The image is built only after both pass. Deployment runs after the build, and BDD testing runs after deployment.

The pipeline uses the shared `pipeline-pvc` workspace. The BDD Task receives the deployed application Route through the `BASE_URL` parameter.

## GitHub Webhook and EventListener

A GitHub push to `master` automatically triggers the Tekton pipeline through the following flow:

```text
GitHub push to master
        |
        v
OpenShift EventListener Route
        |
        v
EventListener
        |
        v
TriggerBinding + TriggerTemplate
        |
        v
PipelineRun
```

EventListener Route:

```text
https://el-github-listener-nyu-customers-dev.apps.rm2.thpm.p1.openshiftapps.com
```

The EventListener:

- Accepts GitHub `push` events
- Filters for `refs/heads/master`
- Reads the repository clone URL from the webhook payload
- Reads the pushed commit SHA from the webhook payload
- Creates a PipelineRun for the `customers` pipeline

The EventListener validates GitHub payloads with a Kubernetes Secret. The actual Secret must never be committed.

Create the Secret in the final namespace:

```bash
oc create secret generic github-webhook-secret \
  --from-literal=secretToken=<WEBHOOK_SECRET> \
  -n nyu-customers-dev
```

Configure the GitHub webhook with:

- Payload URL: the HTTPS EventListener Route
- Content type: `application/json`
- Secret: the same value used in `github-webhook-secret`
- Events: push only
- SSL verification: enabled
- Active: enabled

## Development Workflow

The project follows the course Social Coding and Agile workflow:

1. Create a GitHub Story and add it to the ZenHub backlog.
2. Assign the Story and move it to **In Progress**.
3. Use one feature branch for one Story.
4. Run tests and quality checks before opening a Pull Request.
5. Open one Pull Request for the Story and link it with `Closes #<issue-number>`.
6. Move the Story to **Review/QA** and request a teammate review.
7. Merge only after CI passes and a teammate approves.
8. A merge to `master` automatically triggers the Tekton CD pipeline.
9. Move the Story to **Done** after the implementation and deployment are verified.
10. Close completed Stories after the Sprint Review.

## Validation Summary

The completed project has been verified with:

- 64 unit tests passed
- 100% test coverage
- pylint score of `10.00/10`
- 1 BDD feature passed
- 16 BDD scenarios passed
- 124 BDD steps passed
- Successful OpenShift health check returning `{"status":"OK"}`
- A successful six-stage Tekton PipelineRun
- A GitHub webhook configured to trigger the pipeline on pushes to `master`

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Application language |
| Flask 3.1 | Web application framework |
| Flask-RESTX | REST API and Swagger documentation |
| Flask-SQLAlchemy | ORM and database integration |
| PostgreSQL / psycopg | Persistent database |
| HTML / CSS / JavaScript | Administrative UI |
| pytest | Unit testing |
| coverage.py / Codecov | Coverage measurement and reporting |
| factory-boy | Test data generation |
| Behave | BDD test runner |
| Selenium / Chrome | Browser-based UI testing |
| gunicorn | Production web server |
| pylint / flake8 | Code quality checks |
| Docker | Container image development |
| Buildah | Pipeline image builds |
| Kubernetes / K3D / K3S | Local orchestration |
| Red Hat OpenShift | Remote Kubernetes platform |
| Tekton | Continuous delivery pipeline |
| GitHub Actions | Continuous integration |
| GitHub Webhooks | Automatic CD triggering |
| ZenHub | Agile project management |

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.