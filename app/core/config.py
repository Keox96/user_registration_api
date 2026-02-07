from pydantic import Field
from pydantic_settings import BaseSettings

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@db:5432/user_registration"


class Settings(BaseSettings):
    database_url: str = Field(DEFAULT_DATABASE_URL, env="DATABASE_URL")

    class Config:
        env_file = ".env"  # optional
        case_sensitive = True


settings = Settings()
