"""Application middleware for error handling and request/response logging."""

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that catches unhandled exceptions and returns a clean error response.

    When a 500 error occurs (unhandled exception), instead of exposing the full
    traceback to the client, this middleware returns a clean JSON response with
    a generic message. The full exception details are logged for debugging.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and handle any unhandled exceptions.

        Args:
            request (Request): The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            Response: The response from the handler or a clean error response.
        """
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log the full exception for debugging
            logger.error(
                f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
                exc_info=True,
            )
            # Return a clean error response to the client
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": f"[{type(exc).__name__}] - An internal error occurred. Please try again later.",
                    }
                },
            )
