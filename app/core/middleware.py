"""Application middleware for error handling and request/response logging."""

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

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
        # Log incoming request
        logger.info(
            f"→ {request.method} {request.url.path} "
            f"| Remote: {request.client.host if request.client else 'unknown'} "
            f"| JSON Body: {await request.json() if request.method in ['POST', 'PUT', 'PATCH'] else 'None'}"
        )

        try:
            response = await call_next(request)

            # Log successful response
            logger.info(
                f"← {request.method} {request.url.path} "
                f"| Status: {response.status_code} "
                f"| Reponse: {response.body.decode() if hasattr(response, 'body') else 'None'}"
            )
            return response
        except Exception as exc:
            # Log the full exception for debugging
            logger.error(
                f"✗ {request.method} {request.url.path} "
                f"| Exception: {type(exc).__name__}: {str(exc)} ",
                exc_info=True,
            )
            # Return a clean error response to the client
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": f"[{type(exc).__name__}] - An internal error occurred. Please try again later.",
                    }
                },
            )
