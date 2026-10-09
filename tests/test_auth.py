import pytest
from app.auth.password import (
    hash_password,
    verify_password,
    generate_session_id,
    hash_session_id,
    create_session_expiry,
    is_session_expired,
    is_session_revoked,
)
from app.models.session import Session
from app.models.user import User
from datetime import datetime, timedelta


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        password = "test_password_123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password

    def test_hash_password_different_each_time(self):
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        password = "test_password_123"
        hashed = hash_password(password)
        assert verify_password(hashed, password) is True

    def test_verify_password_incorrect(self):
        password = "test_password_123"
        hashed = hash_password(password)
        assert verify_password(hashed, "wrong_password") is False

    def test_verify_password_empty_string(self):
        hashed = hash_password("some_password")
        assert verify_password(hashed, "") is False

    def test_verify_password_invalid_hash(self):
        assert verify_password("invalid_hash", "password") is False

    def test_argon2id_algorithm_used(self):
        password = "test_password"
        hashed = hash_password(password)
        assert hashed.startswith("$argon2id$")


class TestSessionIdGeneration:
    def test_generate_session_id_returns_string(self):
        session_id = generate_session_id()
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_generate_session_id_unique(self):
        ids = {generate_session_id() for _ in range(100)}
        assert len(ids) == 100

    def test_hash_session_id_deterministic(self):
        session_id = "test_session_id_123"
        hash1 = hash_session_id(session_id)
        hash2 = hash_session_id(session_id)
        assert hash1 == hash2
        assert len(hash1) == 64

    def test_hash_session_id_different_inputs(self):
        hash1 = hash_session_id("session_1")
        hash2 = hash_session_id("session_2")
        assert hash1 != hash2


class TestSessionExpiry:
    def test_create_session_expiry_future(self):
        expiry = create_session_expiry()
        assert isinstance(expiry, datetime)
        assert expiry > datetime.utcnow()

    def test_is_session_expired_false_for_future(self):
        future = datetime.utcnow() + timedelta(hours=1)
        assert is_session_expired(future) is False

    def test_is_session_expired_true_for_past(self):
        past = datetime.utcnow() - timedelta(hours=1)
        assert is_session_expired(past) is True

    def test_is_session_expired_exact_now(self):
        now = datetime.utcnow()
        assert is_session_expired(now) is False


class TestSessionRevocation:
    def test_is_session_revoked_false_for_none(self):
        assert is_session_revoked(None) is False

    def test_is_session_revoked_true_for_datetime(self):
        assert is_session_revoked(datetime.utcnow()) is True


class TestAuthServiceIntegration:
    def test_user_registration_creates_password_hash(self, auth_service, test_db):
        user = auth_service.register_user(
            email="test@example.com",
            password="secure_password_123",
            role="player",
        )
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.password_hash != "secure_password_123"
        assert user.password_hash.startswith("$argon2id$")
        assert user.is_active is True
        assert user.role == "player"

    def test_user_registration_duplicate_email_fails(self, auth_service, test_db):
        auth_service.register_user(
            email="duplicate@example.com",
            password="password123",
            role="player",
        )
        with pytest.raises(Exception):
            auth_service.register_user(
                email="duplicate@example.com",
                password="password456",
                role="coach",
            )

    def test_password_verification_through_service(self, auth_service, test_db):
        auth_service.register_user(
            email="verify@example.com",
            password="correct_password",
            role="player",
        )
        user = auth_service.verify_password("verify@example.com", "correct_password")
        assert user is not None
        assert user.email == "verify@example.com"

        user = auth_service.verify_password("verify@example.com", "wrong_password")
        assert user is None

    def test_session_creation_returns_session_id(self, auth_service, test_db):
        user = auth_service.register_user(
            email="session@example.com",
            password="password123",
            role="player",
        )
        session_id = auth_service.create_session(user.id)
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_session_lookup_by_id(self, auth_service, test_db):
        user = auth_service.register_user(
            email="lookup@example.com",
            password="password123",
            role="player",
        )
        session_id = auth_service.create_session(user.id)
        from app.auth.password import hash_session_id
        from app.services.auth_service import get_session
        session = get_session(test_db, session_id)
        assert session is not None
        assert session.user_id == user.id
        assert session.session_id_hash == hash_session_id(session_id)
        assert session.revoked_at is None

    def test_session_revocation(self, auth_service, test_db):
        user = auth_service.register_user(
            email="revoke@example.com",
            password="password123",
            role="player",
        )
        session_id = auth_service.create_session(user.id)
        result = auth_service.revoke_session(session_id)
        assert result is True

        from app.auth.password import hash_session_id
        from app.services.auth_service import get_session
        session = get_session(test_db, session_id)
        assert session is None

    def test_revoke_nonexistent_session_returns_false(self, auth_service, test_db):
        result = auth_service.revoke_session("nonexistent_session_id")
        assert result is False

    def test_multiple_sessions_per_user(self, auth_service, test_db):
        user = auth_service.register_user(
            email="multi@example.com",
            password="password123",
            role="player",
        )
        session1 = auth_service.create_session(user.id)
        session2 = auth_service.create_session(user.id)
        assert session1 != session2

        from app.auth.password import hash_session_id
        from app.services.auth_service import get_session
        s1 = get_session(test_db, session1)
        s2 = get_session(test_db, session2)
        assert s1 is not None
        assert s2 is not None
        assert s1.session_id_hash != s2.session_id_hash

    def test_revoke_all_user_sessions(self, auth_service, test_db):
        user = auth_service.register_user(
            email="revokeall@example.com",
            password="password123",
            role="player",
        )
        session1 = auth_service.create_session(user.id)
        session2 = auth_service.create_session(user.id)

        from app.services.auth_service import revoke_all_user_sessions
        count = revoke_all_user_sessions(test_db, user.id)
        assert count == 2

        from app.auth.password import hash_session_id
        from app.services.auth_service import get_session
        assert get_session(test_db, session1) is None
        assert get_session(test_db, session2) is None