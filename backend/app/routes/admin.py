from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.services.admin_service import create_admin_user
from app.schemas.auth import RegisterRequest
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/create-admin")
def create_admin(
    data: RegisterRequest,
    db: DBSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Create a new admin user. Only callable by an existing admin."""
    if data.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'admin'",
        )

    existing_email = db.execute(
        select(User).where(User.email == data.email.lower())
    ).scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_username = db.execute(
        select(User).where(User.username == data.username.lower())
    ).scalar_one_or_none()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    existing_phone = db.execute(
        select(User).where(User.phone == data.phone)
    ).scalar_one_or_none()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )

    admin = create_admin_user(
        db,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        username=data.username,
        phone=data.phone,
    )

    return {
        "message": "Admin created",
        "user": {
            "id": admin.id,
            "email": admin.email,
            "username": admin.username,
            "full_name": admin.full_name,
            "role": admin.role,
            "is_active": admin.is_active,
        },
    }