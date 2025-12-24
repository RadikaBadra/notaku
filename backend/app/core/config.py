from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_DB: str

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra env vars like GEMINI_API_KEY without defining them

settings = Settings()
