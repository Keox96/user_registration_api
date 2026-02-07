from fastapi import status

from app.utils.constants import (INVALID_EMAIL_ERROR_CODE,
                                 INVALID_PASSWORD_ERROR_CODE)
from app.utils.exceptions import APIException


class InvalidPassword(APIException):
    def __init__(self, details: dict):
        super().__init__(
            code=INVALID_PASSWORD_ERROR_CODE,
            message="The provided password is incorrect",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class InvalidEmail(APIException):
    def __init__(self, details: dict):
        super().__init__(
            code=INVALID_EMAIL_ERROR_CODE,
            message="The provided email address is not found",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )
