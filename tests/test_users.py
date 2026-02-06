"""Tests for the user endpoints."""

import pytest

from app.utils.constants import (
    USER_ALREADY_EXISTS_ERROR_CODE,
    VALIDATION_ERROR_CODE
    )


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
