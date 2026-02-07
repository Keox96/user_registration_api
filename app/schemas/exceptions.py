from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class APIError(BaseModel):
    code: str = Field(description="A unique error code identifying the type of error")
    message: str = Field(description="A human-readable message describing the error")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional additional details about the error"
    )


class ErrorResponse(BaseModel):
    error: APIError = Field(description="The error information")
