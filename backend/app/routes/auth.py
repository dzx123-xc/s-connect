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
)
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.auth.dependencies import require_role
from app.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, response: Response, db: DBSession = Depends(get_db)):
    existing = db.execute(select(User).where(User.email == data.email.lower())).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = create_user_with_profile(db, data)
    session_id = create_session(db, user.id)

    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        max_age=settings.session_max_age_seconds,
        path="/",
    )

    role_redirects = {
        "player": "/player-dashboard.html",
        "coach": "/coach-dashboard.html",
        "club": "/club-dashboard.html",
        "organizer": "/organizer-dashboard.html",
        "referee": "/referee-dashboard.html",
    }

    return AuthResponse(
        user=user,
        redirect_url=role_redirects.get(user.role, "/discover.html"),
    )


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, response: Response, db: DBSession = Depends(get_db)):
    user = verify_user_password(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    session_id = create_session(db, user.id)

    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=settings.session_cookie_httponly,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        max_age=settings.session_max_age_seconds,
        path="/",
    )

    role_redirects = {
        "player": "/player-dashboard.html",
        "coach": "/coach-dashboard.html",
        "club": "/club-dashboard.html",
        "organizer": "/organizer-dashboard.html",
        "referee": "/referee-dashboard.html",
        "admin": "/admin-portal.html",
    }

    return AuthResponse(
        user=user,
        redirect_url=role_redirects.get(user.role, "/discover.html"),
    )


@router.post("/logout")
def logout(request: Request, response: Response, db: DBSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if session_id:
        revoke_session(db, session_id)

    response.delete_cookie(key=settings.session_cookie_name, path="/", httponly=settings.session_cookie_httponly, secure=settings.session_cookie_secure, samesite=settings.session_cookie_samesite)
    return {"message": "Logged out"}


@router.get("/me")
def me(request: Request, user=Depends(require_role("player", "coach", "club", "organizer", "referee", "admin"))):
    return {"user": user}