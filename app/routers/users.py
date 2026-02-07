import asyncpg
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials

from app.core.dependencies import get_db
from app.core.security import auth_security
from app.database.users import UserRepository
from app.schemas.users import UserActivate, UserCreate, UserResponse
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


@users_router.post("/users/activate", response_model=UserResponse, status_code=200)
async def activate_user(
    user: UserActivate,
    conn: asyncpg.Connection = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(auth_security),
) -> UserResponse:
    """
    Activate a user account with an activation code.

    This endpoint requires HTTP Basic authentication (email and password) and accepts
    a JSON payload containing a 4-digit activation code. The endpoint validates the
    provided credentials, verifies that the activation code matches the one stored
    in the database, checks that the code hasn't expired, and marks the user account
    as active if all validations pass.

    Security:
        - Requires HTTP Basic authentication with email and password.
        - User password must match the stored password hash.

    Args:
        user (UserActivate): The activation data containing the activation code.
            Code must be exactly 4 digits (e.g., "1234").
        conn (asyncpg.Connection): Database connection from the pool (dependency injected).
        credentials (HTTPBasicCredentials): HTTP Basic authentication credentials
            containing email and password (dependency injected).

    Returns:
        UserResponse: A response model containing the user's email and activation status.
            Status will be "activated" on successful activation.

    Raises (HTTP responses):
        - 401 Unauthorized: Invalid email or password provided in authentication.
        - 400 Bad Request: Invalid or expired activation code.
        - 409 Conflict: User account is already activated.
        - 422 Unprocessable Entity: Invalid request payload (e.g., code not 4 digits).
    """
    user_repository = UserRepository(conn)
    email_client = EmailConsoleClient()
    user_service = UserService(user_repository, email_client)
    user_response = await user_service.activate_user(user, credentials)
    return user_response
