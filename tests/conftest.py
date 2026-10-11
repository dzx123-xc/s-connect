import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager

from app.main import app
from app.database import get_db, Base
from app.config import settings


@pytest.fixture(scope="session", autouse=True)
def override_settings():
    settings.database_url = "sqlite:///:memory:"
    settings.debug = False


@asynccontextmanager
async def test_lifespan(app):
    from app.database import init_db
    init_db()
    yield


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine):
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = test_lifespan
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_service(test_db):
    from app.services.auth_service import (
        create_user_with_profile,
        create_session,
        verify_user_password,
        revoke_session,
        get_user_by_email,
    )
    from app.schemas.auth import RegisterRequest

    class AuthServiceWrapper:
        def __init__(self, db):
            self.db = db

        def register_user(self, email: str, password: str, role: str = "player", **kwargs):
            username = kwargs.get("username")
            if not username:
                username = email.split("@")[0]
                if not username:
                    username = "user"
            phone = kwargs.get("phone")
            if not phone:
                # Derive a unique phone from the email to avoid unique-constraint collisions
                seed = abs(hash(email)) % 10000000
                phone = f"+91{7000000000 + seed}"[:15]
            data = RegisterRequest(
                full_name=kwargs.get("full_name", "Test User"),
                username=username,
                phone=phone,
                email=email,
                password=password,
                role=role,
                availability=kwargs.get("availability"),
                state=kwargs.get("state"),
                district=kwargs.get("district"),
                city=kwargs.get("city"),
                village=kwargs.get("village"),
                sport_id=kwargs.get("sport_id"),
                position_id=kwargs.get("position_id"),
                location_id=kwargs.get("location_id"),
                bio=kwargs.get("bio"),
                skills=kwargs.get("skills", []),
                achievements=kwargs.get("achievements", []),
                certifications=kwargs.get("certifications", []),
                experience_years=kwargs.get("experience_years", 0),
                clubs_coached=kwargs.get("clubs_coached", []),
                name=kwargs.get("name"),
                sport_id_club=kwargs.get("sport_id_club"),
                description=kwargs.get("description"),
                founded_year=kwargs.get("founded_year"),
                organization_name=kwargs.get("organization_name"),
                sports_organized=kwargs.get("sports_organized", []),
                license_number=kwargs.get("license_number"),
                sport_id_referee=kwargs.get("sport_id_referee"),
                certification_level=kwargs.get("certification_level"),
            )
            return create_user_with_profile(self.db, data)

        def create_session(self, user_id: int):
            return create_session(self.db, user_id)

        def verify_password(self, email: str, password: str):
            return verify_user_password(self.db, email, password)

        def revoke_session(self, session_id: str):
            return revoke_session(self.db, session_id)

        def get_user_by_email(self, email: str):
            return get_user_by_email(self.db, email)

    return AuthServiceWrapper(test_db)


@pytest.fixture(scope="function")
def admin_client(test_db):
    """Client pre-authenticated as an admin user created via the secure dev mechanism."""
    from app.services.admin_service import create_admin_user

    admin_user = create_admin_user(
        test_db,
        email="admin@example.com",
        password="AdminPass1!",
        full_name="Admin User",
    )
    session_id = None
    from app.services.auth_service import create_session
    session_id = create_session(test_db, admin_user.id)

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = test_lifespan
    with TestClient(app, cookies={"session_id": session_id}) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def player_client(test_db):
    """Client pre-authenticated as a player."""
    from app.services.auth_service import create_user_with_profile
    from app.schemas.auth import RegisterRequest

    data = RegisterRequest(
        full_name="Test Player",
        username="testplayer",
        phone="+919876543210",
        email="player@example.com",
        password="PlayerPass1!",
        role="player",
    )
    user = create_user_with_profile(test_db, data)
    from app.services.auth_service import create_session
    session_id = create_session(test_db, user.id)

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = test_lifespan
    with TestClient(app, cookies={"session_id": session_id}) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def coach_client(test_db):
    """Client pre-authenticated as a coach."""
    from app.services.auth_service import create_user_with_profile
    from app.schemas.auth import RegisterRequest

    data = RegisterRequest(
        full_name="Test Coach",
        username="testcoach",
        phone="+919876543211",
        email="coach@example.com",
        password="CoachPass1!",
        role="coach",
    )
    user = create_user_with_profile(test_db, data)
    from app.services.auth_service import create_session
    session_id = create_session(test_db, user.id)

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = test_lifespan
    with TestClient(app, cookies={"session_id": session_id}) as test_client:
        yield test_client
    app.dependency_overrides.clear()