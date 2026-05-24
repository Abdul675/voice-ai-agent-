# backend/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Vapi
    VAPI_API_KEY: str
    VAPI_ASSISTANT_ID: str
    VAPI_PHONE_NUMBER_ID: str

    # Database — swap sqlite → postgres by changing this one line
    DATABASE_URL: str = "sqlite:///./voice_agent.db"

    class Config:
        env_file = ".env"


settings = Settings()