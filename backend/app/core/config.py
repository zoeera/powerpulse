import os
from typing import List

try:
    from pydantic_settings import BaseSettings
    
    class Settings(BaseSettings):
        PROJECT_NAME: str = "PowerPulse"
        API_V1_STR: str = "/api/v1"
        
        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./powerpulse.db")
        REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
        CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
        
        JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "powerpulse_super_secret_jwt_key_change_in_prod_1234567890")
        JWT_ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
        
        STORAGE_PATH: str = os.getenv("STORAGE_PATH", "storage")
        STORAGE_SIGNING_SECRET: str = os.getenv("STORAGE_SIGNING_SECRET", "powerpulse_storage_secret_signing_key_456")
        STORAGE_URL_EXPIRES_MINUTES: int = 60
        
        MODELS_DIR: str = os.getenv("MODELS_DIR", "models")
        
        BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]
        TGSPDCL_GJS_UNITS_LIMIT: float = 200.0
        BSES_DELHI_FREE_UNITS_LIMIT: float = 200.0
        DATA_RETENTION_MONTHS: int = 24

        class Config:
            case_sensitive = True
            env_file = ".env"
            extra = "ignore"

    settings = Settings()

except ImportError:
    class SettingsFallback:
        PROJECT_NAME = "PowerPulse"
        API_V1_STR = "/api/v1"
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./powerpulse.db")
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
        CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
        JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "powerpulse_super_secret_jwt_key_change_in_prod_1234567890")
        JWT_ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
        STORAGE_PATH = os.getenv("STORAGE_PATH", "storage")
        STORAGE_SIGNING_SECRET = os.getenv("STORAGE_SIGNING_SECRET", "powerpulse_storage_secret_signing_key_456")
        STORAGE_URL_EXPIRES_MINUTES = 60
        MODELS_DIR = os.getenv("MODELS_DIR", "models")
        BACKEND_CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000", "*"]
        TGSPDCL_GJS_UNITS_LIMIT = 200.0
        BSES_DELHI_FREE_UNITS_LIMIT = 200.0
        DATA_RETENTION_MONTHS = 24

    settings = SettingsFallback()
