from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # OTP Settings
    OTP_EXPIRE_MINUTES: int = 5
    MAX_OTP_RETRIES: int = 3

    # SMTP Settings (Gmail with App Password)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
