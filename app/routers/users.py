import asyncpg
from fastapi import APIRouter, Depends

from app.core.dependencies import get_db
from app.database.users import UserRepository
from app.schemas.users import UserCreate, UserResponse
from app.services.users import UserService
from app.utils.smtp import EmailConsoleClient

users_router = APIRouter(tags=["users"])


@users_router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate, conn: asyncpg.Connection = Depends(get_db)
) -> UserResponse:
    """
    Create a new user.

    This endpoint accepts a JSON payload with the user's email and password,
    creates a new user in the database, and returns a response containing the
    user's email and a status message.

    Args:
        user (UserCreate): The user data to create, including email and password.

    Returns:
        UserResponse: A response model containing the user's email and status.
    """
    user_repository = UserRepository(conn)
    email_client = EmailConsoleClient()
    user_service = UserService(user_repository, email_client)
    user_response = await user_service.create_user(user)
    return user_response
