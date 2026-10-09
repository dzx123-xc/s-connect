from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "SConnect"
    app_version: str = "1.0.0"
    debug: bool = True

    database_url: str = "sqlite:///./data/sconnect.db"

    secret_key: str = "dev-secret-key-change-in-production-min-32-chars"
    session_max_age_seconds: int = 30 * 24 * 60 * 60
    session_cookie_name: str = "session_id"
    session_cookie_secure: bool = False
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"

    cors_origins: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]

    argon2_time_cost: int = 3
    argon2_memory_cost: int = 65536
    argon2_parallelism: int = 4
    argon2_hash_len: int = 32
    argon2_salt_len: int = 16

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()