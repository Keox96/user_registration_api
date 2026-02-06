from typing import AsyncGenerator

import asyncpg

from core.config import settings


class Database:
    """
    Database connection pool manager for PostgreSQL using asyncpg.

    This class manages the lifecycle of a connection pool to the PostgreSQL database.
    It provides methods to connect, disconnect, and acquire connections from the pool.

    Attributes:
        pool (asyncpg.Pool | None): The asyncpg connection pool. None until connect() is called.
    """

    def __init__(self):
        """Initialize the Database instance with an empty connection pool."""
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        """
        Establish a connection pool to the PostgreSQL database.

        Creates an asyncpg connection pool with the configured database URL.
        The pool will maintain between 2 and 10 idle connections with a 30 second timeout.

        Raises:
            asyncpg.InvalidDSNError: If the database URL is invalid.
            asyncpg.PostgresError: If connection to the database fails.
        """
        self.pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )

    async def disconnect(self):
        """
        Close all connections in the pool.

        Safely closes the connection pool if it exists. This method should be called
        when shutting down the application.
        """
        if self.pool:
            await self.pool.close()

    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Acquire a connection from the pool as an async context manager.

        This is a generator that yields a database connection and automatically
        returns it to the pool when the context exits.

        Yields:
            asyncpg.Connection: A database connection from the pool.

        Example:
            async with db.get_connection() as conn:
                await conn.execute("SELECT * FROM users")
        """
        async with self.pool.acquire() as connection:
            yield connection


db = Database()
