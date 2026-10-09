from typing import Optional
from fastapi import Depends, HTTPException, status, Request

from app.auth.session import get_current_user, get_current_user_optional
from app.models.user import User


def require_role(*allowed_roles: str):
    def dependency(request: Request) -> User:
        user = get_current_user_optional(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not authorized. Required: {allowed_roles}",
            )
        return user
    return dependency


def require_admin(request: Request) -> User:
    user = get_current_user_optional(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def require_ownership(resource_user_id: int):
    def dependency(request: Request) -> User:
        user = get_current_user(request)
        if user.id != resource_user_id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource",
            )
        return user
    return dependency