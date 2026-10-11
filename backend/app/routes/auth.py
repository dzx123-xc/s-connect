from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select
from app.models.user import User

from app.database import get_db
from app.services.auth_service import (
    create_user_with_profile,
    create_session,
    verify_user_password,
    revoke_session,
    get_public_profile,
)
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, MeResponse, PUBLIC_ROLES
from app.schemas.user import ProfileResponse
from app.auth.dependencies import require_role

router = APIRouter(prefix="/auth", tags=["auth"])

PUBLIC_DASHBOARD_ROUTES = {
    "player": "/player-dashboard.html",
    "coach": "/coach-dashboard.html",
    "club": "/club-dashboard.html",
    "organizer": "/organizer-dashboard.html",
    "referee": "/referee-dashboard.html",
    "admin": "/admin-portal.html",
}


def _build_profile_response(user: User) -> Optional[ProfileResponse]:
    profile_obj = get_public_profile(user)
    if profile_obj is None:
        return None
    attr_name = profile_obj.__class__.__name__.lower().replace("profile", "_profile")
    return ProfileResponse.model_validate({"user": user, attr_name: profile_obj})


def _set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
        path="/",
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, response: Response, db: DBSession = Depends(get_db)):
    if data.role not in PUBLIC_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin registration is not allowed through public registration",
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

    user = create_user_with_profile(db, data)
    session_id = create_session(db, user.id)
    _set_session_cookie(response, session_id)

    return AuthResponse(
        user=user,
        profile=_build_profile_response(user),
        role=user.role,
        redirect_url=PUBLIC_DASHBOARD_ROUTES.get(user.role, "/discover.html"),
    )


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, response: Response, db: DBSession = Depends(get_db)):
    identifier = data.identifier or data.email or data.username or data.phone
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide email, username, or phone",
        )

    user = verify_user_password(db, identifier, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    session_id = create_session(db, user.id)
    _set_session_cookie(response, session_id)

    return AuthResponse(
        user=user,
        profile=_build_profile_response(user),
        role=user.role,
        redirect_url=PUBLIC_DASHBOARD_ROUTES.get(user.role, "/discover.html"),
    )


@router.post("/logout")
def logout(request: Request, response: Response, db: DBSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if session_id:
        revoke_session(db, session_id)

    response.delete_cookie(key="session_id", path="/", httponly=True, secure=False, samesite="lax")
    return {"message": "Logged out"}


@router.get("/me", response_model=MeResponse)
def me(request: Request, user=Depends(require_role(*PUBLIC_ROLES, "admin"))):
    profile_obj = get_public_profile(user)
    profile_data = None
    if profile_obj is not None:
        attr_name = profile_obj.__class__.__name__.lower().replace("profile", "_profile")
        profile_data = ProfileResponse.model_validate({"user": user, attr_name: profile_obj})
    return MeResponse(
        user=user,
        profile=profile_data,
        role=user.role,
        redirect_url=PUBLIC_DASHBOARD_ROUTES.get(user.role, "/discover.html"),
    )