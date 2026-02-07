import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.middleware import ErrorHandlingMiddleware
from app.database.init import init_db
from app.database.pool import db
from app.routers.users import users_router
from app.utils.constants import VALIDATION_ERROR_CODE
from app.utils.exceptions import APIException

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    This async context manager is passed to FastAPI as the `lifespan` hook.
    On startup it establishes connections/resources required by the application
    (currently it opens the database connection pool via `db.connect()` and
    initializes the database schema with `init_db()`).
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
    await init_db()
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(ErrorHandlingMiddleware)
app.include_router(users_router)


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Sanitize errors to ensure they are JSON serializable
    sanitized_errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type"),
        }
        sanitized_errors.append(error_dict)

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": VALIDATION_ERROR_CODE,
                "message": "Invalid request payload",
                "details": sanitized_errors,
            }
        },
    )
