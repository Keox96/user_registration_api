from app.utils.constants import USER_ALREADY_EXISTS_ERROR_CODE
from app.utils.exceptions import APIException


class UserAlreadyExists(APIException):
    def __init__(self, email: str):
        super().__init__(
            code=USER_ALREADY_EXISTS_ERROR_CODE,
            message="A user with this email already exists",
            status_code=409,
            details={"email": email},
        )
