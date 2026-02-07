from app.utils.constants import (EXPIRED_ACTIVATION_CODE_ERROR_CODE,
                                 INVALID_ACTIVATION_CODE_ERROR_CODE,
                                 USER_ALREADY_ACTIVATED_ERROR_CODE,
                                 USER_ALREADY_EXISTS_ERROR_CODE)
from app.utils.exceptions import APIException


class UserAlreadyExists(APIException):
    def __init__(self, email: str):
        super().__init__(
            code=USER_ALREADY_EXISTS_ERROR_CODE,
            message="A user with this email already exists",
            status_code=409,
            details={"email": email},
        )


class UserAlreadyActivated(APIException):
    def __init__(self, email: str):
        super().__init__(
            code=USER_ALREADY_ACTIVATED_ERROR_CODE,
            message="This user account is already activated",
            status_code=409,
            details={"email": email},
        )


class InvalidActivationCode(APIException):
    def __init__(self, code: str):
        super().__init__(
            code=INVALID_ACTIVATION_CODE_ERROR_CODE,
            message="The provided activation code is invalid",
            status_code=400,
            details={"code": code},
        )


class ExpiredActivationCode(APIException):
    def __init__(self, code: str):
        super().__init__(
            code=EXPIRED_ACTIVATION_CODE_ERROR_CODE,
            message="The provided activation code has expired",
            status_code=400,
            details={"code": code},
        )
