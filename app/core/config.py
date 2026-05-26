from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enrollment API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = ""

    JWT_SECRET_KEY: str = ""
    JWT_REFRESH_SECRET: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    RESET_CODE_EXPIRY_MINUTES: int

    M365_SMTP_HOST: str = ""
    M365_SMTP_PORT: int
    M365_EMAIL: str = ""
    M365_APP_PASSWORD: str = ""
    POSTMARK_SERVER_TOKEN: str = ""
    POSTMARK_FROM_EMAIL: str = ""


    DATABASE_URL_ASYNC: str = ""
    DATABASE_URL: str = ""


    #Pydantic Version 2 Settings Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()