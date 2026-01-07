import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = "sqlite:///./referral.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "Referral & Rewards API"
    DEBUG: bool = True

settings = Settings()
