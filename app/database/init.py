"""Database initialization and schema setup."""

from app.database.pool import db


async def init_db():
    """
    Initialize database tables.

    Creates the users table if it doesn't exist. The created_at field will
    automatically be set to the current UTC timestamp when a row is inserted.
    """
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
    async with db.pool.acquire() as connection:
        await connection.execute(query)
