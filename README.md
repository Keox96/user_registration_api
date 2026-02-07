# User Registration API

A FastAPI-based user registration and account activation service with email verification. This API handles user registration, account creation, and email-based activation flows.

## Features

- **User Registration**: Create new user accounts with email and password validation
- **Email Verification**: Send 4-digit activation codes via email for account verification
- **Account Activation**: Activate user accounts using the verification code and HTTP Basic authentication
- **Async Foundation**: Built on FastAPI with async/await patterns for high performance
- **PostgreSQL Integration**: Async database operations using asyncpg connection pooling
- **Security**: Password hashing with Argon2, HTTP Basic authentication support
- **Pydantic v2**: Modern schema validation and configuration

## Tech Stack

- **Framework**: FastAPI (>=0.128.2)
- **Database**: PostgreSQL with asyncpg (>=0.31.0)
- **Validation**: Pydantic v2 with pydantic-settings
- **Security**: Passlib with Argon2 (>=1.7.4)
- **Testing**: pytest with pytest-asyncio (>=1.3.0)
- **Containerization**: Docker & Docker Compose

## Project Structure

```
app/
├── core/
│   ├── config.py           # Settings and environment configuration
│   ├── dependencies.py     # Dependency injection setup
│   ├── middleware.py       # Custom middleware
│   └── security.py         # Security utilities (hashing, auth)
├── database/
│   ├── init.py            # Database initialization
│   ├── pool.py            # Connection pooling setup
│   └── users.py           # User data access layer
├── routers/
│   └── users.py           # User API endpoints
├── schemas/
│   ├── users.py           # User data models
│   └── exceptions.py      # Exception models
├── services/
│   └── users.py           # Business logic
└── utils/
    ├── constants.py       # Application constants
    ├── exceptions/        # Custom exceptions
    └── smtp/              # Email service clients
```

## Software Architecture

The API follows a layered, modular architecture separating concerns into
clear responsibilities. This organization improves testability, maintainability,
and allows independent evolution of components.

- Presentation (API layer) - `app/routers`
   - FastAPI routers expose HTTP endpoints and handle request/response mapping.

- Application / Service layer - `app/services`
   - Implements business logic and orchestrates repository and external client calls.
   - Validates flows such as user creation, activation, and email delivery.

- Domain / Schema layer - `app/schemas`
   - Pydantic models and DTOs used across the application for validation and
      serialization.

- Infrastructure layer - `app/database`, `app/utils/smtp`
   - Database access (repositories) and connection pooling live here.
   - Email clients and any external integrations are implemented in `utils.smtp`.

- Cross-cutting / Core - `app/core`
   - Configuration, dependency injection, security helpers (hashing, auth), and
      middleware for logging/error handling.

Data flow (simplified):
1. A client sends a request to a router in `app/routers`.
2. The router validates input with Pydantic models from `app/schemas` and
    calls a service in `app/services`.
3. The service performs business rules and interacts with repositories in
    `app/database` and clients in `app/utils/smtp`.
4. Services return domain objects or DTOs which routers serialize into HTTP
    responses.

This separation allows swapping implementations (for example replacing the
console email client with an SMTP client or adding Alembic migrations for the
database) without changing higher-level business logic.

## Architecture Schema

Below is a high-level architecture diagram (Mermaid) illustrating the main
components and their interactions. You can paste this into a Mermaid viewer
or GitHub README to render it visually.

```mermaid
flowchart TB
  Client["Client (HTTP)"]
  subgraph API[API Layer]
    Router["FastAPI routers\n(app/routers)"]
    Middleware["Middleware\n(app/core/middleware.py)"]
  end
  Service["Services\n(app/services)"]
  Schemas["Schemas\n(app/schemas)"]
  Repo["Repositories\n(app/database)"]
  DB["PostgreSQL"]
  SMTP["Email Client\n(app/utils/smtp)"]
  Config["Config & DI\n(app/core/config.py)"]

  Client --> Router
  Router --> Middleware
  Middleware --> Router
  Router --> Service
  Router --> Schemas
  Service --> Repo
  Service --> SMTP
  Repo --> DB
  Router --> Config
  Service --> Config
```

This diagram shows: the HTTP client hitting FastAPI routers which are guarded
and enriched by middleware; routers call services that encapsulate business
rules; services call repositories to access the database and email clients to
send messages; configuration and dependency wiring are provided by the core
module.

## Getting Started

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker Compose)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd user_registration_api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On Unix/macOS:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -e .
   ```

5. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/user_registration
   ```

### Running the Application

**Option 1: Using Docker Compose (Recommended)**

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

**Option 2: Running Locally**

1. Ensure PostgreSQL is running and accessible
2. Initialize the database:
   ```bash
   python -c "from app.database.init import init_db; asyncio.run(init_db())"
   ```
3. Start the development server:
   ```bash
   fastapi dev main.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### Create User
```http
POST /users
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "email": "user@example.com",
  "status": "created"
}
```

#### Activate User
```http
POST /users/activate
Authorization: Basic base64(email:password)
Content-Type: application/json

{
  "code": "1234"
}
```

**Response (200 OK):**
```json
{
  "email": "user@example.com",
  "status": "activated"
}
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_users.py -v
```

### Run with coverage
```bash
pytest --cov=app tests/
```

**Note:** Tests use a test database configured in `tests/conftest.py`. Ensure PostgreSQL is running before executing tests.

## Future Improvements

### 1. **Password Strength Requirements**
- Enforce minimum length (12+ characters)
- Require uppercase and lowercase letters
- Require numbers and special characters
- Implement password strength meter in response
- Add password history to prevent reuse

### 2. **OAuth2.0 Authentication**
- Replace HTTP Basic Auth with OAuth2.0 with password flow
- Support JWT tokens for stateless authentication
- Implement token refresh mechanism
- Add support for third-party OAuth providers (Google, GitHub, etc.)
- Implement role-based access control (RBAC)

### 3. **Code Regeneration Endpoint**
- Create `POST /users/{email}/regenerate-code` endpoint
- Add rate limiting to prevent abuse (e.g., 3 requests per hour)
- Invalidate previous activation codes when generating new ones
- Send regenerated code via email

### 4. **Database Schema Management with Alembic**
- Initialize Alembic for version control of database schema
- Create migration system for database changes
- Add automatic migration running on application startup
- Document migration procedures
- Enable rollback capabilities for failed deployments

### 5. **SMTP Email Service Implementation**
- Create `SMTPClient` class inheriting from abstract `EmailClient`
- Configure SMTP server credentials (Gmail, SendGrid, AWS SES, etc.)
- Implement proper error handling and retry logic
- Add email templates for registration and activation emails
- Support HTML and plain text emails
- Implement logging for email sending operations
- Add email sending in background tasks using Celery or similar

### 6. **Additional Improvements**
- Improve request/response logging middleware
- Implement rate limiting on endpoints
- Add input sanitization and validation
- Create comprehensive API documentation
- Add API versioning
- Implement database transactions
- Add health check endpoint
- Implement graceful shutdown handling

## Development

### Code Style
The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **Pylint** for linting

Format code before committing:
```bash
black app/ tests/
isort app/ tests/
```

### Dependencies Management
This project uses Poetry for dependency management. Update dependencies with:
```bash
poetry add [package-name]
poetry update
```
