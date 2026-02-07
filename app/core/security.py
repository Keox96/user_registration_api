from fastapi.security import HTTPBasic
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
auth_security = HTTPBasic()


def hash_password(password: str) -> str:
    """
    Hash the provided password using argon2 via Passlib.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)
