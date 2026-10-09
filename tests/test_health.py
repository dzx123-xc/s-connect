import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_check_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "sconnect"

    def test_health_check_response_structure(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)

    def test_health_db_check_returns_connected(self, client):
        response = client.get("/health/db")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"

    def test_health_db_check_response_structure(self, client):
        response = client.get("/health/db")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert isinstance(data["status"], str)
        assert isinstance(data["database"], str)


class TestHealthEndpointHeaders:
    def test_health_check_content_type_json(self, client):
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_db_check_content_type_json(self, client):
        response = client.get("/health/db")
        assert response.headers["content-type"] == "application/json"