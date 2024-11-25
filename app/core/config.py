from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import ssl
import os
from typing import Optional, Dict, ClassVar

# Chemin de base
BASE_DIR = Path(__file__).parent.parent.parent
print(f"\nConfig Initialization:")
print(f"===============================")
print(f"Config BASE_DIR: {BASE_DIR}")
CA_PATH = BASE_DIR / "ca.pem"

class Settings(BaseSettings):
    # Database
    DB_URL: str
    DB_SSL_MODE: str = "require"
    DB_CA_PATH: Path = CA_PATH
    
    # API Football
    API_KEY: str
    API_BASE_URL: str
    
    # App
    APP_NAME: str = "LoneWolfCast"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Admin
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    
    # Templates & Static
    TEMPLATES_DIR: str = str(BASE_DIR / "app" / "admin" / "templates")
    STATIC_DIR: str = str(BASE_DIR / "app" / "admin" / "static")
    TEMPLATE_CONFIG: ClassVar[Dict] = {
        "TEMPLATES_DIR": str(BASE_DIR / "app" / "admin" / "templates"),
        "RELOAD": True,
        "AUTOESCAPE": True,
        "AUTO_RELOAD": True
    }
    
    # Database Pool
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False
    
    # API Settings
    API_RATE_LIMIT: int = 450
    API_TIMEOUT: int = 30
    API_MAX_CALLS_PER_DAY: int = 75000
    
    # Cache
    CACHE_TTL: int = 3600
    CACHE_PREFIX: str = "lwc"
    
    # Analysis
    MIN_MATCHES_REQUIRED: int = 5
    FORM_WINDOW: int = 5
    H2H_WINDOW: int = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"\nSettings Paths Verification:")
        print(f"===============================")
        print(f"TEMPLATES_DIR: {self.TEMPLATES_DIR}")
        print(f"Templates exists: {os.path.exists(self.TEMPLATES_DIR)}")
        print(f"STATIC_DIR: {self.STATIC_DIR}")
        print(f"Static exists: {os.path.exists(self.STATIC_DIR)}")

    @property
    def DATABASE_URL(self) -> str:
        return self.DB_URL.replace("postgres://", "postgresql://")
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        from urllib.parse import urlparse
        parsed = urlparse(self.DB_URL)
        return f"postgresql+asyncpg://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"
    
    def get_ssl_context(self) -> ssl.SSLContext:
        if not self.DB_CA_PATH.exists():
            raise FileNotFoundError(f"CA certificate not found at {self.DB_CA_PATH}")
        
        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=str(self.DB_CA_PATH)
        )
        return ssl_context

    @property
    def engine_kwargs(self) -> dict:
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "echo": self.DB_ECHO
        }
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()