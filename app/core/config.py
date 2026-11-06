
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enrollment API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str | None = None
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    JWT_SECRET_KEY: str = ""
    JWT_REFRESH_SECRET: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_CODE_EXPIRY_MINUTES: int = 15
    REDIS_BROKER: str = ""
    REDIS_BACKEND: str = ""
    SENTRY_DSN: str = ""

    M365_SMTP_HOST: str = ""
    M365_SMTP_PORT: int = 587
    M365_EMAIL: str = ""
    M365_APP_PASSWORD: str = ""


    # Resend email provider
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "noreply@ribbletrade.uk"
    SEND_EMAILS: bool = False


    DATABASE_URL_ASYNC: str = ""
    DATABASE_URL: str = ""


    #Pydantic Version 2 Settings Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()