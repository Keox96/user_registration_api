import asyncpg
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBasicCredentials

from app.core.dependencies import get_db
from app.core.security import auth_security
from app.database.users import UserRepository
from app.schemas.exceptions import ErrorResponse
from app.schemas.users import UserActivate, UserCreate, UserResponse
from app.services.users import UserService
from app.utils.smtp import EmailConsoleClient

common_responses = {
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
}

users_router = APIRouter(tags=["users"], responses=common_responses)


@users_router.post(
    "/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate, conn: asyncpg.Connection = Depends(get_db)
) -> UserResponse:
    """
    Create a new user account.

    This endpoint accepts a JSON payload with the user's email and password,
    validates the input, stores the user credentials in the database, generates
    a 4-digit activation code, and sends it to the user via email. The user account
    is created in an inactive state and must be activated using the activation code.

    Args:
        user (UserCreate): The user data to create, containing:
            - email (str): A valid, unique email address.
            - password (str): A secure password (validation requirements apply).
        conn (asyncpg.Connection): Database connection from the pool (dependency injected).

    Returns:
        UserResponse: A response model containing:
            - email (str): The created user's email address.
            - status (str): Creation status ("created").

    Raises (HTTP responses):
        - 409 Conflict: Email address already exists in the database.
        - 422 Unprocessable Content: Invalid request payload or validation failure.
        - 500 Internal Server Error: Database or email service error.
    """
    user_repository = UserRepository(conn)
    email_client = EmailConsoleClient()
    user_service = UserService(user_repository, email_client)
    user_response = await user_service.create_user(user)
    return user_response


@users_router.post(
    "/users/activate", response_model=UserResponse, status_code=status.HTTP_200_OK
)
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
        - 422 Unprocessable Content: Invalid request payload (e.g., code not 4 digits).
    """
    user_repository = UserRepository(conn)
    email_client = EmailConsoleClient()
    user_service = UserService(user_repository, email_client)
    user_response = await user_service.activate_user(user, credentials)
    return user_response
