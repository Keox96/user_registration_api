"""Tests for the user endpoints."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from app.core.security import hash_password
from app.utils.constants import (EXPIRED_ACTIVATION_CODE_ERROR_CODE,
                                 INVALID_ACTIVATION_CODE_ERROR_CODE,
                                 INVALID_EMAIL_ERROR_CODE,
                                 INVALID_PASSWORD_ERROR_CODE,
                                 USER_ALREADY_ACTIVATED_ERROR_CODE,
                                 USER_ALREADY_EXISTS_ERROR_CODE,
                                 USER_STATUS_ACTIVATED, USER_STATUS_CREATED,
                                 VALIDATION_ERROR_CODE)


# The following tests cover the user creation flow, including success and various error scenarios.
# Each test case is parameterized to cover different combinations of inputs and expected outcomes.
@pytest.mark.asyncio
async def test_create_user_success(test_client):
    """Test successful user creation."""
    response = await test_client.post(
        "/users",
        json={"email": "test@example.com", "password": "secure_password_123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "email" in data
    assert "status" in data
    assert data["status"] == "created"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,description,error_code",
    [
        (
            {"email": "invalid-email", "password": "secure_password_123"},
            "invalid email format",
            VALIDATION_ERROR_CODE,
        ),
        (
            {"email": "test@example.com"},
            "missing password",
            VALIDATION_ERROR_CODE,
        ),
        (
            {"password": "secure_password_123"},
            "missing email",
            VALIDATION_ERROR_CODE,
        ),
        (
            {},
            "missing both email and password",
            VALIDATION_ERROR_CODE,
        ),
        (
            {"email": "test@example.com", "password": 123},
            "missing both email and password",
            VALIDATION_ERROR_CODE,
        ),
    ],
)
async def test_create_user_validation_error(
    test_client, payload, description, error_code
):
    """Test user creation with invalid or missing fields.

    Args:
        payload: The request body with missing or invalid fields.
        description: Human-readable description of the test case.
    """
    response = await test_client.post("/users", json=payload)
    assert response.status_code == 422, f"Expected 422 for {description}"
    assert response.json()["error"]["code"] == error_code


@pytest.mark.asyncio
async def test_create_user_duplicate_email(test_client):
    """Test user creation with duplicate email."""
    # Create first user
    input_data = {"email": "duplicate@example.com", "password": "password123"}
    response1 = await test_client.post(
        "/users",
        json=input_data,
    )
    assert response1.status_code == 201
    assert response1.json()["email"] == input_data["email"]
    assert response1.json()["status"] == "created"

    # Try to create second user with same email
    input_data["password"] = (
        "password456"  # Change password to isolate email uniqueness
    )
    response2 = await test_client.post(
        "/users",
        json=input_data,
    )
    # Should fail due to unique constraint
    error_data = response2.json()
    assert response2.status_code == 409
    assert error_data["error"]["code"] == USER_ALREADY_EXISTS_ERROR_CODE


# The following tests cover the user activation flow, including success and various error scenarios.
# Each test case is parameterized to cover different combinations of inputs and expected outcomes.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email,password,code_generated,payload_code,expected_status,error_code",
    [
        # ✅ Success case: Correct code
        (
            "success@example.com",
            "password123",
            "1234",
            "1234",
            200,
            None,
        ),
        # ❌ Error case: Invalid email (user does not exist)
        (
            "nonexistent@example.com",
            "password123",
            "1234",
            "1234",
            401,
            INVALID_EMAIL_ERROR_CODE,
        ),
        # ❌ Error case: Invalid password
        (
            "wrongpass@example.com",
            "password123",
            "1234",
            "1234",
            401,
            INVALID_PASSWORD_ERROR_CODE,
        ),
        # ❌ Error case: Invalid activation code
        (
            "wrongcode@example.com",
            "password123",
            "1234",
            "5678",
            400,
            INVALID_ACTIVATION_CODE_ERROR_CODE,
        ),
        # ❌ Error case: Empty code
        (
            "emptycode@example.com",
            "password123",
            "1234",
            "",
            422,
            VALIDATION_ERROR_CODE,
        ),
        # ❌ Error case: Code not 4 digits
        (
            "badlen@example.com",
            "password123",
            "1234",
            "12",
            422,
            VALIDATION_ERROR_CODE,
        ),
        # ❌ Error case: Code with non-numeric characters
        (
            "badchar@example.com",
            "password123",
            "1234",
            "abcd",
            422,
            VALIDATION_ERROR_CODE,
        ),
    ],
)
async def test_activate_user(
    test_client,
    email,
    password,
    code_generated,
    payload_code,
    expected_status,
    error_code,
):
    """Test user activation flow with all possible scenarios.

    Args:
        test_client: Async test client.
        email: User email.
        password: User password.
        code_generated: Code generated during user creation (mocked).
        payload_code: Code provided in the activation payload.
        expected_status: Expected HTTP status code.
        error_code: Expected error code (None for success).
    """
    # Step 1: Create a new user with a mocked code
    with patch("app.services.users.UserService._generate_code") as mock_generate:
        mock_generate.return_value = code_generated

        user_payload = {"email": email, "password": password}

        if error_code == INVALID_EMAIL_ERROR_CODE:
            user_payload["email"] = "true@email.fr"
        if error_code == INVALID_PASSWORD_ERROR_CODE:
            user_payload["password"] = "truepassword"
        create_response = await test_client.post(
            "/users",
            json=user_payload,
        )
        assert create_response.status_code == 201
        created_user = create_response.json()
        assert created_user["email"] == user_payload["email"]
        assert created_user["status"] == USER_STATUS_CREATED

    # Step 2: Try to activate the user
    activate_payload = {"code": payload_code}
    activate_response = await test_client.post(
        "/users/activate",
        json=activate_payload,
        auth=(email, password),
    )

    # Verify the status code
    assert activate_response.status_code == expected_status

    response_data = activate_response.json()

    # Verify the result based on the case
    if expected_status == 200:
        # Success case
        assert response_data["email"] == email
        assert response_data["status"] == "activated"
    else:
        # Error case
        assert error_code is not None
        assert response_data["error"]["code"] == error_code


@pytest.mark.asyncio
async def test_activate_user_already_activated(test_client):
    """Test activation when user is already activated."""
    email = "already_activated@example.com"
    password = "password123"
    code = "5678"

    # Create the user with a mocked code
    with patch("app.services.users.UserService._generate_code") as mock_generate:
        mock_generate.return_value = code

        create_response = await test_client.post(
            "/users",
            json={"email": email, "password": password},
        )
        assert create_response.status_code == 201

    # First activation (success)
    first_activate = await test_client.post(
        "/users/activate",
        json={"code": code},
        auth=(email, password),
    )
    assert first_activate.status_code == 200
    assert first_activate.json()["status"] == USER_STATUS_ACTIVATED

    # Second activation attempt (error)
    second_activate = await test_client.post(
        "/users/activate",
        json={"code": code},
        auth=(email, password),
    )
    assert second_activate.status_code == 409
    assert second_activate.json()["error"]["code"] == USER_ALREADY_ACTIVATED_ERROR_CODE


@pytest.mark.asyncio
async def test_activate_user_expired_code(test_client):
    """Test activation with expired activation code."""
    email = "expired_code@example.com"
    password = "password123"
    code = "9999"

    # Créer l'utilisateur avec le code mockifié
    with patch("app.services.users.UserService._generate_code") as mock_generate:
        mock_generate.return_value = code

        create_response = await test_client.post(
            "/users",
            json={"email": email, "password": password},
        )
        assert create_response.status_code == 201

    # Wait just enough for the code to expire
    # (normally the code expires after 24h, but we can test manually
    # by modifying the timestamp in the DB, which is beyond the scope of this test)
    # For this test, we will simulate an expired code by mocking the verification

    # Mock the repository to return a user with an expired code
    expired_time = (datetime.now(timezone.utc) - timedelta(hours=2)).replace(
        tzinfo=None
    )

    with patch("app.database.users.UserRepository.get_user_by_email") as mock_get:
        user_data = {
            "id": "test-id",
            "email": email,
            "password_hash": hash_password(password),
            "is_active": False,
            "activation_code": code,
            "activation_expires_at": expired_time,
        }
        mock_get.return_value = user_data

        activate_response = await test_client.post(
            "/users/activate",
            json={"code": code},
            auth=(email, password),
        )

        assert activate_response.status_code == 400
        assert (
            activate_response.json()["error"]["code"]
            == EXPIRED_ACTIVATION_CODE_ERROR_CODE
        )
