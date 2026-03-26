from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # API
    api_title: str = "CaribAPI"
    api_version: str = "1.0.0"
    api_description: str = "Caribbean Business Data API"
    contact_email: str = "contact@caribapi.com"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/caribapi")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Stripe
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_price_pro: str = os.getenv("STRIPE_PRICE_PRO", "")
    stripe_price_business: str = os.getenv("STRIPE_PRICE_BUSINESS", "")
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    # Rate Limiting
    rate_limit_free: int = int(os.getenv("RATE_LIMIT_FREE", "100"))
    rate_limit_pro: int = int(os.getenv("RATE_LIMIT_PRO", "10000"))
    rate_limit_business: int = int(os.getenv("RATE_LIMIT_BUSINESS", "100000"))
    
    # Data
    data_update_frequency_hours: int = 24  # Update data daily
    
    class Config:
        env_file = ".env"

settings = Settings()