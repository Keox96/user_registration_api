from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.pool import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    This async context manager is passed to FastAPI as the `lifespan` hook.
    On startup it establishes connections/resources required by the application
    (currently it opens the database connection pool via `db.connect()`).
    On shutdown it must cleanly release those resources (closing the pool with
    `db.disconnect()`).

    Args:
        app (FastAPI): The application instance the lifespan is attached to.

    Yields:
        None: Control is yielded back to FastAPI to run the application.

    Notes:
        Ensure the `db` object implements `connect()` and `disconnect()` methods
        (see `database.pool.Database`). Any exceptions raised during startup
        will prevent the application from starting.
    """
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)
