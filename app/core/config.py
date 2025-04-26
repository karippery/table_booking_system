from pydantic_settings import BaseSettings  # type: ignore
from pydantic import Field


class PaginationSettings(BaseSettings):
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class ConfigDict:
        env_prefix = "PAGINATION_"  # Reads PAGINATION_* from .env


pagination_settings = PaginationSettings()


class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = Field(
        default=(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
        ),
        description="Database connection URL"
    )
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="postgres")

    # Application Configuration
    SECRET_KEY: str = Field(
        default="eI_RVdetwcVhSazxZskgtx6nzLW63InWz7k7_AifqrU",
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    PASSWORD_MIN_LENGTH: int = Field(default=8)

    # Pagination
    PAGINATION_DEFAULT_PAGE_SIZE: int = Field(default=25)
    PAGINATION_MAX_PAGE_SIZE: int = Field(default=100)

    # Booking Defaults
    DEFAULT_DURATION: int = Field(
        default=4,
        description="Default booking duration in hours"
        )

    class ConfigDict:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
        # This will ignore extra env vars instead of raising errors


settings = Settings()
