"""
Secure admin creation mechanism.

Admin users are NOT registerable through the public registration endpoint.
This module provides a separate, explicit creation path used only during
development or by an already-authenticated admin bootstrap process.

Admin credentials are NEVER hardcoded in frontend code.
"""
import os
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.user import User
from app.auth.password import hash_password


def create_admin_user(
    db: DBSession,
    email: str,
    password: str,
    full_name: str,
    username: Optional[str] = None,
    phone: Optional[str] = None,
) -> User:
    """Create an admin user. Intentional, explicit operation."""
    username = username or email.split("@")[0]
    phone = phone or "+910000000000"

    existing = db.query(User).filter(User.email == email.lower()).first()
    if existing:
        raise ValueError(f"User with email {email} already exists")

    existing_username = db.query(User).filter(User.username == username.lower()).first()
    if existing_username:
        raise ValueError(f"Username {username} already taken")

    existing_phone = db.query(User).filter(User.phone == phone).first()
    if existing_phone:
        raise ValueError(f"Phone {phone} already registered")

    admin = User(
        email=email.lower(),
        username=username.lower(),
        phone=phone,
        full_name=full_name,
        password_hash=hash_password(password),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.flush()
    return admin


def bootstrap_admin_from_env(db: DBSession) -> Optional[User]:
    """Create an admin from environment variables if configured.

    Only activates when SCONNECT_ADMIN_EMAIL and SCONNECT_ADMIN_PASSWORD are set.
    Returns None if no admin env vars are configured.
    """
    email = os.environ.get("SCONNECT_ADMIN_EMAIL")
    password = os.environ.get("SCONNECT_ADMIN_PASSWORD")
    if not email or not password:
        return None

    full_name = os.environ.get("SCONNECT_ADMIN_FULL_NAME", "System Administrator")
    username = os.environ.get("SCONNECT_ADMIN_USERNAME")
    phone = os.environ.get("SCONNECT_ADMIN_PHONE")

    return create_admin_user(
        db,
        email=email,
        password=password,
        full_name=full_name,
        username=username,
        phone=phone,
    )


__all__ = ["create_admin_user", "bootstrap_admin_from_env"]