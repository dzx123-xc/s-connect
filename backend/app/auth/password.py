import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.config import settings


ph = PasswordHasher(
    time_cost=settings.argon2_time_cost,
    memory_cost=settings.argon2_memory_cost,
    parallelism=settings.argon2_parallelism,
    hash_len=settings.argon2_hash_len,
    salt_len=settings.argon2_salt_len,
)


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def generate_session_id() -> str:
    return secrets.token_urlsafe(32)


def hash_session_id(session_id: str) -> str:
    return hashlib.sha256(session_id.encode()).hexdigest()


def create_session_expiry() -> datetime:
    return datetime.utcnow() + timedelta(seconds=settings.session_max_age_seconds)


def is_session_expired(expires_at: datetime) -> bool:
    return datetime.utcnow() > expires_at


def is_session_revoked(revoked_at: Optional[datetime]) -> bool:
    return revoked_at is not None