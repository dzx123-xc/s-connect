from datetime import datetime
from typing import Optional

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import SessionLocal
from app.models.session import Session
from app.models.user import User
from app.auth.password import hash_session_id, is_session_expired, is_session_revoked


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        request.state.session = None

        session_id = request.cookies.get("session_id")
        if not session_id:
            response = await call_next(request)
            return response

        session_id_hash = hash_session_id(session_id)

        db = SessionLocal()
        try:
            session = db.query(Session).filter(
                Session.session_id_hash == session_id_hash,
                Session.revoked_at.is_(None),
            ).first()

            if session and not is_session_expired(session.expires_at):
                session.last_accessed_at = datetime.utcnow()
                session.expires_at = datetime.utcnow() + timedelta(seconds=30 * 24 * 60 * 60)
                db.commit()

                user = db.query(User).filter(User.id == session.user_id, User.is_active.is_(True)).first()
                if user:
                    request.state.user = user
                    request.state.session = session

            response = await call_next(request)
            return response
        finally:
            db.close()


def get_current_user(request: Request) -> User:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


def get_current_user_optional(request: Request) -> Optional[User]:
    return getattr(request.state, "user", None)


from datetime import timedelta