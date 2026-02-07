import random
from datetime import datetime, timezone

from fastapi.security import HTTPBasicCredentials

from app.core.security import hash_password, verify_password
from app.database.users import UserRepository
from app.schemas.users import UserActivate, UserCreate, UserResponse
from app.utils.constants import USER_STATUS_ACTIVATED, USER_STATUS_CREATED
from app.utils.exceptions.authentication import InvalidEmail, InvalidPassword
from app.utils.exceptions.users import (ExpiredActivationCode,
                                        InvalidActivationCode,
                                        UserAlreadyActivated,
                                        UserAlreadyExists)
from app.utils.smtp import EmailClient


class UserService:
    def __init__(self, user_repository: UserRepository, email_client: EmailClient):
        self.user_repository = user_repository
        self.email_client = email_client

    # Private method to generate a 4-digit activation code
    def _generate_code(self) -> str:
        return f"{random.randint(0, 9999):04d}"

    # Public method to create a new user account
    async def create_user(self, user: UserCreate) -> UserResponse:
        if await self.user_repository.get_user_by_email(user.email):
            raise UserAlreadyExists(email=user.email)

        # Hash the password
        password_hash = hash_password(user.password)
        # Generate a unique code for the user
        code = self._generate_code()
        # Create the user in the database
        created_user_email = await self.user_repository.create_user(
            user.email, password_hash, code
        )
        # Send a verification email to the user
        await self.email_client.send_verification_email(created_user_email, code)
        return UserResponse(email=created_user_email, status=USER_STATUS_CREATED)

    # Public method to activate a user account using the provided activation code and credentials
    async def activate_user(
        self, user: UserActivate, credentials: HTTPBasicCredentials
    ) -> UserResponse:
        user_db = await self.user_repository.get_user_by_email(credentials.username)
        # Check if the user exists in the database
        if not user_db:
            raise InvalidEmail(details={"email": credentials.username})
        # Verify the provided password against the stored password hash
        if not verify_password(credentials.password, user_db["password_hash"]):
            raise InvalidPassword(details={"email": credentials.username})
        # Check if the user is already activated
        if user_db["is_active"]:
            raise UserAlreadyActivated(email=credentials.username)
        # Check if the provided activation code matches the one stored in the database
        if user_db["activation_code"] != user.code:
            raise InvalidActivationCode(user.code)
        # Check if the activation code has expired
        if user_db["activation_expires_at"] < (datetime.now(timezone.utc)).replace(
            tzinfo=None
        ):
            raise ExpiredActivationCode(user.code)

        # Activate the user account in the database
        await self.user_repository.activate_user(user_db["id"])
        return UserResponse(email=user_db["email"], status=USER_STATUS_ACTIVATED)
