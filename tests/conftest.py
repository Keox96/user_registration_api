"""Pytest configuration and fixtures for testing."""

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.dependencies import get_db
from main import app


@pytest_asyncio.fixture
async def test_db_pool():
    """Create a test database and pool, yield it, then clean up."""
    base_url = settings.database_url.rsplit("/", 1)[0]  # Get base URL without DB name
    # Use a separate test database
    test_database_name = "user_registration_test"
    test_db_url = base_url + "/" + test_database_name

    # Connect to postgres (system DB) to create/drop the test DB
    postgres_system_url = base_url + "/postgres"
    postgres_conn = await asyncpg.connect(postgres_system_url)

    try:
        # Drop the test database if it exists
        await postgres_conn.execute(f"DROP DATABASE IF EXISTS {test_database_name}")
        # Create the test database
        await postgres_conn.execute(f"CREATE DATABASE {test_database_name}")
    finally:
        await postgres_conn.close()

    # Create connection pool to test database
    pool = await asyncpg.create_pool(
        dsn=test_db_url,
        min_size=1,
        max_size=10,
        command_timeout=30,
    )

    # Initialize schema in test database
    async with pool.acquire() as conn:
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN DEFAULT FALSE,
            activation_code CHAR(4),
            activation_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT now()
        );
        """
        await conn.execute(query)

    yield pool

    # Cleanup: close pool and drop test database
    await pool.close()

    postgres_conn = await asyncpg.connect(postgres_system_url)
    try:
        await postgres_conn.execute(f"DROP DATABASE IF EXISTS {test_database_name}")
    finally:
        await postgres_conn.close()


@pytest_asyncio.fixture
async def test_client(test_db_pool):
    """Provide a test client with overridden database dependency."""

    async def override_get_db():
        """Override get_db to use test pool and wrap in transaction."""
        async with test_db_pool.acquire() as conn:
            # Start a transaction
            async with conn.transaction():
                yield conn

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()
