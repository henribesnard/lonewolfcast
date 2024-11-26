from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import os
from typing import ClassVar, Dict

# Chemin de base
BASE_DIR = Path(__file__).parent.parent.parent
print(f"\nConfig Initialization:")
print(f"===============================")
print(f"Config BASE_DIR: {BASE_DIR}")

# Créer le dossier data s'il n'existe pas
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    # Database
    DB_URL: str = f"sqlite+aiosqlite:///{DATA_DIR}/football.db"
    DB_ECHO: bool = False
    
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
        return self.DB_URL
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self.DB_URL
    
    @property
    def engine_kwargs(self) -> dict:
        return {
            "echo": self.DB_ECHO,
            "connect_args": {"check_same_thread": False}
        }
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()