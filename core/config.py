from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        "postgresql://postgres:postgres@db:5432/user_registration", env="DATABASE_URL"
    )

    class Config:
        env_file = ".env"  # optionnel
        case_sensitive = True


settings = Settings()
