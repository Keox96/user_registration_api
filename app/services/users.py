import random

from app.core.security import hash_password
from app.database.users import UserRepository
from app.schemas.users import UserCreate, UserResponse
from app.utils.constants import USER_STATUS_CREATED
from app.utils.exceptions.users import UserAlreadyExists
from app.utils.smtp import EmailClient


class UserService:
    def __init__(self, user_repository: UserRepository, email_client: EmailClient):
        self.user_repository = user_repository
        self.email_client = email_client

    def _generate_code(self) -> str:
        return f"{random.randint(0, 9999):04d}"

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
