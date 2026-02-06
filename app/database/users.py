import uuid
from datetime import datetime, timedelta, timezone


class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    async def create_user(self, email: str, password_hash: str, code: str) -> str:
        user_id = uuid.uuid4()
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=1)).replace(
            tzinfo=None
        )
        query = """
            INSERT INTO users (
                id, email, password_hash, activation_code, activation_expires_at, is_active
            )
            VALUES ($1, $2, $3, $4, $5, false)
        """

        await self.conn.execute(
            query,
            user_id,
            email,
            password_hash,
            code,
            expires_at,
        )
        return email

    async def get_user_by_email(self, email: str):
        query = "SELECT * FROM users WHERE email = $1"
        return await self.conn.fetchrow(query, email)
