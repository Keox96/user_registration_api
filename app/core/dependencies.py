from app.database.pool import db


async def get_db():
    """
    Dependency function to provide a database connection.

    This function is designed to be used as a FastAPI dependency. It acquires a
    connection from the database pool and yields it for use in request handlers.
    After the request is processed, the connection is automatically returned to the pool.

    Yields:
        asyncpg.Connection: A database connection from the pool.

    Example usage in a FastAPI route:
        @app.get("/users")
        async def read_users(conn: asyncpg.Connection = Depends(get_db)):
            # Use conn to execute database queries
            ...
    """
    async with db.get_connection() as conn:
        yield conn
