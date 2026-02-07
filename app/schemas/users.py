from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr = Field(description="User's email address")
    password: str = Field(description="User's password")


class UserActivate(BaseModel):
    code: str = Field(description="Activation code sent to the user's email")

    @field_validator("code")
    def check_code_value(cls, value):
        if not value.strip():
            raise ValueError("Activation code cannot be empty")
        if len(value) != 4:
            raise ValueError("Activation code must be exactly 4 characters long")
        if not value.isdigit():
            raise ValueError("Activation code must contain only digits")
        return value


class UserResponse(BaseModel):
    email: EmailStr = Field(description="User's email address")
    status: str = Field(description="Status of the user account")
