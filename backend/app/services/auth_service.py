from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session as DBSession

from app.models.user import User, Player, Coach, Club, Organizer, Referee
from app.models.session import Session
from app.auth.password import (
    hash_password,
    verify_password,
    generate_session_id,
    hash_session_id,
    create_session_expiry,
)
from app.schemas.auth import RegisterRequest


def create_user_with_profile(db: DBSession, data: RegisterRequest) -> User:
    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(user)
    db.flush()

    if data.role == "player":
        profile = Player(
            user_id=user.id,
            sport_id=data.sport_id,
            position_id=data.position_id,
            location_id=data.location_id,
            bio=data.bio,
            skills=data.skills or [],
            achievements=data.achievements or [],
        )
    elif data.role == "coach":
        profile = Coach(
            user_id=user.id,
            sport_id=data.sport_id,
            certifications=data.certifications or [],
            experience_years=data.experience_years or 0,
            clubs_coached=data.clubs_coached or [],
        )
    elif data.role == "club":
        profile = Club(
            user_id=user.id,
            name=data.name,
            sport_id=data.sport_id_club,
            location_id=data.location_id,
            description=data.description,
            founded_year=data.founded_year,
        )
    elif data.role == "organizer":
        profile = Organizer(
            user_id=user.id,
            organization_name=data.organization_name,
            sports_organized=data.sports_organized or [],
            license_number=data.license_number,
        )
    elif data.role == "referee":
        profile = Referee(
            user_id=user.id,
            sport_id=data.sport_id_referee,
            certification_level=data.certification_level,
            matches_officiated=0,
        )
    else:
        raise ValueError(f"Unknown role: {data.role}")

    db.add(profile)
    db.flush()
    return user


def create_session(db: DBSession, user_id: int) -> str:
    session_id = generate_session_id()
    session_id_hash = hash_session_id(session_id)
    expires_at = create_session_expiry()

    session = Session(
        session_id_hash=session_id_hash,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(session)
    db.flush()
    return session_id


def get_session(db: DBSession, session_id: str) -> Optional[Session]:
    session_id_hash = hash_session_id(session_id)
    return db.query(Session).filter(
        Session.session_id_hash == session_id_hash,
        Session.revoked_at.is_(None),
    ).first()


def validate_session(db: DBSession, session_id: str) -> Optional[User]:
    session = get_session(db, session_id)
    if not session:
        return None
    if datetime.utcnow() > session.expires_at:
        return None

    session.last_accessed_at = datetime.utcnow()
    session.expires_at = datetime.utcnow() + timedelta(seconds=30 * 24 * 60 * 60)
    db.commit()

    user = db.query(User).filter(User.id == session.user_id, User.is_active.is_(True)).first()
    return user


def revoke_session(db: DBSession, session_id: str) -> bool:
    session = get_session(db, session_id)
    if not session:
        return False
    session.revoked_at = datetime.utcnow()
    db.commit()
    return True


def revoke_all_user_sessions(db: DBSession, user_id: int) -> int:
    count = db.query(Session).filter(
        Session.user_id == user_id,
        Session.revoked_at.is_(None),
    ).update({"revoked_at": datetime.utcnow()})
    db.commit()
    return count


def get_user_by_email(db: DBSession, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: DBSession, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def verify_user_password(db: DBSession, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(user.password_hash, password):
        return None
    return user


def get_user_with_profile(db: DBSession, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()