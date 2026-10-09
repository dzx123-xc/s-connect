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
            data = RegisterRequest(
                email=email,
                password=password,
                role=role,
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