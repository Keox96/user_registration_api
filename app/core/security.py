from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash the provided password using argon2 via Passlib.
    """
    return pwd_context.hash(password)
